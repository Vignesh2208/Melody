import json
import os
from cyber_network.network_configuration import NetworkConfiguration
from cyber_network.background_traffic import TrafficFlow, BackgroundTraffic
from Proxy.defines import *
import time
import subprocess
import datetime


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

        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        idx = self.script_dir.index('NetPower_TestBed')
        self.base_dir = self.script_dir[0:idx] + "NetPower_TestBed"
        self.node_mappings_file_path = self.script_dir + "/node_mappings.txt"
        self.log_dir = self.base_dir + "/logs/" + str(self.project_name)
        self.proxy_dir = self.base_dir + "/src/Proxy"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def generate_node_mappings(self, roles):
        with open(self.node_mappings_file_path,"w") as outfile:
            for i in xrange(0,len(self.network_configuration.mininet_obj.hosts)):
                mininet_host = self.network_configuration.mininet_obj.hosts[i]
                self.node_mappings[mininet_host.name] = (mininet_host.IP(), roles[i],DEFAULT_HOST_UDP_PORT)
                lineTowrite = str(mininet_host.name) + "," + str(mininet_host.IP()) + "," + str(DEFAULT_HOST_UDP_PORT) + ","

                for j in xrange(0,len(roles[i][1])) :
                    if j < len(roles[i][1]) - 1 :
                        lineTowrite = lineTowrite + roles[i][1][j] + ","
                    else:
                        lineTowrite = lineTowrite + roles[i][1][j] + "\n"

                outfile.write(lineTowrite)

        #with open('node_mappings.json', 'w') as outfile:
        #    json.dump(self.node_mappings, outfile)

    def start_background_traffic(self):
        traffic_flows = [TrafficFlow("poisson", 5, 1, "ssh", "h1", "h2")]
        bt = BackgroundTraffic(self.network_configuration.mininet_obj, traffic_flows, "ubuntu", "ubuntu", self.base_dir)

        bt.start()

    def start_host_processes(self):
        print "Starting all Host Commands ..."
        for i in range(len(self.network_configuration.mininet_obj.hosts)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            host_id = int(mininet_host.name[1:])
            host_role = self.node_mappings[mininet_host.name][1][0]
            if "controller" not in host_role:
                host_log_file = self.log_dir + "/host_" + str(host_id) + "_log.txt"
            else:
                host_log_file = self.log_dir + "/controller_node_log.txt"

            host_py_script = self.proxy_dir + "/host.py"
            cmd_to_run = "python " + str(host_py_script) + " -c " + self.node_mappings_file_path + " -l " + host_log_file + " -r " + str(self.run_time) \
                         + " -n " + str(self.project_name) + " -d " + str(host_id) + " &"

            if "controller" in host_role :
                cmd_to_run = cmd_to_run + " -i"
                self.control_node_id = host_id
            print "Starting cmd for host: " + str(mininet_host.name) + " at " + str(datetime.datetime.now())
            mininet_host.cmd(cmd_to_run)

    def start_proxy_process(self):

        print "Starting Proxy Process at " + str(datetime.datetime.now())
        proxy_py_script = self.proxy_dir + "/proxy.py"
        proxy_log_file = self.log_dir + "/proxy_log.txt"
        subprocess.Popen(['python',str(proxy_py_script),'-c',self.node_mappings_file_path,'-l',proxy_log_file,
                        '-r',str(self.run_time),'-p',self.power_simulator_ip,'-d', str(self.control_node_id)])
        #os.system("python " + str(proxy_py_script) + " -c " + self.node_mappings_file_path + " -l " + proxy_log_file \
        #         + " -r " + str(self.run_time) + " -p " + self.power_simulator_ip + " -d " + str(self.control_node_id))

    def run(self):
        if self.run_time > 0:
            print "Running Project for roughly (runtime + 5) =  " + str(self.run_time + 5) + " secs ..."
            time.sleep(self.run_time + 5)
        else:
            print "Running Project forever. Press Ctrl-C to quit ..."
            try:
                while 1:
                    time.sleep(1)
            except KeyboardInterrupt:
                print "Interrupted ..."

    def start_project(self):
        print "Starting project ..."
        ng = self.network_configuration.setup_network_graph(mininet_setup_gap=1, synthesis_setup_gap=1)
        self.generate_node_mappings(self.network_configuration.roles)

        self.start_background_traffic()

        self.start_host_processes()
        self.start_proxy_process()
        self.run()

        print "Stopping project..."
        self.stop_project()

    def stop_project(self):
        print "Cleaning up ..."
        self.network_configuration.cleanup_mininet()


def main():

    network_configuration = NetworkConfiguration("ryu",
                                                 "127.0.0.1",
                                                 6633,
                                                 "http://localhost:8080/",
                                                 "admin",
                                                 "admin",
                                                 "clique",
                                                 {"num_switches": 5,
                                                  "per_switch_links": 3,
                                                  "num_hosts_per_switch": 1,
                                                  "switch_switch_link_latency_range": (40, 100),
                                                  "host_switch_link_latency_range": (10, 20)
                                                  },
                                                 conf_root="configurations/",
                                                 synthesis_name="SimpleMACSynthesis",
                                                 synthesis_params={},
                                                 # Can map multiple power simulator objects to same cyber node.
                                                 roles=[
                                                         ("controller_node",["control;1"]),
                                                         ("operations_nodes",["operations;1","operations;2"]),
                                                         ("distribution_ieds",["distribution;1"]),
                                                         ("renewable_generator_ieds",["generator;1"]),
                                                         ("thermal_generator_ieds",["generator;2"])
                                                        ],
                                                 project_name="microgrid_with_background_traffic",
                                                 run_time=10,
                                                 power_simulator_ip="127.0.0.1"
                                                 )

    exp = Main(network_configuration)
    exp.start_project()

if __name__ == "__main__":
    main()
