import datetime
import json
import os
import uuid
from datetime import datetime
from shared_buffer import *
from utils.sleep_functions import sleep
from utils.util_functions import *
from defines import *
from timekeeper_functions import *
import subprocess
import sys
import os
from fractions import gcd
import threading
from progress_timelines import *

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
                 emulated_network_scan_events,
                 emulated_dnp3_traffic_flows,
                 ENABLE_TIMEKEEPER,
                 TDF,
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
        self.enable_timekeeper = ENABLE_TIMEKEEPER
        self.tdf = TDF
        self.cpus_subset = CPUS_SUBSET 	# *NEW*

        self.attack_plan_dir = attack_plan_dir
        self.pid_list = []
        self.host_pids = []
        self.switch_pids = []
        self.emulation_driver_pids = []
        self.replay_driver_pids = []
        self.timeslice = self.get_timeslice()

        self.emulated_background_traffic_flows = emulated_background_traffic_flows
        self.emulated_network_scan_events = emulated_network_scan_events
        self.emulated_dnp3_traffic_flows = emulated_dnp3_traffic_flows

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
        self.load_timekeeper()

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

    def load_timekeeper(self) :
        if self.enable_timekeeper:
            print "Removing Timekeeper module"
            os.system("rmmod " + self.timekeeper_dir + "/build/TimeKeeper.ko")
            time.sleep(1)
            print"Inserting Timekeeper module"
            os.system("insmod " + self.timekeeper_dir + "/build/TimeKeeper.ko")
            time.sleep(1)

    def dilate_node(self,pid,tdf,timeline=-1) :
        if pid != -1 and self.enable_timekeeper == 1 :
            dilate_all(pid,tdf)
            addToExp(pid)
            sys.stdout.flush()

    def set_freeze_quantum(self):
        set_cbe_experiment_timeslice(self.timeslice*self.tdf)


    def dilate_nodes(self) :

        print "Dilating all processes ... "
        time.sleep(1)
        mininet_obj = self.network_configuration.mininet_obj

        if self.enable_timekeeper == 1:
            for i in xrange(0,len(self.pid_list)):
                self.dilate_node(self.pid_list[i],self.tdf)

            print "########################################################################"
            print ""
            print "                        List of dilated pids"
            print  self.pid_list
            print ""
            print "########################################################################"
            print ""
            print "Number of dilated processes         = ", len(self.pid_list)
            print "Number of tcpdump processes         = ", self.n_actual_tcpdump_procs
            print "Number of hosts                     = ", len(self.network_configuration.roles)
            print "Number of switches                  = ", len(self.network_configuration.mininet_obj.switches)
            print ""
            print "########################################################################"
            print ""
            print "                        Host pids"
            print self.host_pids
            print ""
            print "########################################################################"
            print ""
            print "                        Switch pids"
            print  self.switch_pids
            print ""
            print "########################################################################"
            print ""
            print "                     Emulated Driver pids"
            print  self.emulation_driver_pids
            print ""
            print "########################################################################"
            print ""
            print "                     Replay Driver pids"
            print  self.replay_driver_pids
            print ""
            print "########################################################################"
            print ""
            print "Timeslice = ", self.timeslice
            print ""
            print "########################################################################"


            script_dir = os.path.dirname(os.path.realpath(__file__))
            with open(script_dir + "/dilate_pids.txt","w") as f :
                for i in xrange(0,len(self.pid_list)) :
                    f.write(str(self.pid_list[i]) + "\n")
            sys.stdout.flush()

    def start_synchronized_experiment(self) :

        if self.enable_timekeeper == 1 :
            print "Timekeeper synchronizing and freezing ..."
            self.set_freeze_quantum()
            sys.stdout.flush()
            synchronizeAndFreeze()
            print "Sync and Freeze completed. Starting Exp ... "
            sys.stdout.flush()
            startExp()
            print "Experiment started: TDF = ", self.tdf, " local Time = " + str(datetime.now())

        else:
            self.start_time = time.time()
            print "Experiment started with TimeKeeper Disabled. Ignoring TDF settings ... "

    def stop_synchronized_experiment(self) :

        print "########################################################################"
        if self.enable_timekeeper == 1 :
            os.system("sudo killall -9 tcpdump")
            stopExp()
            print "Stopping synchronized experiment at local time = ", str(datetime.now())
            #time.sleep(10)
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

    def start_host_reader_processes(self) :

        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            host_id = int(mininet_host.name[1:])
            host_role = self.node_mappings[mininet_host.name][1][0]
            os.system("echo '' > " + self.log_dir + "/" + mininet_host.name)
            reader_cmd =  self.base_dir + "/src/core/bin/reader " + str(mininet_host.name)  + " " + self.log_dir + " >> " + self.log_dir + "/" + mininet_host.name + " 2>&1 &"

            #
            mininet_host.cmd(reader_cmd)


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

            cmd_to_run = cmd_to_run + " >> " + host_log_file + " 2>&1" + " &"
            mininet_host.cmd(cmd_to_run)

            pid = get_pids_with_cmd(cmd="python " + str(host_py_script) + " -l " + host_log_file, expected_no_of_pids=1)[0]

            self.host_pids.append((pid, mininet_host.name))
            self.pid_list.append(pid)

            #if self.enable_timekeeper == 1:
            set_cpu_affinity(mininet_host.pid)

            #if mininet_host.name == "h3" :
            #    mininet_host.cmd("sudo tcpdump -i h3-eth0 -w /home/user/Desktop/host.pcap &")

        #pid_list = get_pids_with_cmd(cmd="python " + str(host_py_script),expected_no_of_pids=len(self.network_configuration.roles))
        #assert len(pid_list)  == len(self.network_configuration.roles)

        # self.host_pids.extend(pid_list)
        # self.pid_list.extend(pid_list)

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

            if mininet_link.intf1.name.startswith("s") and mininet_link.intf2.name.startswith("s") :

                capture_log_file = self.log_dir  + "/" + mininet_link.intf1.name + "-" + mininet_link.intf2.name + ".pcap"
                with open(capture_log_file , "w") as f :
                    pass

                capture_cmd = capture_cmd + " -i "  + str(switchIntfs.name)
                capture_cmd = capture_cmd + " -w " + capture_log_file + " -B 20000 ip & > /dev/null"
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


        for i in xrange(0,len(self.network_configuration.mininet_obj.switches)) :
            mininet_switch = self.network_configuration.mininet_obj.switches[i]
            self.switch_pids.append(int(mininet_switch.pid))
            self.pid_list.append(int(mininet_switch.pid))

    def set_switch_netdevice_owners(self) :
        pid = 0
        print "Setting switch interface owner pids ..."
        for i in xrange(0,len(self.network_configuration.mininet_obj.switches)) :
            mininet_switch = self.network_configuration.mininet_obj.switches[i]
            if i == 0:
                pid_master = mininet_switch.pid

            pid_master = int(self.pid_list[0])

            for name in mininet_switch.intfNames():
                if name != "lo" :
                    #set_netdevice_owner(mininet_switch.pid,name)
                    set_netdevice_owner(pid_master,name)

        for pid, host_name in self.host_pids:
            mininet_host = self.network_configuration.mininet_obj.get(host_name)
            for name in mininet_host.intfNames():
                if name != "lo" :
                    #set_netdevice_owner(pid, name)
                    set_netdevice_owner(pid_master,name)

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
            while True:
                recv_msg = self.recv_from_attack_orchestrator()
                if recv_msg == "PCAPS-LOADED":
                    break
                sleep(0.5)
            print "Attack Orchestrator: LOADED ALL PCAPS"

            if self.enable_timekeeper == 1 :
                start_time = get_current_virtual_time_pid(self.switch_pids[0])
            else:
                start_time = time.time()
            self.trigger_all_processes("START")
            sys.stdout.flush()

            prev_time  = start_time
            run_time   = self.run_time

            n_rounds_progressed = 0
            #progress for 20ms which is the smallest timestep in powerworld
            if self.timeslice > 20*NS_PER_MS :
                n_rounds = 1
            else:
                n_rounds = int(20*NS_PER_MS/self.timeslice)


            k = 0
            while True:

                if self.enable_timekeeper == 1 :
                     curr_time = get_current_virtual_time_pid(self.switch_pids[0])
                     #print "N rounds progressed = ", n_rounds_progressed, " Time =", curr_time
                     sys.stdout.flush()
                     progress_exp_cbe(n_rounds)
                     n_rounds_progressed += n_rounds



                     if k >= run_time :
                         sys.stdout.flush()
                         break
                     else :
                         if curr_time - prev_time >= 1.0 :
                             k = k + int(curr_time - prev_time)
                             print k," secs of virtual time elapsed. Local time = ", datetime.now()
                             sys.stdout.flush()
                             prev_time = curr_time
                else :
                    if k >= run_time :
                         break
                    k= k + 1
                    print k," secs of real time elapsed"
                    # sleep until runtime expires
                    time.sleep(0.5)

                recv_msg = self.recv_from_attack_orchestrator()
                if recv_msg == "START-REPLAY":
                    self.disable_TCP_RST()
                    self.send_to_attack_orchestrator("ACK")
                if recv_msg == "END-REPLAY":
                    self.enable_TCP_RST()
                    self.send_to_attack_orchestrator("ACK")
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

    def start_emulation_drivers(self):

        n_drivers = 0
        driver_py_script = self.proxy_dir + "/emulation_driver.py"

        for edp in self.emulation_driver_params:

            mininet_host = self.network_configuration.mininet_obj.get(edp["node_id"])
            driver_log_file = self.log_dir + "/" + str(edp["driver_id"]) + "_log.txt"

            input_params_file_path = self.log_dir + "/" + edp["driver_id"] + ".json"
            with open(input_params_file_path, "w") as f:
                json.dump(edp, f)

            cmd_to_run = "python " + str(driver_py_script) + " --input_params_file_path " + input_params_file_path
            cmd_to_run = cmd_to_run + " > " + driver_log_file + " 2>&1" + " &"

            mininet_host.cmd(cmd_to_run)
            n_drivers = n_drivers + 1

        print "Waiting for emulation drivers to start. Number of drivers = ", n_drivers
        pid_list = get_pids_with_cmd(cmd="python " + str(driver_py_script), expected_no_of_pids=n_drivers)
        assert len(pid_list) == n_drivers
        self.emulation_driver_pids.extend(pid_list)
        self.pid_list.extend(pid_list)
        print "All emulation drivers started"

    def stop_emulation_drivers(self):
        for pid in self.emulation_driver_pids:
            try:
                os.system("sudo kill " + str(pid))
            except:
                pass

    def start_replay_drivers(self):

        n_drivers = 0
        driver_py_script = self.proxy_dir + "/replay_driver.py"

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

            cmd_to_run = "python " + str(driver_py_script) + " --input_params_file_path " + input_params_file_path
            cmd_to_run = cmd_to_run + " > " + driver_log_file + " 2>&1" + " &"

            mininet_host.cmd(cmd_to_run)
            n_drivers += 1

        pid_list = get_pids_with_cmd(cmd="python " + str(driver_py_script), expected_no_of_pids=n_drivers)
        assert len(pid_list) == n_drivers
        self.replay_driver_pids.extend(pid_list)
        self.pid_list.extend(pid_list)

    def stop_replay_drivers(self):
        for pid in self.replay_driver_pids:
            try:
                os.system("sudo kill " + str(pid))
            except:
                pass

    def cleanup(self):

        #Clean up ...
        if self.enable_timekeeper:
            resume_exp_cbe()
            self.stop_synchronized_experiment()
        else:
            self.trigger_all_processes("EXIT")
            time.sleep(10)

        self.stop_emulation_drivers()

        print "Cleaning up ..."
        self.enable_TCP_RST()
        script_dir = os.path.dirname(os.path.realpath(__file__))
        with open(script_dir + "/dilate_pids.txt","w") as f :
            pass
        try:
            for proc in self.tcpdump_procs :
                print "terminating tcpdump proc ", proc.pid
                proc.terminate()

        except:
            pass

        for pid, host_name in self.host_pids:
            os.system("sudo kill -9 " + str(pid))
        for pid in self.emulation_driver_pids:
            os.system("sudo kill -9 " + str(pid))
        for pid in self.replay_driver_pids:
            os.system("sudo kill -9 " + str(pid))

        try:
            os.system("sudo killall reader")
        except:
            pass

        self.network_configuration.cleanup_mininet()
        #os.system("sudo killall -9 python")

    def start_project(self):
        print "Starting project ..."
        self.print_topo_info()

        #General Startup ...
        self.generate_node_mappings(self.network_configuration.roles)
        self.start_host_processes()
        self.start_pkt_captures()
        self.start_proxy_process()
        self.start_attack_orchestrator()

        #Background related
        self.start_emulation_drivers()
        self.start_replay_drivers()

        #TimeKeeper related
        if self.enable_timekeeper:

            self.set_switch_netdevice_owners()
            self.dilate_nodes()
            self.start_synchronized_experiment()
            self.start_time = get_current_virtual_time_pid(self.switch_pids[0])
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




