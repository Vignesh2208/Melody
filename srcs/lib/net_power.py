"""Melody main orchestrator logic

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>, Rakesh Kumar (gopchandani@gmail.com)
"""


import datetime
import json
import kronos_functions
import subprocess
import sys
import os
import tempfile
import threading
import logging

import srcs.lib.defines as defines

from srcs.cyber_network.traffic_flow import ReplayFlowsContainer
from srcs.lib.replay_orchestrator import ReplayOrchestrator
from srcs.utils.util_functions import *
from srcs.proto import configuration_pb2
from sys import stdout
from google.protobuf import text_format
from contextlib import contextmanager
from datetime import datetime
from srcs.lib.shared_buffer import *


@contextmanager
def stderr_redirected():
    """Lifted from: https://stackoverflow.com/questions/4675728/redirect-stdout-to-a-file-in-python

    This is the only way I've found to redirect stdout with curses. This way the
    output from questionnaire can be piped to another program, without piping
    what's written to the terminal by the prompters.
    """
    stderr = sys.stderr
    to = os.devnull

    to_file =  open(to, 'wb')
    stderr_fd = stderr.fileno()
    with os.fdopen(os.dup(stderr_fd), 'wb') as copied:
        try:
            os.dup2(to_file.fileno(), stderr_fd)  
        except ValueError:  # filename
            os.dup2(to_file.fileno(), stderr_fd) 
        try:
            yield stderr
        finally:
            os.dup2(copied.fileno(), stderr_fd) 
            to_file.close()


