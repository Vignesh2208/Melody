
import json
import os
import time
import subprocess
import datetime
import sys



sys.path.append("./")
from cyber_network.network_configuration import NetworkConfiguration
from cyber_network.traffic_flow import TrafficFlow
from cyber_network.traffic_flow import TRAFFIC_FLOW_PERIODIC, TRAFFIC_FLOW_EXPONENTIAL ,TRAFFIC_FLOW_ONE_SHOT
import Proxy.shared_buffer
from Proxy.shared_buffer import *
from Proxy.defines import *


class Main:

    def __init__(self, network_configuration):
        self.network_configuration = network_configuration

        # Dictionary containing mappings, keyed by the id of the mininet host
        # Value is a tuple -- (IP Address, Role)
        self.project_name = self.network_configuration.project_name
        self.run_time = self.network_configuration.run_time
        self.power_simulator_ip = self.network_configuration.power_simulator_ip
        self.node_mappings = {}
        self.control_node_id = None
        self.emulated_traffic_flows = []
        self.dnp3_emulated_traffic_flows = []

        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        idx = self.script_dir.index('NetPower_TestBed')
        self.base_dir = self.script_dir[0:idx] + "NetPower_TestBed"
        self.node_mappings_file_path = self.script_dir + "/node_mappings.txt"
        self.log_dir = self.base_dir + "/logs/" + str(self.project_name)
        self.proxy_dir = self.base_dir + "/src/Proxy"
        self.sharedBufferArray = shared_buffer_array()

        result = self.sharedBufferArray.open(bufName="cmd-channel-buffer",isProxy=False)
        if result == BUF_NOT_INITIALIZED or result == FAILURE:
            print "Cmd channel buffer open failed! "
            sys.exit(0)

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

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
	
	

    def start_dnp3_flow(self):
        self.dnp3_emulated_traffic_flows.extend([
			TrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                        offset=1,
                        inter_flow_period=2,
                        run_time=self.run_time,
                        src_mn_node=self.network_configuration.mininet_obj.get("h1"),
                        dst_mn_node=self.network_configuration.mininet_obj.get("h2"),
                        root_user_name="ubuntu",
                        root_password="ubuntu",
                        server_process_start_cmd='sudo python ' + self.base_dir + "/src/cyber_network/slave.py",
                        client_expect_file=self.base_dir + '/src/cyber_network/dnp3_master.expect',
                        long_running=True)
            
			
        ])
        for tf in self.dnp3_emulated_traffic_flows:
            tf.start()

        print "DNP3 traffic threads started..."


    def start_background_traffic(self):
        self.emulated_traffic_flows.extend([
            TrafficFlow(type=TRAFFIC_FLOW_PERIODIC,
                        offset=1,
                        inter_flow_period=1,
                        run_time=self.run_time,
                        src_mn_node=self.network_configuration.mininet_obj.get("h7"),
                        dst_mn_node=self.network_configuration.mininet_obj.get("h1"),
                        root_user_name="ubuntu",
                        root_password="ubuntu",
                        server_process_start_cmd="",
                        client_expect_file=self.base_dir + '/src/cyber_network/ping_session.expect'),

            TrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                        offset=5,
                        inter_flow_period=1,
                        run_time=self.run_time,
                        src_mn_node=self.network_configuration.mininet_obj.get("h7"),
                        dst_mn_node=self.network_configuration.mininet_obj.get("h1"),
                        root_user_name="ubuntu",
                        root_password="ubuntu",
                        server_process_start_cmd="/usr/sbin/sshd -D -o ListenAddress=" + self.network_configuration.mininet_obj.get("h1").IP(),
                        client_expect_file=self.base_dir + '/src/cyber_network/ssh_session.expect'),

            TrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                        offset=10,
                        inter_flow_period=2,
                        run_time=self.run_time,
                        src_mn_node=self.network_configuration.mininet_obj.get("h1"),
                        dst_mn_node=self.network_configuration.mininet_obj.get("h2"),
                        root_user_name="ubuntu",
                        root_password="ubuntu",
                        server_process_start_cmd="sudo socat tcp-l:23,reuseaddr,fork exec:/bin/login,pty,setsid,setpgid,stderr,ctty",
                        client_expect_file=self.base_dir + '/src/cyber_network/socat_session.expect'),

            TrafficFlow(type=TRAFFIC_FLOW_EXPONENTIAL,
                        offset=1,
                        inter_flow_period=self.run_time/2,
                        run_time=self.run_time,
                        src_mn_node=self.network_configuration.mininet_obj.get("h7"),
                        dst_mn_node=self.network_configuration.mininet_obj.get("h1"),
                        root_user_name="ubuntu",
                        root_password="ubuntu",
                        server_process_start_cmd="python -m SimpleHTTPServer",
                        client_expect_file=self.base_dir + '/src/cyber_network/http_session.expect'),

            TrafficFlow(type=TRAFFIC_FLOW_EXPONENTIAL,
                        offset=1,
                        inter_flow_period=self.run_time/2,
                        run_time=self.run_time,
                        src_mn_node=self.network_configuration.mininet_obj.get("h7"),
                        dst_mn_node=self.network_configuration.mininet_obj.get("h1"),
                        root_user_name="ubuntu",
                        root_password="ubuntu",
                        server_process_start_cmd="/usr/sbin/sshd -D -o ListenAddress=" + self.network_configuration.mininet_obj.get("h1").IP(),
                        client_expect_file=self.base_dir + '/src/cyber_network/ssh_session.expect')
        ])

        for tf in self.emulated_traffic_flows:
            tf.start()

        print "Background traffic threads started..."

    def start_host_processes(self):
        print "Starting all Host Commands ..."
        for i in xrange(len(self.network_configuration.roles)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
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
            print "Starting cmd for host: " + str(mininet_host.name) + " at " + str(datetime.datetime.now())
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




    def start_proxy_process(self):

        print "Starting Proxy Process at " + str(datetime.datetime.now())
        proxy_py_script = self.proxy_dir + "/proxy.py"
        proxy_log_file = self.log_dir + "/proxy_log.txt"
        #subprocess.Popen(['python',str(proxy_py_script),'-c',self.node_mappings_file_path,'-l',proxy_log_file,
        #                  '-r',str(self.run_time),'-p',self.power_simulator_ip,'-d', str(self.control_node_id)])
        os.system("python " + str(proxy_py_script) + " -c " + self.node_mappings_file_path + " -l " + proxy_log_file \
                 + " -r " + str(self.run_time) + " -p " + self.power_simulator_ip + " -d " + str(self.control_node_id) + " &")

    def start_attack_dispatcher(self):
        #print "Waiting for 5 secs for all processes to spawn up ..."
        #time.sleep(5)
        print "Starting Attack Dispatcher at " + str(datetime.datetime.now())
        replay_pcaps_dir = self.script_dir + "/pcaps"

        if os.path.isdir(replay_pcaps_dir) :
            attack_dispatcher_script = self.proxy_dir + "/attack_orchestrator.py"
            os.system("python " + str(attack_dispatcher_script) + " -c " + replay_pcaps_dir + " -l " + self.node_mappings_file_path + " -r " + str(self.run_time) + " &")


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
            start_time = time.time()
            while 1 :
                if time.time() - start_time >= self.run_time + 5.0:
                    break
                else:
                    recv_msg = ''
                    dummy_id, recv_msg = self.sharedBufferArray.read("cmd-channel-buffer")
                    if len(recv_msg) != 0:
                        if recv_msg == "START":
                            self.disable_TCP_RST()
                        if recv_msg == "END":
                            self.enable_TCP_RST()
                    time.sleep(0.5)
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
                    time.sleep(1)
            except KeyboardInterrupt:
                print "Interrupted ..."

    def start_project(self):
        print "Starting project ..."
        ng = self.network_configuration.setup_network_graph(mininet_setup_gap=1, synthesis_setup_gap=1)
        self.generate_node_mappings(self.network_configuration.roles)
        self.start_host_processes()
        self.start_switch_link_pkt_captures()
        self.start_proxy_process()
        #self.start_attack_dispatcher()
        self.start_background_traffic()
        self.start_dnp3_flow()
        self.run()

        print "Stopping project..."
        self.stop_project()

    def stop_project(self):

        # Join the threads for background processes to wait on them
        for tf in self.emulated_traffic_flows:
            tf.join()

        for tf in self.dnp3_emulated_traffic_flows:
            tf.join()


        print "Cleaning up ..."
        self.network_configuration.cleanup_mininet()


def main():

    network_configuration = NetworkConfiguration("ryu",
                                                  "127.0.0.1",
                                                 6633,
                                                 "http://localhost:8080/",
                                                 "admin",
                                                 "admin",
                                                 "clique_enterprise",
                                                 {"num_switches": 5,
                                                  "per_switch_links": 3,
                                                  "num_hosts_per_switch": 1,
                                                  #"switch_switch_link_latency_range": (40, 50),
                                                  #"host_switch_link_latency_range": (10, 20)
                                                  },
                                                 conf_root="configurations/",
                                                 synthesis_name="SimpleMACSynthesis",
                                                 synthesis_params={},
                                                 # Can map multiple power simulator objects to same cyber node.
                                                 roles=[
                                                         # internal field bus network. clique topology structure created only for this
                                                         ("controller_node",["control;1"]),
                                                         ("pilot_buses_set_1",["2","25","29"]),
                                                         ("pilot_buses_set_2",["22","23","19"]),
                                                         ("pilot_buses_set_3",["20","10","6", "9"]),
                                                         ("generator",["30;1","31;1","32;1","33;1","34;1","35;1","36;1","37;1","38;1","39;1"]),

                                                         # part of enterprise network. Linear topology which is attached to the clique at one switch
                                                         ("enterprise-1",["vpn-gateway;1"]),
                                                         ("enterprise-2",["attacker;1"])

                                                        ],                       
                                                 project_name="microgrid_with_background_traffic",
                                                 run_time=30,
                                                 power_simulator_ip="127.0.0.1"
                                                 )

    exp = Main(network_configuration)
    exp.start_project()

if __name__ == "__main__":
    main()
