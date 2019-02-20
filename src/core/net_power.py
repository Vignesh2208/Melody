import datetime
import json
from datetime import datetime
from google.protobuf.empty_pb2 import Empty
from shared_buffer import *
from src.cyber_network.traffic_flow import ReplayFlowsContainer
from src.core.replay_orchestrator import ReplayOrchestrator
from src.utils.sleep_functions import sleep
from src.utils.util_functions import *
import grpc
from grpc import *
from src.proto import pss_pb2_grpc
from src.core.pss_server import *
from defines import *
from kronos_functions import *
from kronos_helper_functions import *
from concurrent import futures
from src.proto.pss_pb2_grpc import *
import subprocess
import sys
import os
import tempfile
import threading
from sys import stdout


def rpc_process():
    with grpc.insecure_channel('11.0.0.255:50051') as channel:
        stub = pss_pb2_grpc.pssStub(channel)
        status = stub.process(Empty())
        logging.info("Process return <%s>"%status.status)


class NetPower(object):

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
                 CPUS_SUBSET):

        self.network_configuration = network_configuration
        self.switch_2_switch_latency = self.network_configuration.topo_params["switch_switch_link_latency_range"][0]
        self.host_2_switch_latency = self.network_configuration.topo_params["host_switch_link_latency_range"][0]

        # Dictionary containing mappings, keyed by the id of the mininet host
        # Value is a tuple -- (IP Address, Role)
        self.project_name = self.network_configuration.project_name
        self.run_time = run_time
        self.power_simulator_ip = self.network_configuration.power_simulator_ip
        self.host_to_powersim_ids = {}
        self.powersim_id_to_host = {}
        self.project_dir = project_dir
        self.base_dir = base_dir
        self.enable_kronos = enable_kronos
        self.rel_cpu_speed = rel_cpu_speed
        self.cpus_subset = CPUS_SUBSET

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
        for i in xrange(0, len(self.network_configuration.roles)):
                mininet_host_name = self.network_configuration.roles[i][0]

                self.host_to_powersim_ids[mininet_host_name] = []
                port_mapping = self.network_configuration.roles[i][1]
                for mapping in port_mapping:
                    entity_id = mapping[0]
                    self.host_to_powersim_ids[mininet_host_name].append(entity_id)

                if len(self.host_to_powersim_ids[mininet_host_name]) == 0 :
                    self.host_to_powersim_ids[mininet_host_name].append("DUMMY_" + str(mininet_host_name))
        self.open_main_cmd_channel_buffers()
        
        self.check_kronos_loaded()
        self.replay_flows_container = ReplayFlowsContainer()
        for flow in self.replay_traffic_flows:
            self.replay_flows_container.add_replay_flow(flow)
        self.nodes_involved_in_replay = self.replay_flows_container.get_all_involved_nodes()
        self.replay_orchestrator = None
        self.prev_queued_disturbance_threads = []
        self.nxt_queued_disturbance_threads = []
        self.total_elapsed_virtual_time = 0.0
        

        set_cpu_affinity(int(os.getpid()))

    def get_emulation_driver_params(self):
        for bg_flow in self.emulated_background_traffic_flows:
            self.emulation_driver_params.append(bg_flow.get_emulated_driver_attributes(for_client=True))
            attr = bg_flow.get_emulated_driver_attributes(for_client=False)
            if attr is not None:
                self.emulation_driver_params.append(attr)

    def check_kronos_loaded(self):
        if self.enable_kronos == 1 and is_module_loaded() == 0:
            print "ERROR: Kronos is not loaded. Please load and try again!"
            sys.exit(0)
        elif self.enable_kronos == 1:
            self.initialize_kronos_exp()

    def initialize_kronos_exp(self):
        ret = initializeExp(1);
        if ret < 0:
            print "ERROR:  Kronos initialization failed. Exiting ..."
            sys.exit(0)

    def start_synchronized_experiment(self):

        if self.enable_kronos == 1:
            print "Kronos >> Synchronizing and freezing all processes ..."
            n_tracers = len(self.pid_list)
            while synchronizeAndFreeze(n_tracers) <= 0:
                print "Kronos >> Synchronize and Freeze failed. Retrying in 1 sec"
                time.sleep(1)
            print "Kronos >> Synchronize and Freeze succeeded !"
            print "Kronos >> Experiment started with Rel_cpu_speed: ", self.rel_cpu_speed, " at Local Time: " + str(
                datetime.now())

        else:
            self.start_time = time.time()
            print "Melody >> Experiment started with Kronos disabled ... "

    def stop_synchronized_experiment(self):

        print "########################################################################"
        if self.enable_kronos == 1:
            stopExp()
            print "Kronos >> Stopping synchronized experiment at Local Time: ", str(datetime.now())
            self.trigger_all_processes("EXIT")
            self.replay_orchestrator.send_command("EXIT")
            print "Kronos >> Stopped synchronized experiment"
        else:
            print "Melody >> Stopping emulation at Local Time: ", str(datetime.now())
        print "########################################################################"

    def generate_node_mappings(self, roles):
        with open(self.node_mappings_file_path, "w") as outfile:
            for i in xrange(0, len(roles)):
                mininet_host_name = roles[i][0]
                port_mapping = roles[i][1]
                for mapping in port_mapping:
                    entity_id = mapping[0]
                    entity_port = mapping[1]
                    self.powersim_id_to_host[entity_id] = {}
                    self.powersim_id_to_host[entity_id]["port"] = entity_port
                    self.powersim_id_to_host[entity_id]["mapped_host"] = mininet_host_name
                    self.powersim_id_to_host[entity_id]["mapped_host_ip"] = "10.0.0." + str(mininet_host_name[1:])
                if len(port_mapping) == 0:
                    entity_id = "DUMMY_" + str(mininet_host_name)
                    entity_port = 5100
                    self.powersim_id_to_host[entity_id] = {}
                    self.powersim_id_to_host[entity_id]["port"] = entity_port
                    self.powersim_id_to_host[entity_id]["mapped_host"] = mininet_host_name
                    self.powersim_id_to_host[entity_id]["mapped_host_ip"] = "10.0.0." + str(mininet_host_name[1:])

            json.dump(self.powersim_id_to_host, outfile)

    def cmd_to_start_process_under_tracer(self, cmd_to_run, tracer_id):

        tracer_path = "/usr/bin/tracer"
        tracer_args = [tracer_path]
        tracer_args.extend(["-i", str(tracer_id)])
        tracer_args.extend(["-r", str(self.rel_cpu_speed)])
        tracer_args.extend(["-n", str(self.timeslice)])
        tracer_args.extend(["-c", "\"" + cmd_to_run + "\""])
        tracer_args.append("-s")
        return ' '.join(tracer_args)

    def start_host_processes(self):
        print "Melody >> Starting all hosts: ", self.cyber_host_apps, self.host_to_powersim_ids

        for mininet_host in self.network_configuration.mininet_obj.hosts:
            for mapped_powerim_id in self.host_to_powersim_ids[mininet_host.name]:
                host_id = int(mininet_host.name[1:])
                host_log_file = self.log_dir + "/" + mapped_powerim_id  + "_log.txt"
                host_py_script = self.base_dir + "/src/core/host.py"
                cmd_to_run = "python " + str(
                    host_py_script) + " -l " + host_log_file + " -c " + self.node_mappings_file_path + " -r " + str(
                    self.run_time) + " -n " + str(self.project_name) + " -d " + str(host_id) + " -m "  + str(mapped_powerim_id)

                if mininet_host.name in self.cyber_host_apps:
                    cmd_to_run += " -a " + str(self.cyber_host_apps[mininet_host.name])
                else:
                    cmd_to_run += " -a NONE"

                if self.enable_kronos == 1:
                    cmd_to_run = self.cmd_to_start_process_under_tracer(cmd_to_run, host_id)
                cmd_to_run += ' > ' + host_log_file + ' 2>&1 & echo $! '

                with tempfile.NamedTemporaryFile() as f:
                    mininet_host.cmd(cmd_to_run + '>> ' + f.name)
                    pid = int(f.read())
                    self.host_pids[mininet_host.name] = pid
                    self.pid_list.append(pid)

                set_cpu_affinity(mininet_host.pid)

    def start_switch_processes(self):
        print "Melody >> Starting all switches ..."
        n_hosts = len(self.host_pids.keys())

        for mininet_switch in self.network_configuration.mininet_obj.switches:
            sw_id = int(mininet_switch.name[1:]) + n_hosts
            cmd_to_run = "python " + self.base_dir + "/src/utils/dummy_nop_process.py"
            sw_log_file = "/tmp/sw_" + str(sw_id) + "_log.txt"
            if self.enable_kronos == 1:
                cmd_to_run = self.cmd_to_start_process_under_tracer(cmd_to_run, sw_id)
            cmd_to_run += ' > ' + sw_log_file + ' 2>&1 & echo $! '
            with tempfile.NamedTemporaryFile() as f:
                mininet_switch.cmd(cmd_to_run + '>> ' + f.name)
                pid = int(f.read())
                self.switch_pids[mininet_switch.name] = pid
                self.pid_list.append(pid)

            set_cpu_affinity(mininet_switch.pid)

    def start_emulation_drivers(self):

        driver_py_script = self.base_dir + "/src/core/emulation_driver.py"
        tracer_id = len(self.host_pids.keys()) + len(self.switch_pids.keys())

        for edp in self.emulation_driver_params:

            mininet_host = self.network_configuration.mininet_obj.get(edp["node_id"])
            driver_log_file = "/tmp/" + str(edp["driver_id"]) + "_log.txt"
            tracer_id += 1

            input_params_file_path = "/tmp/" + edp["driver_id"] + ".json"
            with open(input_params_file_path, "w") as f:
                json.dump(edp, f)

            cmd_to_run = "python " + str(driver_py_script) + " --input_params_file_path=" + input_params_file_path
            if self.enable_kronos == 1:
                cmd_to_run = self.cmd_to_start_process_under_tracer(cmd_to_run, tracer_id)
            cmd_to_run += ' > ' + driver_log_file + ' 2>&1 & echo $! '

            with tempfile.NamedTemporaryFile() as f:
                mininet_host.cmd(cmd_to_run + '>> ' + f.name)
                pid = int(f.read())
                self.emulation_driver_pids.append(pid)
                self.pid_list.append(pid)
        print "Melody >> All background flow drivers started ..."

    def start_replay_drivers(self):

        driver_py_script = self.base_dir + "/src/core/replay_driver.py"
        tracer_id = len(self.host_pids.keys()) + len(self.switch_pids.keys()) + len(self.emulation_driver_pids)

        for node in self.nodes_involved_in_replay:
            mininet_host = self.network_configuration.mininet_obj.get(node)
            rdp = {"driver_id": mininet_host.name + "-replay",
                   "run_time": self.run_time,
                   "node_id": mininet_host.name,
                   "node_ip": mininet_host.IP(),
                   "replay_plan_file_path": "/tmp/replay_plan.json"
                   }

            driver_log_file = "/tmp/" + str(rdp["driver_id"]) + "_log.txt"
            input_params_file_path = "/tmp/" + str(rdp["driver_id"]) + ".json"
            with open(input_params_file_path, "w") as f:
                json.dump(rdp, f)
            tracer_id += 1

            cmd_to_run = "python " + str(driver_py_script) + " --input_params_file_path=" + input_params_file_path
            if self.enable_kronos == 1:
                cmd_to_run = self.cmd_to_start_process_under_tracer(cmd_to_run, tracer_id)
            cmd_to_run += ' > ' + driver_log_file + ' 2>&1 & echo $! '

            with tempfile.NamedTemporaryFile() as f:
                mininet_host.cmd(cmd_to_run + '>> ' + f.name)
                pid = int(f.read())
                self.replay_driver_pids.append(pid)
                self.pid_list.append(pid)

        print "Melody >> All replay flow drivers started ... "

    def start_host_capture(self, host_obj):
        core_cmd = "tcpdump"
        capture_cmd = "sudo " + core_cmd
        capture_log_file = self.log_dir + "/" + host_obj.name + ".pcap"
        with open(capture_log_file, "w") as f:
            pass

        capture_cmd = capture_cmd + " -i " + str(host_obj.name + "-eth0")
        capture_cmd = capture_cmd + " -w " + capture_log_file + " -U -B 20000 ip & > /dev/null"
        self.n_actual_tcpdump_procs = self.n_actual_tcpdump_procs + 1

        host_obj.cmd(capture_cmd)

    def start_all_host_captures(self):
        print "Melody >> Starting tcpdump capture on hosts ..."
        for host in self.network_configuration.mininet_obj.hosts:
            self.start_host_capture(host)

    def start_pkt_captures(self):
        self.start_all_host_captures()

        print "Melody >> Starting tcpdump capture on switches ..."

        for mininet_link in self.network_configuration.mininet_obj.links:
            switchIntfs = mininet_link.intf1
            core_cmd = "tcpdump"
            capture_cmd = "sudo " + core_cmd

            # 1. to capture all pcaps:
            if mininet_link.intf1.name.startswith("s") and mininet_link.intf2.name.startswith("s"):
                capture_log_file = self.log_dir + "/" + mininet_link.intf1.name + "-" + mininet_link.intf2.name + ".pcap"
                with open(capture_log_file, "w") as f:
                    pass

                capture_cmd = capture_cmd + " -i " + str(switchIntfs.name)
                capture_cmd = capture_cmd + " -w " + capture_log_file + " -B 40000 ip & > /dev/null"
                self.n_actual_tcpdump_procs = self.n_actual_tcpdump_procs + 1

                proc = subprocess.Popen(capture_cmd, shell=True)
                self.tcpdump_procs.append(proc)
                set_cpu_affinity(int(proc.pid))  # *NEW* ??? not dependent on timekeeper running?

        # Get all the pids of actual tcpdump processes
        actual_tcpdump_pids = get_pids_with_cmd(cmd=core_cmd, expected_no_of_pids=self.n_actual_tcpdump_procs)
        set_cpu_affinity_pid_list(actual_tcpdump_pids)

        # Get all the pids of sudo tcpdump parents
        sudo_tcpdump_parent_pids = get_pids_with_cmd(cmd="sudo " + core_cmd,
                                                     expected_no_of_pids=self.n_actual_tcpdump_procs)
        set_cpu_affinity_pid_list(sudo_tcpdump_parent_pids)

        self.tcpdump_pids = sudo_tcpdump_parent_pids

    def set_netdevice_owners(self):
        print "Kronos >> Assuming control over mininet network interfaces ..."
        for mininet_switch in self.network_configuration.mininet_obj.switches:
            assert mininet_switch.name in self.switch_pids
            tracer_pid = self.switch_pids[mininet_switch.name]

            for name in mininet_switch.intfNames():
                if name != "lo":
                    set_netdevice_owner(tracer_pid, name)

        for host_name in self.host_pids:
            mininet_host = self.network_configuration.mininet_obj.get(host_name)
            assert mininet_host.name in self.host_pids
            tracer_pid = self.host_pids[mininet_host.name]
            for name in mininet_host.intfNames():
                if name != "lo":
                    set_netdevice_owner(tracer_pid, name)

    def start_proxy_process(self):

        print "Melody >> Starting proxy ... "
        proxy_script = self.base_dir + "/src/core/pss_server.py"
        cmd_to_run = "python " + str(proxy_script) + " --project_dir=" + self.project_dir + " --listen_ip=11.0.0.255"
        cmd_to_run += ' > /tmp/proxy_log.txt 2>&1 & echo $! '
        self.proxy_pid = -1
        with tempfile.NamedTemporaryFile() as f:
            os.system(cmd_to_run + '>> ' + f.name)
            pid = int(f.read())
            self.proxy_pid = pid
            print "Melody >> Proxy PID: ", self.proxy_pid, " Waiting 5 sec for GRPC server to get setup ..."
            time.sleep(5.0)

    def start_control_network(self):
        print "Melody >> Starting Control Network"
        for host in self.network_configuration.mininet_obj.hosts:
            host_number = host.name[1:]
            host.cmd("ip link add eth0 type veth peer name " + host.name + "base netns 1")
            host.cmd("ifconfig eth0 up")
            host.cmd("ifconfig eth0 11.0.0." + str(host_number))
        os.system("sudo ip link add base type veth peer name hostbase netns 1")
        os.system("sudo ifconfig base 11.0.0.255 up")
        os.system("sudo ifconfig hostbase up")
        os.system("sudo brctl addbr connect")
        for host in self.network_configuration.mininet_obj.hosts:
            os.system("sudo ifconfig " + str(host.name) + "base up")
            os.system("sudo brctl addif connect " + str(host.name) + "base")
        os.system("sudo brctl addif connect hostbase")
        os.system("sudo ifconfig connect up")



    def stop_control_network(self):
        print "Melody >> Stopping Control Network"
        os.system("sudo kill -9 " + str(self.proxy_pid))
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


    def trigger_proxy_batch_processing(self):

        print "Triggering next batch processing at proxy ..."
        t = threading.Thread(target=rpc_process)
        t.start()
        t.join()

    def send_disturbance_to_powersim(self, obj_type, obj_id, field_type, value):
        print "Queueing disturbance: OBJ_TYPE: %s, OBJ_ID: %s, "\
              "FIELD_TYPE: %s, DISTURBANCE_VALUE: %s"%(obj_type, obj_id, field_type, value)

        if self.enable_kronos:
            tstamp = self.total_elapsed_virtual_time
        else:
            tstamp = time.time()

        t = threading.Thread(target=rpc_write_disturbance, args=(obj_type, obj_id, field_type, value, tstamp,))
        t.start()


    def start_replay_orchestrator(self):
        print "Melody >> Starting replay orchestrator ... "

        self.replay_flows_container.create_replay_plan()
        replay_plan_file = "/tmp/replay_plan.json"
        self.replay_orchestrator = ReplayOrchestrator(self, replay_plan_file, self.run_time)
        self.replay_orchestrator.start()

    def send_cmd_to_node(self, node_name, cmd):
        mininet_host = self.network_configuration.mininet_obj.get(node_name)
        if mininet_host is not None:
            mininet_host.cmd(cmd)

    def allow_icmp_requests(self):
        for host in self.network_configuration.mininet_obj.hosts:
            self.send_cmd_to_node(host.name, "sudo iptables -I OUTPUT -p icmp -j ACCEPT &")

    def allow_icmp_responses(self):
        for host in self.network_configuration.mininet_obj.hosts:
            self.send_cmd_to_node(host.name, "sudo iptables -I INPUT -p icmp -j ACCEPT &")

    def disable_TCP_RST(self):

        for host in self.network_configuration.mininet_obj.hosts:
            self.send_cmd_to_node(host.name, "sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j DROP")
        sleep(1)

    def enable_TCP_RST(self):

        for host in self.network_configuration.mininet_obj.hosts:
            self.send_cmd_to_node(host.name, "sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j ACCEPT")

    def open_main_cmd_channel_buffers(self):
        print "Melody >> Opening main inter-process communication channels ..." 
        for mininet_host in self.network_configuration.mininet_obj.hosts:
            if mininet_host.name in self.host_to_powersim_ids:
                for mapped_powersim_id in self.host_to_powersim_ids[mininet_host.name]:
                    result = self.shared_buf_array.open(mapped_powersim_id + "-main-cmd-channel-buffer", isProxy=True)
                    if result == BUF_NOT_INITIALIZED or result == FAILURE:
                        print "Shared Buffer open failed! Buffer not initialized for host: " + str(mininet_host.name)
                        sys.exit(0)

            result = self.shared_buf_array.open(bufName=str(mininet_host.name) + "-replay-main-cmd-channel-buffer",
                                                isProxy=True)
            if result == BUF_NOT_INITIALIZED or result == FAILURE:
                print "Shared Buffer open open failed! Buffer not initialized for replay driver: " \
                      + str(mininet_host.name)
                sys.exit(0)

        for edp in self.emulation_driver_params:
            result = self.shared_buf_array.open(bufName=edp["driver_id"] + "-main-cmd-channel-buffer", isProxy=True)
            if result == BUF_NOT_INITIALIZED or result == FAILURE:
                print "Shared Buffer open failed! Buffer not initialized for driver: " + edp["driver_id"]
                sys.exit(0)

        print "Melody >> Opened main inter-process communication channels ... "

    def trigger_all_processes(self, trigger_cmd):
        for mininet_host in self.network_configuration.mininet_obj.hosts:
            if mininet_host.name in self.host_to_powersim_ids:
                for mapped_powersim_id in self.host_to_powersim_ids[mininet_host.name]:
                    ret = 0
                    while ret <= 0:
                        ret = self.shared_buf_array.write(mapped_powersim_id + "-main-cmd-channel-buffer", trigger_cmd, 0)

        for edp in self.emulation_driver_params:
            ret = 0
            while ret <= 0:
                ret = self.shared_buf_array.write(edp["driver_id"] + "-main-cmd-channel-buffer", trigger_cmd, 0)

        print "Melody >> Triggered hosts and drivers with command: ", trigger_cmd

    def trigger_nxt_replay(self):
        print "Melody >> Triggering next replay ..."
        self.replay_orchestrator.send_command("TRIGGER")

    def wait_for_loaded_pcap_msg(self):

        print "Melody >> In Warm up phase waiting for pcaps to be loaded by all replay drivers ... "
        n_warmup_rounds = 0
        outstanding_hosts = self.nodes_involved_in_replay
        while True:
            if len(outstanding_hosts) == 0:
                break

            for host in outstanding_hosts:
                dummy_id, msg = self.shared_buf_array.read(str(host) \
                                                            + "-replay-main-cmd-channel-buffer")
                if msg == "LOADED":
                    print "Melody >> Got a PCAP-Loaded message from replay driver for node: ", host
                    outstanding_hosts.remove(host)
                    sys.stdout.flush()
            if self.enable_kronos == 1:
                progress_n_rounds(1)
                n_warmup_rounds += 1
                stdout.write("\rNumber of rounds ran until all replay pcaps were loaded: %d" % n_warmup_rounds)
                stdout.flush()

            else:
                sleep(0.1)
        print "\nMelody >> All replay drivers ready to proceed ..."
        sys.stdout.flush()

    def print_topo_info(self):

        print "########################################################################"
        print ""
        print "                        Topology Information"
        print ""
        print "########################################################################"
        print ""
        print "Links in the network topology:"
        for link in self.network_configuration.ng.get_switch_link_data():
            print link

        print "All the hosts in the topology:"
        for sw in self.network_configuration.ng.get_switches():
            print "Hosts at switch:", sw.node_id
            for h in sw.attached_hosts:
                print "Name:", h.node_id, "IP:", h.ip_addr, "Port:", h.switch_port
        print ""
        print "########################################################################"

    def cleanup(self):

        # Clean up ...
        if self.enable_kronos == 1:
            self.stop_synchronized_experiment()
            time.sleep(5)
        else:
            self.trigger_all_processes("EXIT")
            self.replay_orchestrator.send_command("EXIT")
            time.sleep(5)

        print "Cleaning up ..."
        self.enable_TCP_RST()
        self.stop_control_network()
        #print "Stopping all TCPDUMP processes ..."
        #for pid in self.tcpdump_pids:
        #    os.system("sudo kill -2 " + str(pid))
        self.network_configuration.cleanup_mininet()

    def initialize_project(self):
        print "Melody >> Initializing project ..."
        self.generate_node_mappings(self.network_configuration.roles)
        self.print_topo_info()
        self.start_host_processes()
        self.start_switch_processes()
        self.start_control_network()
        self.start_proxy_process()
        self.start_pkt_captures()
        self.start_replay_orchestrator()
        # Background related
        self.start_emulation_drivers()
        self.start_replay_drivers()


       

        # Kronos related
        if self.enable_kronos:

            self.set_netdevice_owners()
            self.start_synchronized_experiment()
            self.start_time = get_current_virtual_time()
        else:
            self.start_time = time.time()
            # if timekeeper is not enabled, restrict emulation/replay operations to cpu subset
            for pid in self.emulation_driver_pids:  # *NEW*
                set_def_cpu_affinity(pid, self.cpus_subset)
            for pid in self.replay_driver_pids:
                set_def_cpu_affinity(pid, self.cpus_subset)
            for hostname in self.host_pids:
                set_def_cpu_affinity(self.host_pids[hostname], self.cpus_subset)
            for sw_name in self.switch_pids:
                set_def_cpu_affinity(self.switch_pids[sw_name], self.cpus_subset)

        self.wait_for_loaded_pcap_msg()

    def run_for(self, run_time_ns):

        if not self.started:
            print "########################################################################"
            print ""
            print "          Starting Experiment. Total Run time (secs) = ", self.run_time
            print ""
            print "########################################################################"
            self.trigger_all_processes("START")
            self.started = True

        if run_time_ns > 0:
            if run_time_ns < self.timeslice:
                run_time_ns = self.timeslice
            # progress for 20ms
            if self.timeslice > 20 * NS_PER_MS:
                n_rounds = 1
            else:
                n_rounds = int(20 * NS_PER_MS / self.timeslice)
            n_total_rounds = int(run_time_ns / self.timeslice)
            n_rounds_progressed = 0

            k = 0
            while True:

                if self.enable_kronos == 1:
                    sys.stdout.flush()
                    progress_n_rounds(n_rounds)
                    n_rounds_progressed += n_rounds
                    stdout.write("\rNumber of Rounds Progressed:  %d/%d" % (n_rounds_progressed, n_total_rounds))
                    stdout.flush()

                    if n_rounds_progressed >= n_total_rounds:
                        sys.stdout.flush()
                        break
                else:
                    time.sleep(float(run_time_ns)/float(NS_PER_SEC))
                    break

            if self.enable_kronos == 1:
                stdout.write("\n")
                self.total_elapsed_virtual_time += float(run_time_ns)/float(SEC)

    def close_project(self):
        self.cleanup()