class NetPower(object):
    """Class which starts mininet, proxy, disturbance generator and manages their operation.
    
    It initializes the project and brings it under the control of Kronos. It provides API to drive the co-simulation
    of mininet and a power simulator.
    
    """

    def __init__(self,
                 run_time,
                 network_configuration,
                 project_dir,
                 base_dir,
                 log_dir,
                 emulated_background_traffic_flows,
                 replay_traffic_flows,
                 cyber_host_apps,
                 enable_kronos,
                 rel_cpu_speed,
                 power_sim_spec):
        """Initializing Melody

        :param run_time: Total running time of co-simulation in seconds
        :type run_time: int
        :param network_configuration: Mininet Network configuration obj
        :type network_configuration: (srcs/cyber_network/network_configuration)
        :param project_dir: Directory path of project
        :type project_dir: str
        :param base_dir: Melody Installation directory
        :type base_dir: str
        :param log_dir: Directory to store log files and pcaps
        :type log_dir: str
        :param emulated_background_traffic_flows: A list of EmulatedTrafficFlow objects
        :type emulated_background_traffic_flows: a list of srcs/cyber_network/traffic_flow : EmulatedTrafficFlow objects
        :param replay_traffic_flows: A list of ReplayTraficFlow objects
        :type replay_traffic_flows: a list of srcs/cyber_network/traffic_flow : ReplayTrafficFlow objects
        :param cyber_host_apps: A dictionary mapping an application_id to its corresponding source file
        :type cyber_host_apps: dict
        :param enable_kronos: Enable/Disable Kronos. 1 - enable kronos, 0 - disable kronos
        :type enable_kronos: int
        :param rel_cpu_speed: Relative cpu speed for virtual time advancement
        :type rel_cpu_speed: int
        :param power_sim_spec: A dictionary containing powersim driver name and case file path
        :type power_sim_spec: dict
        """

        
        self.network_configuration = network_configuration
        self.switch_2_switch_latency = self.network_configuration.topo_params[
            "switch_switch_link_latency_range"][0]
        self.host_2_switch_latency = self.network_configuration.topo_params[
            "host_switch_link_latency_range"][0]

        # Dictionary containing mappings, keyed by the id of the mininet host
        # Value is a tuple -- (IP Address, Role)
        self.project_name = self.network_configuration.project_name
        self.run_time = run_time
        self.host_to_application_ids = {}
        self.powersim_id_to_host = {}
        self.project_dir = project_dir
        self.base_dir = base_dir
        self.enable_kronos = enable_kronos
        self.rel_cpu_speed = rel_cpu_speed
        self.cpus_subset = "1-12"
        self.power_sim_spec = power_sim_spec

        self.pid_list = []
        self.host_pids = {}
        self.switch_pids = {}
        self.emulation_driver_pids = []
        self.replay_driver_pids = []
        self.timeslice = 100000
        self.cyber_host_apps = cyber_host_apps

        self.emulated_background_traffic_flows = emulated_background_traffic_flows
        self.replay_traffic_flows = replay_traffic_flows
        self.emulation_driver_params = []
        self.proxy_server = None

        self.get_emulation_driver_params()

        self.node_mappings_file_path = "/tmp/node_mappings.json"
        self.log_dir = log_dir
        self.flag_debug = True  # flag for debug printing
        self.nxt_tracer_id = 1

        # Clean up logs from previous run(s)
        os.system("rm -rf " + self.log_dir + "/*")
        os.system("sudo rm /tmp/*_log.txt")
        os.system("sudo rm /tmp/*replay.json")
        os.system("sudo rm /tmp/*emulation*.json")

        self.shared_buf_array = shared_buffer_array()
        self.tcpdump_procs = []
        self.n_actual_tcpdump_procs = 0
        self.n_dilated_tcpdump_procs = 0
        self.started = False

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        for i in range(0, len(self.network_configuration.roles)):
                mininet_host_name = self.network_configuration.roles[i][0]

                self.host_to_application_ids[mininet_host_name] = []
                port_mapping = self.network_configuration.roles[i][1]
                for mapping in port_mapping:
                    entity_id = mapping[0]
                    self.host_to_application_ids[mininet_host_name].append(
                        entity_id)

                if len(self.host_to_application_ids[mininet_host_name]) == 0 :
                    self.host_to_application_ids[mininet_host_name].append(
                        f"DUMMY_{mininet_host_name}")
        self.attributes_dict = {}
        self.open_main_cmd_channel_buffers()
        
        
        self.replay_flows_container = ReplayFlowsContainer()
        for flow in self.replay_traffic_flows:
            self.replay_flows_container.add_replay_flow(flow)
        self.nodes_involved_in_replay = \
            self.replay_flows_container.get_all_involved_nodes()
        self.replay_orchestrator = None
        self.prev_queued_disturbance_threads = []
        self.nxt_queued_disturbance_threads = []
        self.total_elapsed_virtual_time = 0.0


    def get_number_of_tracers(self):
        num_tracers = 0

        # All host processes
        for mininet_host in self.network_configuration.mininet_obj.hosts:
            num_tracers += len(self.host_to_application_ids[mininet_host.name])

        # All switch processes
        num_tracers += len(self.network_configuration.mininet_obj.switches)

        # All emulation drivers
        num_tracers += len(self.emulation_driver_params)

        # All replay drivers
        num_tracers += len(self.nodes_involved_in_replay)

        # Disturbance generator
        num_tracers += 1
        return num_tracers
        

    def get_application_id_attributes(self, application_id,
        project_config_file):

        if not os.path.isfile(project_config_file):
            logging.info("Project config file is incorrect !")
            return {}
        project_config = configuration_pb2.ProjectConfiguration()
        with open(project_config_file, 'r') as f:
            text_format.Parse(f.read(), project_config)

        attr = {}

        for mapping in project_config.cyber_physical_map:
            for mapped_app in mapping.mapped_application:
                if mapped_app.application_id == application_id:
                    for attribute in mapped_app.attribute:
                        attr[attribute.name] = attribute.value
                    break
        return attr

    def get_emulation_driver_params(self):
        """Construct list of emulated traffic flow objects

        :return: None
        """
        for bg_flow in self.emulated_background_traffic_flows:
            self.emulation_driver_params.append(
                bg_flow.get_emulated_driver_attributes(for_client=True))
            attr = bg_flow.get_emulated_driver_attributes(for_client=False)
            if attr is not None:
                self.emulation_driver_params.append(attr)

    def check_kronos_loaded(self):
        """Check if kronos is loaded

        :return: Fails if Kronos is enabled but not loaded
        """
        if self.enable_kronos == 1 and not os.path.isfile('/proc/kronos'):
            logging.error(
                "Kronos is not loaded. Please load it and try again!")
            sys.exit(defines.EXIT_FAILURE)

    def initialize_kronos_exp(self):
        """Initialize Kronos exp

        :return: None
        """
        self.check_kronos_loaded()
        num_tracers = self.get_number_of_tracers()
        logging.info(f"Initializing Kronos experiment with {num_tracers} nodes")
        ret = kronos_functions.initializeExp(num_tracers)
        if ret < 0:
            logging.error("Kronos initialization failed. Exiting ...")
            sys.exit(defines.EXIT_FAILURE)

    def start_synchronized_experiment(self):
        """Start a synchronized kronos experiment if kronos is enabled

        :return: None
        """

        if self.enable_kronos == 1:
            logging.info(
                "Kronos >> Synchronizing and freezing all processes ...")
            while kronos_functions.synchronizeAndFreeze() <= 0:
                logging.info(
                    "Kronos >> Synchronize and Freeze failed. Retrying in 1 sec")
                time.sleep(1)
            logging.info(
                "Kronos >> Synchronize and Freeze succeeded !")
            logging.info(
                "Kronos >> Experiment started with REL_CPU_SPEED: %s",
                self.rel_cpu_speed)
        else:
            self.start_time = time.time()
            logging.info(
                "Melody >> Experiment started with Kronos disabled ... ")

    def stop_synchronized_experiment(self):
        """Stop a synchronized kronos experiment if kronos is disabled

        :return: None
        """

        logging.info(
            "########################################################################")
        if self.enable_kronos == 1:
            kronos_functions.stopExp()
            logging.info("Kronos >> Stopping synchronized experiment ...")
            self.trigger_all_processes(defines.EXIT_CMD)
            self.replay_orchestrator.send_command(defines.EXIT_CMD)
            logging.info("Kronos >> Stopped synchronized experiment")
        else:
            logging.info(
                "Melody >> Stopping emulation ... ")
        logging.info(
            "########################################################################")

    def generate_node_mappings(self, roles):
        """Generate a dictionary which maps application_id to a hostname, ip and port. Stores this in /tmp

        :param roles: list of tuples (host_name, [application_id, listen_port])
        :return: None
        """
        with open(self.node_mappings_file_path, "w") as outfile:
            for i in range(0, len(roles)):
                mininet_host_name = roles[i][0]
                port_mapping = roles[i][1]
                for mapping in port_mapping:
                    entity_id = mapping[0]
                    entity_port = mapping[1]
                    self.powersim_id_to_host[entity_id] = {}
                    self.powersim_id_to_host[entity_id]["port"] = entity_port
                    self.powersim_id_to_host[entity_id][
                        "mapped_host"] = mininet_host_name
                    self.powersim_id_to_host[entity_id][
                        "mapped_host_ip"] = f"10.0.0.{mininet_host_name[1:]}"
                if len(port_mapping) == 0:
                    entity_id = "DUMMY_" + str(mininet_host_name)
                    entity_port = 5100
                    self.powersim_id_to_host[entity_id] = {}
                    self.powersim_id_to_host[entity_id]["port"] = entity_port
                    self.powersim_id_to_host[entity_id][
                        "mapped_host"] = mininet_host_name
                    self.powersim_id_to_host[entity_id][
                        "mapped_host_ip"] = f"10.0.0.{mininet_host_name[1:]}"

            json.dump(self.powersim_id_to_host, outfile)
        with open("/tmp/application_params.json", "w") as outfile:
            json.dump(self.attributes_dict, outfile)

    def cmd_to_start_process_under_tracer(self, cmd_to_run):
        """Gets a command string which can be started under kronos

        :param cmd_to_run: Command to run under kronos control
        :type cmd_to_run: str
        :return: str command to run
        """

        tracer_path = "/usr/bin/tracer"
        tracer_args = [tracer_path]
        tracer_args.extend(["-i", str(self.nxt_tracer_id)])
        tracer_args.extend(["-r", str(self.rel_cpu_speed)])
        tracer_args.extend(["-c", "\"" + cmd_to_run + "\""])
        tracer_args.append("-s")

        self.nxt_tracer_id += 1
        return ' '.join(tracer_args)

    def start_host_processes(self):
        """Starts all co-simulation host processes

        This starts all specified applications inside mininet hosts.

        :return: None
        """
        logging.info("Melody >> Starting all hosts ... ")

        for mininet_host in self.network_configuration.mininet_obj.hosts:
            for mapped_application_id in self.host_to_application_ids[mininet_host.name]:
                host_id = int(mininet_host.name[1:])
                host_log_file = f"{self.log_dir}/{mapped_application_id}_log.txt"
                host_py_script = f"{self.base_dir}/srcs/lib/host.py"
                cmd_to_run = f"python {host_py_script} -l {host_log_file} " \
                             f"-c {self.node_mappings_file_path} " \
                             f"-r {self.run_time} -n {self.project_name} " \
                             f"-d {host_id} -m {mapped_application_id}" 

                if mapped_application_id in self.cyber_host_apps:
                    cmd_to_run = f"{cmd_to_run} -a {self.cyber_host_apps[mapped_application_id]}"
                else:
                    cmd_to_run = f"{cmd_to_run} -a NONE"

                if self.enable_kronos == 1:
                    cmd_to_run = self.cmd_to_start_process_under_tracer(cmd_to_run)
                cmd_to_run = f"{cmd_to_run} >  {host_log_file} 2>&1 & echo $! "

                with tempfile.NamedTemporaryFile() as f:
                    mininet_host.cmd(f"{cmd_to_run} >> {f.name}")
                    pid = int(f.read())
                    self.host_pids[mininet_host.name] = pid
                    self.pid_list.append(pid)

    def start_switch_processes(self):
        """Starts all mininet switch processes

        :return: None
        """
        logging.info("Melody >> Starting all switches ...")
        for mininet_switch in self.network_configuration.mininet_obj.switches:
            sw_id = int(mininet_switch.name[1:])
            cmd_to_run = f"python {self.base_dir}/srcs/utils/dummy_nop_process.py"
            sw_log_file = f"/tmp/sw_{sw_id}_log.txt"
            if self.enable_kronos == 1:
                cmd_to_run = self.cmd_to_start_process_under_tracer(cmd_to_run)
            cmd_to_run = f"{cmd_to_run} > {sw_log_file} 2>&1 & echo $! "
            with tempfile.NamedTemporaryFile() as f:
                mininet_switch.cmd(f"{cmd_to_run} >> {f.name}")
                pid = int(f.read())
                self.switch_pids[mininet_switch.name] = pid

    def start_emulation_drivers(self):
        """Starts all emulation drivers

        Emulation drivers would control background traffic generation.

        :return: None
        """

        driver_py_script = f"{self.base_dir}/srcs/lib/emulation_driver.py"
        for edp in self.emulation_driver_params:

            mininet_host = self.network_configuration.mininet_obj.get(
                edp["node_id"])
            driver_log_file = "/tmp/%s_log.txt" %(str(edp["driver_id"]))
            input_params_file_path = "/tmp/%s.json" %(edp["driver_id"])
            with open(input_params_file_path, "w") as f:
                json.dump(edp, f)

            cmd_to_run = f"python {driver_py_script} --input_params_file_path={input_params_file_path}"
            if self.enable_kronos == 1:
                cmd_to_run = self.cmd_to_start_process_under_tracer(cmd_to_run)
            cmd_to_run = f"{cmd_to_run} > {driver_log_file} 2>&1 & echo $! "

            with tempfile.NamedTemporaryFile() as f:
                mininet_host.cmd(f"{cmd_to_run} >> {f.name}")
                pid = int(f.read())
                self.emulation_driver_pids.append(pid)
                self.pid_list.append(pid)
        logging.info("Melody >> All background flow drivers started ...")

    def start_replay_drivers(self):
        """Starts all replay drivers

        Replay drivers would control replaying all pcaps.

        :return: None
        """

        driver_py_script = f"{self.base_dir}/srcs/lib/replay_driver.py"
        for node in self.nodes_involved_in_replay:
            mininet_host = self.network_configuration.mininet_obj.get(node)
            rdp = {
                "driver_id": f"{mininet_host.name}-replay",
                "run_time": self.run_time,
                "node_id": mininet_host.name,
                "node_ip": mininet_host.IP(),
                "replay_plan_file_path": "/tmp/replay_plan.json"
                }

            driver_log_file = "/tmp/%s_log.txt" % (str(rdp["driver_id"]))
            input_params_file_path = "/tmp/%s.json" % (str(rdp["driver_id"]))
            with open(input_params_file_path, "w") as f:
                json.dump(rdp, f)

            cmd_to_run = f"python {driver_py_script} --input_params_file_path={input_params_file_path}"
            if self.enable_kronos == 1:
                cmd_to_run = self.cmd_to_start_process_under_tracer(cmd_to_run)
            cmd_to_run = f"{cmd_to_run} > {driver_log_file} 2>&1 & echo $! "

            with tempfile.NamedTemporaryFile() as f:
                mininet_host.cmd(f"{cmd_to_run} >> {f.name}")
                pid = int(f.read())
                self.replay_driver_pids.append(pid)
                self.pid_list.append(pid)

        logging.info("Melody >> All replay flow drivers started ... ")

    def start_host_capture(self, host_obj):
        """Start packet capture in each host

        :param host_obj: mininet_host object
        :return: None
        """
        core_cmd = "tcpdump"
        capture_cmd = f"sudo {core_cmd}"
        capture_log_file = f"{self.log_dir}/{host_obj.name}.pcap"
        with open(capture_log_file, "w") as f:
            pass

        capture_cmd = f"{capture_cmd} -i {host_obj.name}-eth0"
        capture_cmd = f"{capture_cmd} -w {capture_log_file} -U -B 20000 ip & > /dev/null 2>&1"
        self.n_actual_tcpdump_procs = self.n_actual_tcpdump_procs + 1
        host_obj.cmd(capture_cmd)

    def start_all_host_captures(self):
        """Start packet captures in all hosts

        :return: None
        """
        logging.info("Melody >> Starting tcpdump capture on hosts ...")
        for host in self.network_configuration.mininet_obj.hosts:
            self.start_host_capture(host)

    def start_pkt_captures(self):
        """Start packet captures in all host and switch interfaces

        :return: None
        """
        self.start_all_host_captures()
        logging.info("Melody >> Starting tcpdump capture on switches ...")
        for mininet_link in self.network_configuration.mininet_obj.links:
            switchIntfs = mininet_link.intf1
            core_cmd = "tcpdump"
            capture_cmd = f"sudo {core_cmd}"

            # 1. to capture all pcaps:
            if mininet_link.intf1.name.startswith("s") and mininet_link.intf2.name.startswith("s"):
                capture_log_file = \
                    f"{self.log_dir}/{mininet_link.intf1.name}-{mininet_link.intf2.name}.pcap"
                with open(capture_log_file, "w") as f:
                    pass

                capture_cmd = f"{capture_cmd} -i {switchIntfs.name}"
                capture_cmd = f"{capture_cmd} -w {capture_log_file} -B 40000 ip > /dev/null 2>&1 &"
                self.n_actual_tcpdump_procs = self.n_actual_tcpdump_procs + 1

                proc = subprocess.Popen(capture_cmd, shell=True)
                self.tcpdump_procs.append(proc)
                
        # Get all the pids of sudo tcpdump parents
        sudo_tcpdump_parent_pids = get_pids_with_cmd(
            cmd=f"sudo {core_cmd}",
            expected_no_of_pids=self.n_actual_tcpdump_procs)

        self.tcpdump_pids = sudo_tcpdump_parent_pids

    def set_netdevice_owners(self):
        """Associates interfaces with Kronos so that packets are delayed in virtual time.

        :return: None
        """
        logging.info(
            "Kronos >> Assuming control over mininet network interfaces ...")
        for mininet_switch in self.network_configuration.mininet_obj.switches:
            assert mininet_switch.name in self.switch_pids
            for name in mininet_switch.intfNames():
                if name != "lo":
                    kronos_functions.setNetDeviceOwner(0, name)

        for host_name in self.host_pids:
            mininet_host = self.network_configuration.mininet_obj.get(host_name)
            assert mininet_host.name in self.host_pids
            for name in mininet_host.intfNames():
                if name != "lo" and name != "eth0" :
                    kronos_functions.setNetDeviceOwner(0, name)

    def start_proxy_process(self):
        """Starts the proxy process

        :return: None
        """
        logging.info("Melody >> Starting proxy ... ")
        proxy_script = f"{self.base_dir}/srcs/lib/pss_server.py"
        driver_name = self.power_sim_spec["driver_name"]
        powersim_case_file_path = self.power_sim_spec["case_file_path"]
        cmd_to_run = f"python {proxy_script} --driver_name={driver_name} " \
                     f"--listen_ip=11.0.0.255 --case_file_path={powersim_case_file_path} "
        cmd_to_run = f"{cmd_to_run} > /tmp/proxy_log.txt 2>&1 & echo $! "

        if not os.path.isfile(powersim_case_file_path):
            logging.info(
                "Melody >> WARNING: Please check your configuration. "
                "Case file path: %s is incorrect!" %powersim_case_file_path)
        self.proxy_pid = -1
        with tempfile.NamedTemporaryFile() as f:
            os.system(cmd_to_run + '>> ' + f.name)
            pid = int(f.read())
            self.proxy_pid = pid
            logging.info(
                f"Melody >> Proxy PID: {self.proxy_pid} "
                f"Waiting 5 sec for GRPC server to get setup ...")
            time.sleep(5.0)

    def start_control_network(self):
        """Starts a separate control network which allows all mininet hosts to communicate outside the mininet network

        The control network allows each host to send GRPC requests to the proxy.

        :return: None
        """
        logging.info("Melody >> Starting grpc control network ...")
        for host in self.network_configuration.mininet_obj.hosts:
            host_number = host.name[1:]
            host.cmd(f"ip link add eth0 type veth peer name {host.name}base netns 1")
            host.cmd("ifconfig eth0 up")
            host.cmd(f"ifconfig eth0 11.0.0.{host_number}")
        os.system("sudo ip link add base type veth peer name hostbase netns 1")
        os.system("sudo ifconfig base 11.0.0.255 up")
        os.system("sudo ifconfig hostbase up")
        os.system("sudo brctl addbr connect")
        for host in self.network_configuration.mininet_obj.hosts:
            os.system(f"sudo ifconfig {host.name}base up")
            os.system(f"sudo brctl addif connect {host.name}base")
        os.system("sudo brctl addif connect hostbase")
        os.system("sudo ifconfig connect up")

    def start_disturbance_generator(self):
        """Starts the disturbance generator process and brings it under the control of Kronos

        The disturbance generator will send disturbances to the power simulator.

        :return: None
        """
        if os.path.isfile(f"{self.project_dir}/disturbances.prototxt"):
            disturbance_gen_script = f"{self.base_dir}/srcs/lib/disturbance_gen.py"
            disturbance_file = f"{self.project_dir}/disturbances.prototxt"
            disturbance_gen_log_file = "/tmp/disturbance_gen_log.txt"

            cmd_to_run = f"python {disturbance_gen_script} " \
                         f"--path_to_disturbance_file={disturbance_file}"
            if self.enable_kronos == 1:
                cmd_to_run = self.cmd_to_start_process_under_tracer(cmd_to_run)
            cmd_to_run = f"{cmd_to_run} > {disturbance_gen_log_file} 2>&1 & echo $! "

            with tempfile.NamedTemporaryFile() as f:
                os.system(f"{cmd_to_run} >> {f.name}")
                pid = int(f.read())
                logging.info(f"Melody >> Disturbance Generator PID: {pid}")
                self.pid_list.append(pid)

    def stop_control_network(self):
        """Stops the control network which enables GRPC connectivity

        :return: None
        """
        logging.info("Melody >> Stopping grpc control network ...")
        os.system(f"sudo kill -9 {self.proxy_pid}")
        os.system("sudo fuser -k 50051/tcp")
        time.sleep(5.0)
        os.system("sudo ifconfig connect down")
        for host in self.network_configuration.mininet_obj.hosts:
            host.cmd("ifconfig eth0 down")
            host.cmd("ip link del eth0")
        os.system("sudo ifconfig base down")
        os.system("sudo ip link del base")
        os.system("sudo ifconfig connect down")
        os.system("sudo brctl delbr connect")

    def sync_with_power_simulator(self):
        """Sends an RPC process request to the proxy.

        This triggers batch processing which processes all read/write rpc requests sent in the previous batch.

        :return: None
        """

        t = threading.Thread(target=defines.rpc_process)
        t.start()
        t.join()

    def start_replay_orchestrator(self):
        """Starts the replay orchestrator process

        The replay orchestrator process will drive replaying pcaps.

        :return: None
        """
        logging.info("Melody >> Starting replay orchestrator ... ")
        self.replay_flows_container.create_replay_plan()
        replay_plan_file = "/tmp/replay_plan.json"
        self.replay_orchestrator = ReplayOrchestrator(self, replay_plan_file)
        self.replay_orchestrator.start()

    def send_cmd_to_node(self, node_name, cmd):
        """Sends a command to execute on a mininet host

        :param node_name: mininet host name
        :type node_name: str
        :param cmd: command string to execute
        :type cmd: str
        :return: None
        """
        mininet_host = self.network_configuration.mininet_obj.get(node_name)
        if mininet_host is not None:
            mininet_host.cmd(cmd)

    def allow_icmp_requests(self):
        """Enables ICMP requests on all hosts

        :return: None
        """
        for host in self.network_configuration.mininet_obj.hosts:
            self.send_cmd_to_node(host.name,
                "sudo iptables -I OUTPUT -p icmp -j ACCEPT &")

    def allow_icmp_responses(self):
        """Allows ICMP responses on all hosts

        :return: None
        """
        for host in self.network_configuration.mininet_obj.hosts:
            self.send_cmd_to_node(host.name,
                "sudo iptables -I INPUT -p icmp -j ACCEPT &")

    def disable_TCP_RST(self):
        """Disables TCP_RST on all hosts

        :return: None
        """
        for host in self.network_configuration.mininet_obj.hosts:
            self.send_cmd_to_node(host.name,
                "sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j DROP &")

    def enable_TCP_RST(self):
        """Enables TCP_RST on all hosts

        :return: None
        """
        for host in self.network_configuration.mininet_obj.hosts:
            self.send_cmd_to_node(host.name,
                "sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j ACCEPT &")

    def open_main_cmd_channel_buffers(self):
        """Open shared buffer channels to all hosts

        Shared buffer channels are used to control co-simulation hosts, replay drivers and emulation drivers.

        :return: None or exits on Failure to open shared buffer channels
        """
        logging.info(
            "Melody >> Opening main inter-process communication channels ...")

        for mininet_host in self.network_configuration.mininet_obj.hosts:
            if mininet_host.name in self.host_to_application_ids:
                for mapped_application_id in self.host_to_application_ids[
                    mininet_host.name]:
                    result = self.shared_buf_array.open(
                        f"{mapped_application_id}-main-cmd-channel-buffer",
                        isProxy=True)
                    if (result == defines.BUF_NOT_INITIALIZED or
                        result == defines.FAILURE):
                        logging.error(
                            f"Shared Buffer open failed! "
                            f"Buffer not initialized for host: {mininet_host.name}")
                        sys.exit(defines.EXIT_FAILURE)

                    self.attributes_dict[mapped_application_id] = \
                        self.get_application_id_attributes(
                            mapped_application_id,
                            f"{self.project_dir}/project_configuration.prototxt")

            result = self.shared_buf_array.open(
                bufName=f"{mininet_host.name}-replay-main-cmd-channel-buffer",
                isProxy=True)
            if result == defines.BUF_NOT_INITIALIZED or result == defines.FAILURE:
                logging.error(
                    "Shared Buffer open open failed! "
                    f"Buffer not initialized for replay driver: {mininet_host.name}")
                sys.exit(defines.EXIT_FAILURE)

        for edp in self.emulation_driver_params:
            curr_edp_driver_id = edp["driver_id"]
            result = self.shared_buf_array.open(
                bufName=f"{curr_edp_driver_id}-main-cmd-channel-buffer", isProxy=True)
            if result == defines.BUF_NOT_INITIALIZED or result == defines.FAILURE:
                logging.error(
                    "Shared Buffer open failed! Buffer not initialized "
                    f"for driver: {curr_edp_driver_id}")
                sys.exit(defines.EXIT_FAILURE)

        result = self.shared_buf_array.open(
            bufName="disturbance-gen-cmd-channel-buffer", isProxy=True)
        if result == defines.BUF_NOT_INITIALIZED or result == defines.FAILURE:
            logging.error(
                "Shared Buffer open open failed! Buffer not initialized for "
                "disturbance generator ")
            sys.exit(defines.EXIT_FAILURE)

        logging.info(
            "Melody >> Opened main inter-process communication channels ... ")

    def trigger_all_processes(self, trigger_cmd):
        """Sends a message over shared buffer channels to all co-simulated hosts, replay and emulation drivers

        :param trigger_cmd: command to send
        :type trigger_cmd: str
        :return: None
        """
        for mininet_host in self.network_configuration.mininet_obj.hosts:
            if mininet_host.name in self.host_to_application_ids:
                for mapped_application_id in self.host_to_application_ids[mininet_host.name]:
                    self.shared_buf_array.write(
                        f"{mapped_application_id}-main-cmd-channel-buffer",
                        trigger_cmd, 0)

        for edp in self.emulation_driver_params:
            curr_edp_driver_id = edp["driver_id"]
            self.shared_buf_array.write(
                f"{curr_edp_driver_id}-main-cmd-channel-buffer",
                trigger_cmd, 0)

        self.shared_buf_array.write("disturbance-gen-cmd-channel-buffer", trigger_cmd, 0)

        logging.info(
            f"Melody >> Triggered hosts and drivers with command: {trigger_cmd}")

    def trigger_nxt_replay(self):
        """Sends a command to replay orchestrater

        This queues a replay command on the replay orchestrator. The replay orchestrator will initate the next
        replay as soon as possible.

        :return: None
        """
        logging.info("Melody >> Triggering next replay ...")
        self.replay_orchestrator.send_command(defines.TRIGGER_CMD)

    def trigger_nxt_k_replays(self, k):
        for _ in range(0, k):
            self.replay_orchestrator.send_command(defines.TRIGGER_CMD)

    def wait_for_loaded_pcap_msg(self):
        """Waits for required pcaps to be loaded by all replay-drivers

        :return: None
        """
        logging.info("########################################################################")
        logging.info(
            "\nMelody >> Waiting for pcaps to be loaded by all replay drivers ... ")
        n_warmup_rounds = 0
        outstanding_hosts = self.nodes_involved_in_replay
        while True:
            if len(outstanding_hosts) == 0:
                break

            for host in outstanding_hosts:
                dummy_id, msg = self.shared_buf_array.read(
                    f"{str(host)}-replay-main-cmd-channel-buffer")
                if msg == defines.LOADED_CMD:
                    logging.info(
                        "\nMelody >> Got a PCAP-Loaded message from "
                        f"replay driver for node: {host}")
                    outstanding_hosts.remove(host)
                    
            if self.enable_kronos == 1:
                kronos_functions.progressBy(self.timeslice, 1)
                n_warmup_rounds += 1

                if n_warmup_rounds % 100 == 0:
                    stdout.write(
                        "\rNumber of rounds ran until all replay pcaps were loaded: %d"
                        % n_warmup_rounds)
                    stdout.flush()
            else:
                time.sleep(0.1)
        if self.enable_kronos == 1 :
            logging.info(
                f"\nMelody >> All pcaps loaded in "
                f"{float(n_warmup_rounds*self.timeslice)/float(defines.SEC)} "
                "seconds (virtual time)")
        logging.info("\nMelody >> All replay drivers ready to proceed ...\n")
        

    def print_topo_info(self):
        """Prints topology information

        """

        logging.info("########################################################################")
        logging.info("")
        logging.info("                        Topology Information")
        logging.info("")
        logging.info("########################################################################")
        logging.info("")
        logging.info("Links in the network topology:")
        for link in self.network_configuration.ng.get_switch_link_data():
            logging.info(link)

        logging.info("All the hosts in the topology:")
        for sw in self.network_configuration.ng.get_switches():
            logging.info(f"Hosts at switch: {sw.node_id}")
            for h in sw.attached_hosts:
                logging.info(
                    f"Name: {h.node_id} IP: {h.ip_addr} Port: {h.switch_port}")
        logging.info("")
        logging.info("########################################################################")

    def cleanup(self):
        """Cleanup the emulation

        :return: None
        """
        print("Stopping project ...")
        if self.enable_kronos == 1:
            self.stop_synchronized_experiment()
            time.sleep(5)
        else:
            print("\nMelody >> Stopping Experiment ...")
            self.trigger_all_processes(defines.EXIT_CMD)
            print("\nMelody >> Sent EXIT command to all drivers ...")
            self.replay_orchestrator.send_command(defines.EXIT_CMD)
            print("\nMelody >> Sent EXIT command to replay orchestrator ...")
            for pid in self.pid_list:
                os.system("sudo kill -9 %s"%str(pid))
            for pid in self.tcpdump_pids:
                os.system("sudo kill -9 %s"%(str(pid)))
            time.sleep(5)

        logging.info("########################################################################\n")
        
        logging.info("Melody >> Stopping all packet captures ...")
        
        self.enable_TCP_RST()
        self.stop_control_network()
        logging.info("########################################################################")

    def initialize_project(self):
        """Initialize the project

        Starts all co-simulation hosts, switches, control network, proxy, packet captures, emulation & replay drivers
        and disturbance generator processes.

        :return: None
        """
        logging.info("Melody >> Initializing project ...")
        self.generate_node_mappings(self.network_configuration.roles)

        if self.enable_kronos:
            self.initialize_kronos_exp()
        #self.print_topo_info()
        self.start_host_processes()
        self.start_switch_processes()
        self.start_control_network()
        self.start_proxy_process()
        self.start_pkt_captures()
        self.start_replay_orchestrator()
        # Background related
        self.start_emulation_drivers()
        self.start_replay_drivers()
        self.start_disturbance_generator()

        # Kronos related
        if self.enable_kronos:
            self.set_netdevice_owners()
            self.start_synchronized_experiment()
            self.start_time = kronos_functions.getCurrentVirtualTime()
        else:
            self.start_time = time.time()
            for pid in self.emulation_driver_pids:  # *NEW*
                set_def_cpu_affinity(pid, self.cpus_subset)
            for pid in self.replay_driver_pids:
                set_def_cpu_affinity(pid, self.cpus_subset)
            for hostname in self.host_pids:
                set_def_cpu_affinity(self.host_pids[hostname], self.cpus_subset)
            for sw_name in self.switch_pids:
                set_def_cpu_affinity(self.switch_pids[sw_name], self.cpus_subset)

        self.wait_for_loaded_pcap_msg()

    def run_for(self, run_time_ns, sync=True):
        """Runs the cyber emulation for the specified time in nano seconds.

        The cyber emulation gets frozen after running for the specified duration iff it is under kronos control.

        :param run_time_ns: Batch run time in nano seconds
        :type run_time_ns: int
        :param sync: If True, it syncs with power simulator after running for the required time
        :type sync: bool
        :return: None
        """
        if not self.started:
            logging.info("########################################################################")
            logging.info("")
            logging.info("          Starting Experiment. Total Run time (secs) = %d" %self.run_time)
            logging.info("")
            logging.info("########################################################################")
            self.trigger_all_processes(defines.START_CMD)
            self.started = True

        if run_time_ns > 0:
            if run_time_ns < self.timeslice:
                run_time_ns = self.timeslice
            # progress for 20ms
            if self.timeslice > 20 * defines.NS_PER_MS:
                n_rounds = 1
            else:
                n_rounds = int(10 * defines.NS_PER_MS / self.timeslice)
            n_total_rounds = int(run_time_ns / self.timeslice)
            n_rounds_progressed = 0
            while True:

                if self.enable_kronos == 1:
                    kronos_functions.progressBy(self.timeslice, n_rounds)
                    n_rounds_progressed += n_rounds
                    stdout.write(
                        "\rRunning for %f ms. Number of Rounds Progressed:  %d/%d" % (
                        float(run_time_ns)/float(defines.MS),
                        n_rounds_progressed, n_total_rounds))
                    stdout.flush()

                    if n_rounds_progressed >= n_total_rounds:
                        break
                else:
                    time.sleep(float(run_time_ns)/float(defines.NS_PER_SEC))
                    break

            if self.enable_kronos == 1:
                if sync:
                    stdout.write(
                        "\r................... Syncing with power simulator ...................")
                    stdout.flush()
                    self.sync_with_power_simulator()
                stdout.write("\n")
                self.total_elapsed_virtual_time += \
                    float(run_time_ns)/float(defines.SEC)
            elif sync:
                stdout.write(
                    "\r................... Syncing with power simulator ...................\n")
                stdout.flush()
                self.sync_with_power_simulator()

    def close_project(self):
        """To be called on finish

        :return: None
        """

        self.cleanup()
