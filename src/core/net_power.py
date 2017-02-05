import time
import datetime
from datetime import datetime
from shared_buffer import *
from defines import *
from timekeeper_functions import *
import subprocess


class NetPower(object):

    def __init__(self,
                 run_time,
                 network_configuration,
                 script_dir,
                 base_dir,
                 replay_pcaps_dir,
                 log_dir,
                 emulated_background_traffic_flows,
                 emulated_network_scan_events,
                 emulated_dnp3_traffic_flows,
				 ENABLE_TIMEKEEPER,
				 TDF
		):

        self.network_configuration = network_configuration

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
        self.replay_pcaps_dir = replay_pcaps_dir
        self.pid_list = []

        self.emulated_background_traffic_flows = emulated_background_traffic_flows
        self.emulated_network_scan_events = emulated_network_scan_events
        self.emulated_dnp3_traffic_flows = emulated_dnp3_traffic_flows

        self.node_mappings_file_path = self.script_dir + "/node_mappings.txt"
        self.log_dir = log_dir
        self.proxy_dir = self.base_dir + "/src/core"
        self.sharedBufferArray = shared_buffer_array()

        result = self.sharedBufferArray.open(bufName="cmd-channel-buffer",isProxy=False)
        if result == BUF_NOT_INITIALIZED or result == FAILURE:
            print "Cmd channel buffer open failed! "
            sys.exit(0)

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.load_timekeeper()
        self.set_freeze_quantum()
		


    def load_timekeeper(self) :
        if self.enable_timekeeper == 1 :
            print "Removing Timekeeper module"
            os.system("rmmod " + self.timekeeper_dir + "/build/TimeKeeper.ko")
            time.sleep(1)
            print"Inseting Timekeeper module"
            os.system("insmod " + self.timekeeper_dir + "/build/TimeKeeper.ko")
            time.sleep(1)

    def dilate_node(self,pid,tdf) :
        if pid != -1 and self.enable_timekeeper == 1 :
            dilate_all(pid,tdf)
            addToExp(pid) 
            print "Added Host ", pid , " to synchronized experiment. TDF = ", self.tdf

    def set_freeze_quantum(self):
        timeslice = 10000000
        freeze_quantum = timeslice/2 		  # in nano seconds
        freeze_quantum = freeze_quantum/1000000
        set_cbe_experiment_timeslice(freeze_quantum*self.tdf)
		

    def dilate_nodes(self) :

        print "Dilating all nodes ... "
        mininet_obj = self.network_configuration.mininet_obj
        if self.enable_timekeeper == 1:
            for i in xrange(0,len(self.pid_list)):
                self.dilate_node(self.pid_list[i],self.tdf)
                pass

            print "List of dilated pids = ", self.pid_list
            script_dir = os.path.dirname(os.path.realpath(__file__))
            print "Writing to file : ", script_dir + "/dilate_pids.txt"
            with open(script_dir + "/dilate_pids.txt","w") as f :
                for i in xrange(0,len(self.pid_list)) :
                    f.write(str(self.pid_list[i]) + "\n")

    def start_synchronized_experiment(self) :

        if self.enable_timekeeper == 1 :
            print "Timekeeper synchronizing and freezing ..."
            synchronizeAndFreeze()
            time.sleep(2)
            self.start_time = get_current_virtual_time()
            startExp()
            print "Experiment start time", self.start_time, " local Time = " + str(datetime.now())
        else:
            self.start_time = time.time()
            print "Experiment started with TimeKeeper disabled. Ignoring TDF settings ... "

    def stop_synchronized_experiment(self) :
        if self.enable_timekeeper == 1 :
            stopExp()
            print "Stopping synchronized experiment at local time = ", str(datetime.now())
            time.sleep(20)
        else: 
            print "Stopping synchronized experiment at local time = ", str(datetime.now())
        
        
			
            

    def generate_node_mappings(self, roles):
        with open(self.node_mappings_file_path,"w") as outfile:
            for i in xrange(0,len(roles)):
                mininet_host = self.network_configuration.mininet_obj.hosts[i]
                self.node_mappings[mininet_host.name] = (mininet_host.IP(), roles[i],DEFAULT_HOST_UDP_PORT)
                lineTowrite = str(mininet_host.name) + "," + str(mininet_host.IP()) + "," + str(DEFAULT_HOST_UDP_PORT) + ","

                for j in xrange(0,len(roles[i][1])) :
                    if j < len(roles[i][1]) - 1 :
                        lineTowrite = lineTowrite + roles[i][1][j] + ","
                    else:
                        lineTowrite = lineTowrite + roles[i][1][j] + "\n"

                outfile.write(lineTowrite)

    def start_host_processes(self):
        print "Starting all Host Commands ..."
        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            print "PID of host ", i , " = ", mininet_host.pid
            self.pid_list.append(int(mininet_host.pid))
            host_id = int(mininet_host.name[1:])
            host_role = self.node_mappings[mininet_host.name][1][0]

            if "controller" not in host_role:
                host_log_file = self.log_dir + "/host_" + str(host_id) + "_log.txt"
            else:
                host_log_file = self.log_dir + "/controller_node_log.txt"

            host_py_script = self.proxy_dir + "/host.py"
            cmd_to_run = "python " + str(host_py_script) + " -c " + self.node_mappings_file_path + " -l " + host_log_file + " -r " + str(self.run_time) \
                         + " -n " + str(self.project_name) + " -d " + str(host_id)

            if "controller" in host_role :
                cmd_to_run = cmd_to_run + " -i"
                self.control_node_id = host_id

            cmd_to_run = cmd_to_run + " >> " + host_log_file + " 2>&1" + " &"
            print "Starting cmd for host: " + str(mininet_host.name) + " at " + str(datetime.now())
            mininet_host.cmd(cmd_to_run)

    def start_switch_link_pkt_captures(self):
        print "Starting wireshark capture on switches ..."

        for i in range(len(self.network_configuration.mininet_obj.links)):
            mininet_link = self.network_configuration.mininet_obj.links[i]
            switchIntfs = mininet_link.intf1
            capture_cmd = "sudo tcpdump"

            if mininet_link.intf1.name.startswith("s") and mininet_link.intf2.name.startswith("s") :

                capture_log_file = self.log_dir  + "/" + mininet_link.intf1.name + "-" + mininet_link.intf2.name + ".pcap"
                with open(capture_log_file , "w") as f :
                    pass

				
                capture_cmd = capture_cmd + " -i "  + str(switchIntfs.name)
                capture_cmd = capture_cmd + " -w " + capture_log_file + " &"
                os.system(capture_cmd)

                #proc = subprocess.Popen(["sudo tcpdump", "-i", str(switchIntfs.name),"-w", capture_log_file],shell=False)
                #print "TCP Dump pid  = ", proc.pid, " Interface = ", switchIntfs.name
                #self.pid_list.append(int(proc.pid))

    def start_proxy_process(self):

        print "Starting core Process at " + str(datetime.now())
        proxy_py_script = self.proxy_dir + "/proxy.py"
        proxy_log_file = self.log_dir + "/proxy_log.txt"
        #subprocess.Popen(['python',str(proxy_py_script),'-c',self.node_mappings_file_path,'-l',proxy_log_file,
        #                  '-r',str(self.run_time),'-p',self.power_simulator_ip,'-d', str(self.control_node_id)])
        os.system("python " + str(proxy_py_script) + " -c " + self.node_mappings_file_path + " -l " + proxy_log_file \
                  + " -r " + str(self.run_time) + " -p " + self.power_simulator_ip + " -d " + str(self.control_node_id) + " &")

    def start_attack_dispatcher(self):
        #print "Waiting for 5 secs for all processes to spawn up ..."
        #time.sleep(5)
        print "Starting Attack Dispatcher at " + str(datetime.now())


        #self.disable_TCP_RST()

        if os.path.isdir(self.replay_pcaps_dir):
            attack_dispatcher_script = self.proxy_dir + "/attack_orchestrator.py"
            os.system("python " + str(attack_dispatcher_script) + " -c " + self.replay_pcaps_dir + " -l " +
                      self.node_mappings_file_path + " -r " + str(self.run_time) + " &")

    def disable_TCP_RST(self):
        print "DISABLING TCP RST"
        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            mininet_host.cmd("sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j DROP ")

    def enable_TCP_RST(self):
        print "RE-ENABLING TCP RST"
        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            mininet_host.cmd("sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j ACCEPT ")

    def run(self):
        if self.run_time > 0:
            print "Running Project for roughly (runtime + 5) =  " + str(self.run_time + 5) + " secs ..."
            start_time = self.start_time
            prev_time  = self.start_time
            self.run_time = self.run_time + 5

            k = 0		
            while True :

                if self.enable_timekeeper == 1 :
                     curr_time = get_current_virtual_time()

                     if curr_time - start_time >= self.run_time :					
                         break;
                     else :
                         if curr_time - prev_time >= 1.0 :
                             k = k + (curr_time - prev_time)
                             print k," secs elapsed"
                             prev_time = curr_time
						

                else :
                    if k >= self.run_time :
                         break
                    k= k + 1
                    # sleep until runtime expires	
                    time.sleep(1)

                recv_msg = ''
                dummy_id, recv_msg = self.sharedBufferArray.read("cmd-channel-buffer")
                if len(recv_msg) != 0:
                    if recv_msg == "START":
                        self.disable_TCP_RST()
                    if recv_msg == "END":
                        self.enable_TCP_RST()
                time.sleep(0.05)
        else:
            print "Running Project forever. Press Ctrl-C to quit ..."
            try:
                while 1:
                    recv_msg = ''
                    dummy_id, recv_msg = self.sharedBufferArray.read("cmd-channel-buffer")
                    if len(recv_msg) != 0:
                        if recv_msg == "START" :
                            self.disable_TCP_RST()
                        if recv_msg == "END" :
                            self.enable_TCP_RST()
                    time.sleep(0.05)
            except KeyboardInterrupt:
                print "Interrupted ..."

    def print_topo_info(self):
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

    def start_emulated_traffic_threads(self):

        for tf in self.emulated_network_scan_events:
            tf.start()

        print "Network scan event threads started..."

        for tf in self.emulated_dnp3_traffic_flows:
            tf.start()

        print "DNP3 traffic threads started..."

        for tf in self.emulated_background_traffic_flows:
            tf.start()

        print "Background traffic threads started..."

    def stop_emulated_traffic_threads(self):

        # Join the threads for background processes to wait on them
        for tf in self.emulated_background_traffic_flows:
            tf.join()

        print "Network scan event threads stopped..."

        for tf in self.emulated_dnp3_traffic_flows:
            tf.join()

        print "DNP3 traffic threads stopped..."

        for tf in self.emulated_network_scan_events:
            tf.join()

        print "Background traffic threads stopped..."

    def start_project(self):
        print "Starting project ..."
        self.print_topo_info()

        self.generate_node_mappings(self.network_configuration.roles)
        self.start_host_processes()
        self.start_switch_link_pkt_captures()

        self.start_proxy_process()
        self.start_attack_dispatcher()

        self.start_emulated_traffic_threads()

        self.dilate_nodes()

        self.start_synchronized_experiment()

        self.run()

        self.stop_synchronized_experiment()

        self.stop_emulated_traffic_threads()

        print "Cleaning up ..."
        self.network_configuration.cleanup_mininet()
