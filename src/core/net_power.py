import datetime
import json
import os
import uuid
from datetime import datetime
from shared_buffer import *
from utils.sleep_functions import sleep
from utils.util_functions import *
from defines import *
from kronos_functions import *
from kronos_helper_functions import *
import subprocess
import sys
import os
from fractions import gcd
import threading
import tempfile

NS_PER_MS = 1000000



class NetPower(object):

    def __init__(self,
                 run_time,
                 network_configuration,
                 script_dir,
                 base_dir,
                 attack_plan_dir,
                 log_dir,
                 emulated_background_traffic_flows,
                 enable_kronos,
                 rel_cpu_speed,
		 CPUS_SUBSET):	# *NEW*

        self.network_configuration = network_configuration
        self.switch_2_switch_latency = self.network_configuration.topo_params["switch_switch_link_latency_range"][0]
        self.host_2_switch_latency = self.network_configuration.topo_params["host_switch_link_latency_range"][0]

        # Dictionary containing mappings, keyed by the id of the mininet host
        # Value is a tuple -- (IP Address, Role)
        self.project_name = self.network_configuration.project_name
        self.run_time = run_time
        self.power_simulator_ip = self.network_configuration.power_simulator_ip
        self.node_mappings = {}
        self.control_node_id = None

        self.script_dir = script_dir
        self.base_dir = base_dir
        self.timekeeper_dir = self.base_dir + "/src/core/dilation-code"
        self.enable_kronos = enable_kronos
        self.rel_cpu_speed = rel_cpu_speed
        self.cpus_subset = CPUS_SUBSET 	# *NEW*

        self.attack_plan_dir = attack_plan_dir
        self.pid_list = []
        self.host_pids = {}
        self.switch_pids = {}
        self.emulation_driver_pids = []
        self.replay_driver_pids = []
        self.timeslice = self.get_timeslice()

        self.emulated_background_traffic_flows = emulated_background_traffic_flows

        self.emulation_driver_params = []
        self.get_emulation_driver_params()

        self.node_mappings_file_path = self.script_dir + "/node_mappings.txt"
        self.log_dir = log_dir
        self.flag_debug = True 	# flag for debug printing

        # Clean up logs from previous run(s)
        os.system("rm -rf " + self.log_dir + "/*")

        self.proxy_dir = self.base_dir + "/src/core"
        self.sharedBufferArray = shared_buffer_array()
        self.tcpdump_procs = []
        self.n_actual_tcpdump_procs = 0
        self.n_dilated_tcpdump_procs = 0


        result = self.sharedBufferArray.open(bufName="cmd-channel-buffer",isProxy=False)
        if result == BUF_NOT_INITIALIZED or result == FAILURE:
            print "Cmd channel buffer open failed! "
            sys.exit(0)

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.open_main_cmd_channel_buffers()
        self.check_kronos_loaded()

        set_cpu_affinity(int(os.getpid()))


    def get_timeslice(self):
        if self.switch_2_switch_latency == 0 and self.host_2_switch_latency == 0:
            return NS_PER_MS # 1ms

        if self.switch_2_switch_latency == 0 :
            return self.host_2_switch_latency*NS_PER_MS

        if self.host_2_switch_latency == 0 :
            return self.switch_2_switch_latency*NS_PER_MS

        gcd_val = gcd(self.host_2_switch_latency*NS_PER_MS, self.switch_2_switch_latency*NS_PER_MS)
        return gcd_val


    def get_emulation_driver_params(self):
        for bg_flow in self.emulated_background_traffic_flows:

            if bg_flow.client_expect_file:
                self.emulation_driver_params.append({"type": bg_flow.type,
                                                     "cmd": bg_flow.client_expect_file,
                                                     "offset": bg_flow.offset + 1,
                                                     "inter_flow_period": bg_flow.inter_flow_period,
                                                     "run_time": bg_flow.run_time,
                                                     "long_running": bg_flow.long_running,
                                                     "root_user_name": bg_flow.root_user_name,
                                                     "root_password": bg_flow.root_password,
                                                     "node_id": bg_flow.src_mn_node.name,
                                                     "driver_id":  bg_flow.src_mn_node.name + "-emulation-" + str(uuid.uuid1())})

            if bg_flow.server_process_start_cmd:
                self.emulation_driver_params.append({"type": TRAFFIC_FLOW_ONE_SHOT,
                                                     "cmd": bg_flow.server_process_start_cmd,
                                                     "offset": bg_flow.offset,
                                                     "inter_flow_period": bg_flow.inter_flow_period,
                                                     "run_time": bg_flow.run_time,
                                                     "long_running": bg_flow.long_running,
                                                     "root_user_name": bg_flow.root_user_name,
                                                     "root_password": bg_flow.root_password,
                                                     "node_id": bg_flow.dst_mn_node.name,
                                                     "driver_id": bg_flow.src_mn_node.name + "-emulation-" + str(uuid.uuid1())})

    def check_kronos_loaded(self) :
        if self.enable_kronos == 1 and is_module_loaded() == 0:
            print "Kronos is not loaded. Pls load and try again!"
            sys.exit(0)

    def initialize_kronos_exp(self) :
        ret = initializeExp(1);
        if ret < 0 :
            print "Kronos Initialization Failed. Exiting ..."
            sys.exit(0)
            
    def start_synchronized_experiment(self) :

        if self.enable_kronos == 1 :
            print "Kronos synchronizing and freezing ..."
            n_tracers = len(self.host_pids.keys()) + len(self.switch_pids.keys()) +  len(emulation_driver_pids) + len(replay_driver_pids)
            while synchronizeAndFreeze(n_tracers) <= 0 :
                print "Sync and Freeze Failed. Retrying in 1 sec"
                time.sleep(1)
            print "Synchronize and Freeze succeeded !"
            print "Experiment started: rel_cpu_speed = ", self.rel_cpu_speed, " local Time = " + str(datetime.now())

        else:
            self.start_time = time.time()
            print "Experiment started with Kronos Disabled ... "

    def stop_synchronized_experiment(self) :

        print "########################################################################"
        if self.enable_kronos == 1 :
            os.system("sudo killall -9 tcpdump")
            stopExp()
            print "Stopping synchronized experiment at local time = ", str(datetime.now())
            self.trigger_all_processes("EXIT")
            print "Stopped synchronized experiment"
        else:
            print "Stopping synchronized experiment at local time = ", str(datetime.now())
        print "########################################################################"

    def generate_node_mappings(self, roles):
        with open(self.node_mappings_file_path,"w") as outfile:
            for i in xrange(0,len(roles)):
                mininet_host = self.network_configuration.mininet_obj.hosts[i]
                self.node_mappings[mininet_host.name] = (mininet_host.IP(), roles[i], DEFAULT_HOST_UDP_PORT)
                lineTowrite = str(mininet_host.name) + "," + str(mininet_host.IP()) + "," + str(DEFAULT_HOST_UDP_PORT) + ","

                for j in xrange(0,len(roles[i][1])) :
                    if j < len(roles[i][1]) - 1 :
                        lineTowrite = lineTowrite + roles[i][1][j] + ","
                    else:
                        lineTowrite = lineTowrite + roles[i][1][j] + "\n"

                outfile.write(lineTowrite)

    def cmd_to_start_process_under_tracer(cmd_to_run, tracer_id) :

                tracer_path = "/usr/bin/tracer"
                tracer_args = [tracer_path]
                tracer_args.extend(["-i", str(tracer_id)])
                tracer_args.extend(["-r", str(self.rel_cpu_speed)])
                tracer_args.extend(["-n", str(self.timeslice)])
                tracer_args.extend(["-c", "\"" + cmd_to_run + "\""])
                tracer_args.append("-s")
                return ' '.join(tracer_args)

        

    def start_host_processes(self):
        print "Starting all Host Commands ..."

        pid_list= []

        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            host_id = int(mininet_host.name[1:])
            host_role = self.node_mappings[mininet_host.name][1][0]

            if "controller" not in host_role:
                host_log_file = self.log_dir + "/host_" + str(host_id) + "_log.txt"
            else:
                host_log_file = self.log_dir + "/controller_node_log.txt"

            host_py_script = self.proxy_dir + "/host.py"
            cmd_to_run = "python " + str(host_py_script) + " -l " + host_log_file + " -c " + self.node_mappings_file_path  + " -r " + str(self.run_time) + " -n " + str(self.project_name) + " -d " + str(host_id)

            if "controller" in host_role :
                cmd_to_run = cmd_to_run + " -i"
                self.control_node_id = host_id
            if self.enable_kronos == 1 :
                cmd_to_run = cmd_to_start_process_under_tracer(cmd_to_run, host_id)
            cmd_to_run += ' > ' + host_log_file + ' 2>&1 & echo $! '
  
            with tempfile.NamedTemporaryFile() as f:
                mininet_host.cmd(cmd_to_run + '>> ' + f.name)
                pid = int(f.read())
                self.host_pids[mininet_host.name] = pid
                self.pid_list.append(pid)

            set_cpu_affinity(mininet_host.pid)


    def start_switch_processes(self) :
        pid = 0
        print "Starting dummy switch processes ..."
        n_hosts = len(self.host_pids.keys())
        for i in xrange(0,len(self.network_configuration.mininet_obj.switches)) :
            mininet_switch = self.network_configuration.mininet_obj.switches[i]
            sw_id = int(mininet_host.name[1:]) + n_hosts
            cmd_to_run = "python " + self.base_dir + "/src/utils/dummy_nop_process.py"
            sw_log_file = self.log_dir + "/sw_" + str(sw_id) + "_log.txt"
            if self.enable_kronos == 1 :
                cmd_to_run = cmd_to_start_process_under_tracer(cmd_to_run, sw_id)
            cmd_to_run += ' > ' + sw_log_file + ' 2>&1 & echo $! '
            with tempfile.NamedTemporaryFile() as f:
                mininet_switch.cmd(cmd_to_run + '>> ' + f.name)
                pid = int(f.read())
                self.switch_pids[mininet_switch.name] = pid
                self.pid_list.append(pid)

            set_cpu_affinity(mininet_switch.pid)


    def start_emulation_drivers(self):

        
        driver_py_script = self.proxy_dir + "/emulation_driver.py"
        tracer_id = len(self.host_pids.keys()) + len(self.switch_pids.keys())

        for edp in self.emulation_driver_params:

            mininet_host = self.network_configuration.mininet_obj.get(edp["node_id"])
            driver_log_file = self.log_dir + "/" + str(edp["driver_id"]) + "_log.txt"  
            tracer_id = += 1

            input_params_file_path = self.log_dir + "/" + edp["driver_id"] + ".json"
            with open(input_params_file_path, "w") as f:
                json.dump(edp, f)

            cmd_to_run = "python " + str(driver_py_script) + " --input_params_file_path " + input_params_file_path
            if self.enable_kronos == 1:
                cmd_to_run = cmd_to_start_process_under_tracer(cmd_to_run, tracer_id)
            cmd_to_run += ' > ' + driver_log_file + ' 2>&1 & echo $! '
  
            with tempfile.NamedTemporaryFile() as f:
                mininet_host.cmd(cmd_to_run + '>> ' + f.name)
                pid = int(f.read())
                self.emulation_driver_pids.append(pid)
                self.pid_list.append(pid)
        print "All emulation drivers started !"


    def start_replay_drivers(self):

        n_drivers = 0
        driver_py_script = self.proxy_dir + "/replay_driver.py"
        tracer_id = len(self.host_pids.keys()) + len(self.switch_pids.keys()) + len(self.emulation_driver_pids)

        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]

            rdp = {"driver_id": mininet_host.name + "-replay",
                   "run_time": self.run_time,
                   "node_id": mininet_host.name,
                   "node_ip": mininet_host.IP(),
                   "attack_path_file_path": self.attack_plan_dir + "/attack_plan.json"
                   }

            driver_log_file = self.log_dir + "/" + str(rdp["driver_id"]) + "_log.txt"
            input_params_file_path = self.log_dir + "/" + rdp["driver_id"] + ".json"
            with open(input_params_file_path, "w") as f:
                json.dump(rdp, f)
            tracer_id = += 1

            cmd_to_run = "python " + str(driver_py_script) + " --input_params_file_path " + input_params_file_path
            if self.enable_kronos == 1:
                cmd_to_run = cmd_to_start_process_under_tracer(cmd_to_run, tracer_id)
            cmd_to_run += ' > ' + driver_log_file + ' 2>&1 & echo $! '

            with tempfile.NamedTemporaryFile() as f:
                mininet_host.cmd(cmd_to_run + '>> ' + f.name)
                pid = int(f.read())
                self.replay_driver_pids.append(pid)
                self.pid_list.append(pid)

        print "All replay drivers started !"

        

    def start_host_capture(self, host_obj):
        core_cmd = "tcpdump"
        capture_cmd = "sudo " + core_cmd
        capture_log_file = self.log_dir  + "/" + host_obj.name + ".pcap"
        with open(capture_log_file , "w") as f :
            pass

        capture_cmd = capture_cmd + " -i "  + str(host_obj.name + "-eth0")
        capture_cmd = capture_cmd + " -w " + capture_log_file + " -U -B 20000 ip & > /dev/null"
        self.n_actual_tcpdump_procs = self.n_actual_tcpdump_procs + 1

        host_obj.cmd(capture_cmd)
    

    def start_all_host_captures(self):
        print "Starting tcpdump capture on hosts ..."
        for h in self.network_configuration.get_mininet_hosts_obj():
            if h.name != "h1":
                continue
            self.start_host_capture(h)

    def start_pkt_captures(self):
        self.start_all_host_captures()
    
        print "Starting tcpdump capture on switches ..."

        for i in range(len(self.network_configuration.mininet_obj.links)):
            mininet_link = self.network_configuration.mininet_obj.links[i]
            switchIntfs = mininet_link.intf1
            core_cmd = "tcpdump"
            capture_cmd = "sudo " + core_cmd

            # 1. to capture all pcaps:
            if mininet_link.intf1.name.startswith("s") and mininet_link.intf2.name.startswith("s") :
                capture_log_file = self.log_dir  + "/" + mininet_link.intf1.name + "-" + mininet_link.intf2.name + ".pcap"
                with open(capture_log_file , "w") as f :
                    pass

                capture_cmd = capture_cmd + " -i "  + str(switchIntfs.name)
                capture_cmd = capture_cmd + " -w " + capture_log_file + " -B 40000 ip & > /dev/null"
                self.n_actual_tcpdump_procs = self.n_actual_tcpdump_procs + 1

                proc = subprocess.Popen(capture_cmd, shell=True)
                self.tcpdump_procs.append(proc)
                set_cpu_affinity(int(proc.pid))   # *NEW* ??? not dependent on timekeeper running?

            capture_cmd = "sudo " + core_cmd

        # Get all the pids of actual tcpdump processes
        actual_tcpdump_pids = get_pids_with_cmd(cmd=core_cmd, expected_no_of_pids=self.n_actual_tcpdump_procs)
        set_cpu_affinity_pid_list(actual_tcpdump_pids)

        # Get all the pids of sudo tcpdump parents
        sudo_tcpdump_parent_pids = get_pids_with_cmd(cmd="sudo " + core_cmd,expected_no_of_pids=self.n_actual_tcpdump_procs)
        set_cpu_affinity_pid_list(sudo_tcpdump_parent_pids)

    def set_netdevice_owners(self) :
        print "Setting interface owners ..."
        for i in xrange(0,len(self.network_configuration.mininet_obj.switches)) :
            mininet_switch = self.network_configuration.mininet_obj.switches[i]
            assert mininet_switch.name in self.switch_pids
            tracer_pid = self.switch_pids[mininet_switch.name]

            for name in mininet_switch.intfNames():
                if name != "lo" :
                    set_netdevice_owner(tracer_pid,name)

        for pid, host_name in self.host_pids:
            mininet_host = self.network_configuration.mininet_obj.get(host_name)
            assert mininet_host.name in self.host_pids
            tracer_pid = self.host_pids[mininet_host.name]
            for name in mininet_host.intfNames():
                if name != "lo" :
                    set_netdevice_owner(tracer_pid,name)

    def start_proxy_process(self):

        print "Starting Proxy Process at " + str(datetime.now())
        proxy_py_script = self.proxy_dir + "/proxy.py"
        proxy_log_file = self.log_dir + "/proxy_log.txt"
        core_proxy_start_cmd = "python " + str(proxy_py_script)
        proxy_start_cmd = core_proxy_start_cmd  + " -c " + self.node_mappings_file_path + " -l " + proxy_log_file + " -r " + str(self.run_time) + " -p " + self.power_simulator_ip + " -d " + str(self.control_node_id) + " &"
        os.system(proxy_start_cmd)

    def start_attack_orchestrator(self):
        print "Starting Attack orchestrator at " + str(datetime.now())

        if os.path.isdir(self.attack_plan_dir):
            attack_orchestrator_script = self.proxy_dir + "/attack_orchestrator.py"
            core_attk_orchestrator_cmd = "python " + str(attack_orchestrator_script)
            attk_orchestrator_start_cmd = core_attk_orchestrator_cmd + " -c " + self.attack_plan_dir + " -l " + self.node_mappings_file_path + " -r " + str(self.run_time + 2) + " &"
            proc = subprocess.Popen(attk_orchestrator_start_cmd, shell=True)

            print "Setting Attack orchestrator affinity to cores 0,1 ..."
            set_cpu_affinity(int(proc.pid))
            actual_attk_orchestrator_pids = get_pids_with_cmd(cmd=core_attk_orchestrator_cmd, expected_no_of_pids=1)
            set_cpu_affinity_pid_list(actual_attk_orchestrator_pids)

    def send_cmd_to_node(self,node_name,cmd) :
        mininet_host = self.network_configuration.mininet_obj.get(node_name)
        if mininet_host != None:
            mininet_host.cmd(cmd)

    def allow_icmp_requests(self):
        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            self.send_cmd_to_node(mininet_host.name,"sudo iptables -I OUTPUT -p icmp -j ACCEPT &")

    def allow_icmp_responses(self):
        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            self.send_cmd_to_node(mininet_host.name,"sudo iptables -I INPUT -p icmp -j ACCEPT &")

    def disable_TCP_RST(self):

        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            self.send_cmd_to_node(mininet_host.name,"sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j DROP")
        sleep(1)
        print "Attack Orchestrator: DISABLED TCP RST"

    def enable_TCP_RST(self):

        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            self.send_cmd_to_node(mininet_host.name,"sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j ACCEPT")
        print "Attack Orchestrator: ENABLED TCP RST"

    def open_main_cmd_channel_buffers(self):

        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            result = self.sharedBufferArray.open(bufName=str(mininet_host.name) + "main-cmd-channel-buffer", isProxy=True)
            if result == BUF_NOT_INITIALIZED or result == FAILURE:
                print "Shared Buffer open failed! Buffer not initialized for host: " + str(mininet_host.name)
                sys.exit(0)

        for edp in self.emulation_driver_params:
            result = self.sharedBufferArray.open(bufName=edp["driver_id"] + "main-cmd-channel-buffer", isProxy=True)
            if result == BUF_NOT_INITIALIZED or result == FAILURE:
                print "Shared Buffer open failed! Buffer not initialized for driver: " + edp["driver_id"]
                sys.exit(0)

        print "Opened Main channel buffers "

    def trigger_all_processes(self, trigger_cmd):
        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            ret = 0
            while ret <= 0:
                ret = self.sharedBufferArray.write(str(mininet_host.name) + "main-cmd-channel-buffer", trigger_cmd, 0)

        for edp in self.emulation_driver_params:
            ret = 0
            while ret <= 0 :
                ret = self.sharedBufferArray.write(edp["driver_id"] + "main-cmd-channel-buffer", trigger_cmd, 0)

        self.send_to_attack_orchestrator("START")
        print "NetPower: Triggered hosts, drivers and attack orchestrator with Command: ", trigger_cmd

    def send_to_attack_orchestrator(self, msg):
        ret = 0
        while ret <= 0:
            ret = self.sharedBufferArray.write("cmd-channel-buffer", msg, 0)

    def recv_from_attack_orchestrator(self):
        recv_msg = ''
        dummy_id, recv_msg = self.sharedBufferArray.read("cmd-channel-buffer")
        return recv_msg

    def run(self):

        if self.run_time > 0:
            print "########################################################################"
            print ""
            print "             Starting Experiment. Run time = ", self.run_time
            print ""
            print "########################################################################"

            # Before starting
            print "In Warm up phase waiting for pcaps to be loaded by all replay drivers ... "
            while True:
                recv_msg = self.recv_from_attack_orchestrator()
                if recv_msg == "PCAPS-LOADED":
                    break
                if self.enable_kronos == 1 :
                    progress_n_rounds(100)
                    n_rounds_progressed += 100
                else :
                    sleep(0.5)
            print "Attack Orchestrator: LOADED ALL PCAPS"

            if self.enable_kronos == 1 :
                start_time = get_current_virtual_time()
            else:
                start_time = time.time()
            self.trigger_all_processes("START")
            sys.stdout.flush()

            prev_time  = start_time
            run_time   = self.run_time

            #progress for 20ms which is the smallest timestep in powerworld
            if self.timeslice > 20*NS_PER_MS :
                n_rounds = 1
            else:
                n_rounds = int(20*NS_PER_MS/self.timeslice)


            k = 0
            while True:

                if self.enable_kronos == 1 :
                     curr_time = get_current_virtual_time_pid(self.switch_pids[0])
                     print "N rounds progressed = ", n_rounds_progressed, " Curr Virtual Time =", curr_time
                     sys.stdout.flush()
                     progress_n_rounds(n_rounds)
                     n_rounds_progressed += n_rounds

                     if k >= run_time :
                         sys.stdout.flush()
                         break
                     else :
                         if curr_time - prev_time >= 1.0 :
                             k = k + int(curr_time - prev_time)
                             print k," secs of virtual time elapsed. Real time = ", datetime.now()
                             sys.stdout.flush()
                             prev_time = curr_time
                else :
                    if k >= run_time :
                         break
                    k= k + 1
                    print k," secs of real time elapsed"
                    #sleep until runtime expires
                    time.sleep(0.5)

                recv_msg = self.recv_from_attack_orchestrator()
                if recv_msg == "START-REPLAY":
                    self.disable_TCP_RST()
                    self.send_to_attack_orchestrator("ACK")
                if recv_msg == "END-REPLAY":
                    self.enable_TCP_RST()
                    self.send_to_attack_orchestrator("ACK")

                if self.enable_kronos == 0 :
                    time.sleep(0.5)

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

        print "Roles assigned to the hosts:"
        host_index = 1
        for role in self.network_configuration.roles:
            print "h"+str(host_index), ":", role
            host_index += 1

        print ""
        print "########################################################################"

    


    def cleanup(self):

        #Clean up ...
        if self.enable_kronos == 1:
            self.stop_synchronized_experiment()
        else:
            self.trigger_all_processes("EXIT")
            time.sleep(10)

        print "Cleaning up ..."
        self.enable_TCP_RST()
        self.network_configuration.cleanup_mininet()

    def start_project(self):
        print "Starting project ..."
        self.print_topo_info()

        #General Startup ...
        self.generate_node_mappings(self.network_configuration.roles)
        self.start_host_processes()
        self.start_switch_processes()
        self.start_pkt_captures()
        self.start_proxy_process()
        self.start_attack_orchestrator()

        #Background related
        self.start_emulation_drivers()
        self.start_replay_drivers()

        #Kronos related
        if self.enable_kronos:

            self.set_netdevice_owners()
            self.start_synchronized_experiment()
            self.start_time = get_current_virtual_time()
        else:
            self.start_time = time.time()
            # if timekeeper is not enabled, restrict emulation/replay operations to cpu subset
            for pid in self.emulation_driver_pids: # *NEW*
                set_def_cpu_affinity(pid,self.cpus_subset)
            for pid in self.replay_driver_pids:
                set_def_cpu_affinity(pid,self.cpus_subset)
            for (pid,hostname) in self.host_pids:
                set_def_cpu_affinity(pid,self.cpus_subset)
            for pid in self.switch_pids:
                set_def_cpu_affinity(pid,self.cpus_subset)


        self.run()
        self.cleanup()




