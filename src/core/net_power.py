import datetime
import shlex
from datetime import datetime
import time
from shared_buffer import *
from utils.sleep_functions import sleep
from utils.util_functions import *
from utils import tcpdump
from defines import *
from timekeeper_functions import *
import subprocess
import sys
import os


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
        self.host_pids = []
        self.switch_pids = []

        self.emulated_background_traffic_flows = emulated_background_traffic_flows
        self.emulated_network_scan_events = emulated_network_scan_events
        self.emulated_dnp3_traffic_flows = emulated_dnp3_traffic_flows

        self.node_mappings_file_path = self.script_dir + "/node_mappings.txt"
        self.log_dir = log_dir
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

        self.load_timekeeper()
        #if self.enable_timekeeper == 1 :
        #    set_cpu_affinity(int(os.getpid())
        
		


    def load_timekeeper(self) :
        if self.enable_timekeeper != None :
            print "Removing Timekeeper module"
            os.system("rmmod " + self.timekeeper_dir + "/build/TimeKeeper.ko")
            time.sleep(1)
            print"Inserting Timekeeper module"
            os.system("insmod " + self.timekeeper_dir + "/build/TimeKeeper.ko")
            time.sleep(1)

    def dilate_node(self,pid,tdf) :
        if pid != -1 and self.enable_timekeeper == 1 :
            dilate_all(pid,tdf)
            addToExp(pid) 
            sys.stdout.flush()

    def set_freeze_quantum(self):

        if self.tdf > 1 :
            timeslice = 1000000
        else:
            timeslice = 2000000
        set_cbe_experiment_timeslice(timeslice*self.tdf)
		

    def dilate_nodes(self) :

        print "Dilating all processes ... "
        time.sleep(1)
        mininet_obj = self.network_configuration.mininet_obj
        if self.enable_timekeeper == 1:
            for i in xrange(0,len(self.pid_list)):
                self.dilate_node(self.pid_list[i],self.tdf)
                pass

            print "########################################################################"
            print ""
            print "                        List of dilated pids"
            print  self.pid_list
            print ""
            print "########################################################################"
            print ""
            print "Number of dilated processes         = ", len(self.pid_list)
            print "Number of dilated tcpdump processes = ", self.n_dilated_tcpdump_procs
            print "Actual number of tcpdump processes  = ", self.n_actual_tcpdump_procs
            print "Number of hosts                     = ", len(self.network_configuration.roles)
            print "Number of switches                  = ", len(self.network_configuration.mininet_obj.switches)
            print ""
            print "########################################################################"
            print ""
            print "                        Host pids"
            print  self.host_pids
            print ""
            print "########################################################################" 
            print ""
            print "                        Switch pids"
            print  self.switch_pids
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
            self.start_time = get_current_virtual_time()
            startExp()
            print "Experiment start time", self.start_time, " local Time = " + str(datetime.now())
        else:
            self.start_time = time.time()
            print "Experiment started with TimeKeeper Disabled. Ignoring TDF settings ... "

    def stop_synchronized_experiment(self) :
        if self.enable_timekeeper == 1 :
            stopExp()
            print "Stopping synchronized experiment at local time = ", str(datetime.now())
            time.sleep(10)
            print "Stopped synchronized experiment"
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

    def start_host_reader_processes(self) :

        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            host_id = int(mininet_host.name[1:])
            host_role = self.node_mappings[mininet_host.name][1][0]

            #start reader process
            #reader_cmd = "sudo nice -5 su -c \'" + self.base_dir + "/src/core/bin/reader " + str(mininet_host.name)  + " " + self.log_dir + " >> " + self.log_dir + "/" + mininet_host.name + " 2>&1 &\'"

            reader_cmd =  self.base_dir + "/src/core/bin/reader " + str(mininet_host.name)  + " " + self.log_dir + " >> " + self.log_dir + "/" + mininet_host.name + " 2>&1 &"
            mininet_host.cmd(reader_cmd)

    def start_host_processes(self):
        print "Starting all Host Commands ..."
        self.start_host_reader_processes()
        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            self.pid_list.append(int(mininet_host.pid))
            self.host_pids.append(int(mininet_host.pid))
            host_id = int(mininet_host.name[1:])
            host_role = self.node_mappings[mininet_host.name][1][0]

            if "controller" not in host_role:
                host_log_file = self.log_dir + "/host_" + str(host_id) + "_log.txt"
            else:
                host_log_file = self.log_dir + "/controller_node_log.txt"


            if mininet_host.name == "h2" :
                host_py_script = self.proxy_dir + "/test.py"
            else:
                host_py_script = self.proxy_dir + "/host.py"
            cmd_to_run = "python " + str(host_py_script) + " -c " + self.node_mappings_file_path + " -l " + host_log_file + " -r " + str(self.run_time) + " -n " + str(self.project_name) + " -d " + str(host_id)

            if "controller" in host_role :
                cmd_to_run = cmd_to_run + " -i"
                self.control_node_id = host_id

            cmd_to_run = cmd_to_run + " >> " + host_log_file + " 2>&1" + " &"
            mininet_host.cmd(cmd_to_run)


    def start_switch_link_pkt_captures(self):
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
                set_cpu_affinity(int(proc.pid))	

            capture_cmd = "sudo " + core_cmd
 
            if mininet_link.intf1.name.startswith("s1-eth2")  :

                capture_log_file = self.log_dir  + "/" + mininet_link.intf2.name + "-" + mininet_link.intf1.name + ".pcap"
                with open(capture_log_file , "w") as f :
                    pass
				
                capture_cmd = capture_cmd + " -i "  + str(mininet_link.intf2.name)
                capture_cmd = capture_cmd + " -w " + capture_log_file + " -B 20000 ip & > /dev/null"
                self.n_actual_tcpdump_procs = self.n_actual_tcpdump_procs + 1

                proc = subprocess.Popen(capture_cmd, shell=True)
                self.tcpdump_procs.append(proc)
                set_cpu_affinity(int(proc.pid))
               
                
        
        time.sleep(2)
        # Get all the pids of actual tcpdump processes
        actual_tcpdump_pids = get_pids_with_cmd(core_cmd)
        #self.pid_list.extend(actual_tcpdump_pids)
        #self.n_dilated_tcpdump_procs = self.n_dilated_tcpdump_procs + len(actual_tcpdump_pids)
        
        # Get all the pids of sudo tcpdump parents
        sudo_tcpdump_parent_pids = get_pids_with_cmd("sudo " + core_cmd)
        set_cpu_affinity_pid_list(sudo_tcpdump_parent_pids) 
        

        for i in xrange(0,len(self.network_configuration.mininet_obj.switches)) :
            mininet_switch = self.network_configuration.mininet_obj.switches[i]
            self.switch_pids.append(int(mininet_switch.pid))
            self.pid_list.append(int(mininet_switch.pid))
            


    def set_switch_netdevice_owners(self) :
        print "Setting switch interface owner pids ..."
        for i in xrange(0,len(self.network_configuration.mininet_obj.switches)) :
            mininet_switch = self.network_configuration.mininet_obj.switches[i]
            for name in mininet_switch.intfNames():
                if name != "lo" :
                    set_netdevice_owner(mininet_switch.pid,name)
                
    

    def start_proxy_process(self):

        print "Starting Proxy Process at " + str(datetime.now())
        proxy_py_script = self.proxy_dir + "/proxy.py"
        proxy_log_file = self.log_dir + "/proxy_log.txt"
        core_proxy_start_cmd = "python " + str(proxy_py_script)
        proxy_start_cmd = core_proxy_start_cmd  + " -c " + self.node_mappings_file_path + " -l " + proxy_log_file + " -r " + str(self.run_time) + " -p " + self.power_simulator_ip + " -d " + str(self.control_node_id) + " &"
        os.system(proxy_start_cmd)
        

    def start_attack_dispatcher(self):
        print "Starting Attack Dispatcher at " + str(datetime.now())

        if os.path.isdir(self.replay_pcaps_dir):
            attack_dispatcher_script = self.proxy_dir + "/attack_orchestrator.py"
            core_attk_dispatcher_cmd = "python " + str(attack_dispatcher_script)
            attk_dispatcher_start_cmd = core_attk_dispatcher_cmd + " -c " + self.replay_pcaps_dir + " -l " + self.node_mappings_file_path + " -r " + str(self.run_time + 2) + " &"
            proc = subprocess.Popen(attk_dispatcher_start_cmd,shell=True) 
            
            print "Setting Attack Dispatcher affinity to cores 0,1 ..."
            set_cpu_affinity(int(proc.pid))
            actual_attk_dispatcher_pids = get_pids_with_cmd(core_attk_dispatcher_cmd)
            set_cpu_affinity_pid_list(actual_attk_dispatcher_pids)
            

    def send_cmd_to_node(self,node_name,cmd) :
        filename = "/tmp/" + node_name + "-reader"
        with open(filename,"w+") as f :
            f.write(cmd)

    def disable_TCP_RST(self):
        
        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            self.send_cmd_to_node(mininet_host.name,"sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j DROP &")
        print "DISABLED TCP RST"

    def enable_TCP_RST(self):
        
        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            self.send_cmd_to_node(mininet_host.name,"sudo iptables -I OUTPUT -p tcp --tcp-flags RST RST -j ACCEPT &")
        print "RE-ENABLED TCP RST"

    def run(self):

        
        if self.run_time > 0:
            print "Running Project for roughly (runtime + 2) =  " + str(self.run_time + 2) + " secs ..."
            sys.stdout.flush()
            start_time = get_current_virtual_time()
            prev_time  = start_time
            run_time   = self.run_time + 2

            k = 0		
            while True :

                if self.enable_timekeeper == 1 :
                     curr_time = get_current_virtual_time()

                     if curr_time - start_time >= run_time :					
                         break;
                     else :
                         if curr_time - prev_time >= 1.0 :
                             k = k + int(curr_time - prev_time)
                             print k," secs of virtual time elapsed"
                             sys.stdout.flush()
                             prev_time = curr_time
						

                else :
                    if k >= run_time :
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
                    sleep(0.05)
            except KeyboardInterrupt:
                print "Interrupted ..."

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
        
        #General Startup ...
        self.generate_node_mappings(self.network_configuration.roles)
        self.start_host_processes()
        self.start_switch_link_pkt_captures()
        self.start_proxy_process()
        self.start_attack_dispatcher()

        #TimeKeeper related ...
        self.set_switch_netdevice_owners()
        self.dilate_nodes()
        self.start_synchronized_experiment()

        #Background related ...
        self.start_emulated_traffic_threads()
        self.run()

        #Clean up ...
        self.stop_synchronized_experiment()
        self.stop_emulated_traffic_threads()

        print "Cleaning up ..."

        script_dir = os.path.dirname(os.path.realpath(__file__))
        with open(script_dir + "/dilate_pids.txt","w") as f :
            pass
        try:
            for proc in self.tcpdump_procs :
                print "terminating tcpdump proc ", proc.pid
                proc.terminate()

        except:
            pass

        os.system("sudo killall reader")
        self.network_configuration.cleanup_mininet()
