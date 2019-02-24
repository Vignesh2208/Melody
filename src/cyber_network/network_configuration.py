__author__ = 'Rakesh Kumar'

import time
import os
import json
import httplib2
import fcntl
import struct
from socket import *

from mininet.cli import CLI

from itertools import permutations
from collections import defaultdict
from functools import partial
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.node import OVSSwitch
from mininet.link import TCLink
from controller_man import ControllerMan
from src.cyber_network.synthesis.network_graph import NetworkGraph
from src.cyber_network.synthesis.match import Match

from src.cyber_network.topologies.ring_topo import RingTopo
from src.cyber_network.topologies.clos_topo import ClosTopo
from src.cyber_network.topologies.linear_topo import LinearTopo
from src.cyber_network.topologies.clique_topo import CliqueTopo
from src.cyber_network.topologies.clique_enterprise_topo import CliqueEnterpriseTopo

from src.cyber_network.synthesis.dijkstra_synthesis import DijkstraSynthesis
from src.cyber_network.synthesis.aborescene_synthesis import AboresceneSynthesis
from src.cyber_network.synthesis.simple_mac_synthesis import SimpleMACSynthesis
from src.cyber_network.synthesis.synthesis_lib import SynthesisLib
from src.cyber_network.synthesis.flow_specification import FlowSpecification
import subprocess

from core.kronos_helper_functions import *

class NetworkConfiguration(object):

    def __init__(self,
                 controller,
                 controller_ip,
                 controller_port,
                 controller_api_base_url,
                 controller_api_user_name,
                 controller_api_password,
                 topo_name,
                 topo_params,
                 conf_root,
                 synthesis_name,
                 synthesis_params,
                 roles,
                 project_name="test",
                 power_simulator_ip="127.0.0.1",
                 link_latency=""):

        self.controller = controller
        self.topo_name = topo_name
        self.topo_params = topo_params
        self.topo_name = topo_name
        self.conf_root = conf_root
        self.synthesis_name = synthesis_name
        self.synthesis_params = synthesis_params
        self.roles = roles
        self.project_name = project_name
        self.power_simulator_ip = power_simulator_ip
        self.link_latency = link_latency

        self.controller_ip = controller_ip
        self.controller_port = controller_port
        self.topo = None
        self.nc_topo_str = None
        self.init_topo()
        self.init_synthesis()

        self.mininet_obj = None
        self.cm = None
        self.ng = None

        # Setup the directory for saving configs, check if one does not exist,
        # if not, assume that the controller, cyber_network and rule synthesis needs to be triggered.
        self.conf_path = self.conf_root + str(self) + "/"
        if not os.path.exists(self.conf_path):
            os.makedirs(self.conf_path)
            self.load_config = False
            self.save_config = True
        else:
            self.load_config = False
            self.save_config = True

        self.h = httplib2.Http()
        self.controller_api_base_url = controller_api_base_url
        self.controller_api_base_url = controller_api_base_url
        self.h.add_credentials(controller_api_user_name, controller_api_password)

    def __str__(self):
        return self.controller + "_" + str(self.synthesis) + "_" + str(self.topo)

    def __del__(self):
        self.cm.stop_controller()
        self.cleanup_mininet()

    def init_topo(self):
        if self.topo_name == "ring":
            self.topo = RingTopo(self.topo_params)
            self.nc_topo_str = "Ring topology with " + str(self.topo.total_switches) + " switches"
        elif self.topo_name == "clostopo":
            self.topo = ClosTopo(self.topo_params)
            self.nc_topo_str = "Clos topology with " + str(self.topo.total_switches) + " switches"
        elif self.topo_name == "linear":
            self.topo = LinearTopo(self.topo_params)
            self.nc_topo_str = "Linear topology with " + str(self.topo_params["num_switches"]) + " switches"
        elif self.topo_name == "clique":
            self.topo = CliqueTopo(self.topo_params)
            self.nc_topo_str = "Linear topology with " + str(self.topo_params["num_switches"]) + " switches"
        elif self.topo_name == "clique_enterprise" :
            self.topo = CliqueEnterpriseTopo(self.topo_params)
            self.nc_topo_str = "Clique Enterprise topology with " + str(self.topo_params["num_switches"]) + " switches"
        else:

            raise NotImplementedError("Topology: %s" % self.topo_name)

    def init_synthesis(self):
        if self.synthesis_name == "DijkstraSynthesis":
            self.synthesis_params["master_switch"] = self.topo_name == "linear"
            self.synthesis = DijkstraSynthesis(self.synthesis_params)

        elif self.synthesis_name == "AboresceneSynthesis":
            self.synthesis = AboresceneSynthesis(self.synthesis_params)
        elif self.synthesis_name == "SimpleMACSynthesis":
            self.synthesis = SimpleMACSynthesis(self.synthesis_params)
        else:
            self.synthesis = None

    def prepare_all_flow_specifications(self):

        flow_specs = []

        flow_match = Match(is_wildcard=True)
        #flow_match["ethernet_type"] = 0x0800

        for src_host_id, dst_host_id in permutations(self.ng.host_ids, 2):

            if src_host_id == dst_host_id:
                continue

            fs = FlowSpecification(src_host_id, dst_host_id, flow_match)
            fs.ng_src_host = self.ng.get_node_object(src_host_id)
            fs.ng_dst_host = self.ng.get_node_object(dst_host_id)
            fs.mn_src_host = self.mininet_obj.get(src_host_id)
            fs.mn_dst_host = self.mininet_obj.get(dst_host_id)

            flow_specs.append(fs)

        return flow_specs

    def trigger_synthesis(self, synthesis_setup_gap):

        if self.synthesis_name == "DijkstraSynthesis":
            self.synthesis.network_graph = self.ng
            self.synthesis.synthesis_lib = SynthesisLib("localhost", "8181", self.ng)
            self.synthesis.synthesize_all_node_pairs()

        elif self.synthesis_name == "AboresceneSynthesis":
            self.synthesis.network_graph = self.ng
            self.synthesis.synthesis_lib = SynthesisLib("localhost", "8181", self.ng)
            flow_match = Match(is_wildcard=True)
            flow_match["ethernet_type"] = 0x0800
            self.synthesis.synthesize_all_switches(flow_match, 2)

        elif self.synthesis_name == "SimpleMACSynthesis":
            self.synthesis.network_graph = self.ng
            self.synthesis.synthesis_lib = SynthesisLib("localhost", "8181", self.ng)
            flow_specs = self.prepare_all_flow_specifications()
            self.synthesis.synthesize_flow_specifications(flow_specs)

        if synthesis_setup_gap:
            time.sleep(synthesis_setup_gap)

        if self.mininet_obj:
            #self.mininet_obj.pingAll()

            # full_data = self.mininet_obj.pingFull(hosts=[self.mininet_obj.get('h1'),
            #                                              self.mininet_obj.get('h2')])
            # print full_data

            """
            h1 = self.mininet_obj.get('h1')
            h2 = self.mininet_obj.get('h2')

            s1 = self.mininet_obj.get('s1')

            cmd = "ping -c3 " + h2.IP()
            output = h1.cmd(cmd)

            macAddr = os.popen("ifconfig -a s1-eth1 | grep HWaddr | awk -F \' \' \'{print $5}\'").read().rstrip('\n')
            #macAddr = str(proc.stdout.read())
            os.system("sudo tcprewrite --enet-smac=" + str(macAddr) + " --infile=/home/ubuntu/Desktop/Workspace/NetPower_TestBed/test.pcap --outfile=/home/ubuntu/Desktop/Workspace/NetPower_TestBed/test2.pcap")

            cmd = "sudo tcpreplay -i s1-eth1 /home/ubuntu/Desktop/Workspace/NetPower_TestBed/test2.pcap"
            os.system(cmd)
            #output = h1.cmd(cmd)

            print "here"
            """



    def get_ryu_switches(self):
        ryu_switches = {}

        # Get all the ryu_switches from the inventory API
        remaining_url = 'stats/switches'
        resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

        #CLI(self.mininet_obj)

        #import pdb; pdb.set_trace()



        ryu_switch_numbers = json.loads(content)

        for dpid in ryu_switch_numbers:

            this_ryu_switch = {}

            # Get the flows
            remaining_url = 'stats/flow' + "/" + str(dpid)
            resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

            if resp["status"] == "200":
                switch_flows = json.loads(content)
                switch_flow_tables = defaultdict(list)
                for flow_rule in switch_flows[str(dpid)]:
                    switch_flow_tables[flow_rule["table_id"]].append(flow_rule)
                this_ryu_switch["flow_tables"] = switch_flow_tables
            else:
                print "Error pulling switch flows from RYU."

            # Get the ports
            remaining_url = 'stats/portdesc' + "/" + str(dpid)
            resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

            if resp["status"] == "200":
                switch_ports = json.loads(content)
                this_ryu_switch["ports"] = switch_ports[str(dpid)]
            else:
                print "Error pulling switch ports from RYU."

            # Get the groups
            remaining_url = 'stats/groupdesc' + "/" + str(dpid)
            resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

            if resp["status"] == "200":
                switch_groups = json.loads(content)
                this_ryu_switch["groups"] = switch_groups[str(dpid)]
            else:
                print "Error pulling switch ports from RYU."

            ryu_switches[dpid] = this_ryu_switch

        with open(self.conf_path + "ryu_switches.json", "w") as outfile:
            json.dump(ryu_switches, outfile)

    def get_onos_switches(self):

        # Get all the onos_switches from the inventory API
        remaining_url = 'devices'
        resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

        onos_switches = json.loads(content)

        for this_switch in onos_switches["devices"]:

            # Get the flows
            remaining_url = 'flows' + "/" + this_switch["id"]
            resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

            if resp["status"] == "200":
                switch_flows = json.loads(content)
                switch_flow_tables = defaultdict(list)
                for flow_rule in switch_flows["flows"]:
                    switch_flow_tables[flow_rule["tableId"]].append(flow_rule)
                this_switch["flow_tables"] = switch_flow_tables
            else:
                print "Error pulling switch flows from Onos."

            # Get the ports

            remaining_url = "links?device=" + this_switch["id"]
            resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

            if resp["status"] == "200":
                switch_links = json.loads(content)["links"]
                this_switch["ports"] = {}
                for link in switch_links:
                    if link["src"]["device"] == this_switch["id"]:
                        this_switch["ports"][link["src"]["port"]] = link["src"]
                    elif link["dst"]["device"] == this_switch["id"]:
                        this_switch["ports"][link["dst"]["port"]] = link["dst"]
            else:
                print "Error pulling switch ports from RYU."

            # Get the groups
            remaining_url = 'groups' + "/" + this_switch["id"]
            resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

            if resp["status"] == "200":
                this_switch["groups"] = json.loads(content)["groups"]
            else:
                print "Error pulling switch ports from RYU."

        with open(self.conf_path + "onos_switches.json", "w") as outfile:
            json.dump(onos_switches, outfile)

    def get_mininet_host_nodes(self):

        mininet_host_nodes = {}

        for sw in self.topo.switches():
            mininet_host_nodes[sw] = []
            for h in self.get_all_switch_hosts(sw):
                mininet_host_dict = {"host_switch_id": "s" + sw[1:],
                                     "host_name": h.name,
                                     "host_IP": h.IP(),
                                     "host_MAC": h.MAC()}

                mininet_host_nodes[sw].append(mininet_host_dict)

        with open(self.conf_path + "mininet_host_nodes.json", "w") as outfile:
            json.dump(mininet_host_nodes, outfile)

        return mininet_host_nodes

    def get_onos_host_nodes(self):

        # Get all the onos_hosts from the inventory API
        remaining_url = 'hosts'
        resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

        onos_hosts = json.loads(content)["hosts"]

        with open(self.conf_path + "onos_hosts.json", "w") as outfile:
            json.dump(onos_hosts, outfile)

        return onos_hosts

    def get_host_nodes(self):
        if self.controller == "ryu":
            self.get_mininet_host_nodes()
        elif self.controller == "onos":
            self.get_onos_host_nodes()
        else:
            raise NotImplemented

    def get_mininet_links(self):

        mininet_port_links = {}

        with open(self.conf_path + "mininet_port_links.json", "w") as outfile:
            json.dump(self.topo.ports, outfile)

        return mininet_port_links

    def get_onos_links(self):
        # Get all the onos_links from the inventory API
        remaining_url = 'links'
        resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

        onos_links = json.loads(content)["links"]

        with open(self.conf_path + "onos_links.json", "w") as outfile:
            json.dump(onos_links, outfile)

        return onos_links

    def get_links(self):
        if self.controller == "ryu":
            self.get_mininet_links()
        elif self.controller == "onos":
            self.get_onos_links()
        else:
            raise NotImplementedError

    def get_switches(self):
        # Now the output of synthesis is carted away
        if self.controller == "ryu":
            self.get_ryu_switches()
        elif self.controller == "onos":
            self.get_onos_switches()
        else:
            raise NotImplementedError

    def setup_network_graph(self, mininet_setup_gap=None, synthesis_setup_gap=None):

        if not self.load_config and self.save_config:

            if self.controller == "ryu":

                self.cm = ControllerMan(controller=self.controller)
                self.cm.start_controller()

                #time.sleep(mininet_setup_gap)
                self.start_mininet()
                if mininet_setup_gap:
                    time.sleep(mininet_setup_gap)

            # These things are needed by network graph...
            self.get_switches()
            self.get_host_nodes()
            self.get_links()

            self.ng = NetworkGraph(network_configuration=self)
            self.ng.parse_network_graph()

            if self.synthesis_name:

                # Now the synthesis...
                self.trigger_synthesis(synthesis_setup_gap)

                # Refresh just the switches in the network graph, post synthesis
                self.get_switches()
                self.ng.parse_network_graph()
                #self.ng.parse_switches()

        else:
            self.ng = NetworkGraph(network_configuration=self)
            self.ng.parse_network_graph()

        print "total_flow_rules:", self.ng.total_flow_rules

        return self.ng

    def start_mininet(self):

        self.cleanup_mininet()

        if self.controller == "ryu":
            self.mininet_obj = Mininet(topo=self.topo,
                                       cleanup=True,
                                       autoStaticArp=True,
                                       autoSetMacs=True,
                                       link=TCLink,
                                       controller=lambda name: RemoteController(name,
                                                                                ip=self.controller_ip,
                                                                                port=self.controller_port),
                                       switch=partial(OVSSwitch, protocols='OpenFlow13'))

            self.mininet_obj.start()

    def cleanup_mininet(self):

        if self.mininet_obj:
            print "Mininet cleanup..."
            #self.mininet_obj.stop()

        os.system("sudo mn -c")

    def get_all_switch_hosts(self, switch_id):

        p = self.topo.ports

        for node in p:

            # Only look for this switch's hosts
            if node != switch_id:
                continue

            for switch_port in p[node]:
                dst_list = p[node][switch_port]
                dst_node = dst_list[0]
                if dst_node.startswith("h"):
                    yield self.mininet_obj.get(dst_node)

    def get_mininet_hosts_obj(self):
        for sw in self.topo.switches():
            for h in self.get_all_switch_hosts(sw):
                yield h

    def is_host_pair_pingable(self, src_host, dst_host):
        hosts = [src_host, dst_host]
        ping_loss_rate = self.mininet_obj.ping(hosts, '1')

        # If some packets get through, then declare pingable
        if ping_loss_rate < 100.0:
            return True
        else:
            # If not, do a double check:
            cmd_output = src_host.cmd("ping -c 3 " + dst_host.IP())
            print cmd_output
            if cmd_output.find("0 received") != -1:
                return False
            else:
                return True

    def are_all_hosts_pingable(self):
        ping_loss_rate = self.mininet_obj.pingAll('1')

        # If some packets get through, then declare pingable
        if ping_loss_rate < 100.0:
            return True
        else:
            return False

    def get_intf_status(self, ifname):

        # set some symbolic constants
        SIOCGIFFLAGS = 0x8913
        null256 = '\0'*256

        # create a socket so we have a handle to query
        s = socket(AF_INET, SOCK_DGRAM)

        # call ioctl() to get the flags for the given interface
        result = fcntl.ioctl(s.fileno(), SIOCGIFFLAGS, ifname + null256)

        # extract the interface's flags from the return value
        flags, = struct.unpack('H', result[16:18])

        # check "UP" bit and print a message
        up = flags & 1

        return ('down', 'up')[up]

    def wait_until_link_status(self, sw_i, sw_j, intended_status):

        num_seconds = 0

        for link in self.mininet_obj.links:
            if (sw_i in link.intf1.name and sw_j in link.intf2.name) or (sw_i in link.intf2.name and sw_j in link.intf1.name):

                while True:
                    status_i = self.get_intf_status(link.intf1.name)
                    status_j = self.get_intf_status(link.intf2.name)

                    if status_i == intended_status and status_j == intended_status:
                        break

                    time.sleep(1)
                    num_seconds +=1

        return num_seconds

    def is_bi_connected_manual_ping_test(self, experiment_host_pairs_to_check, edges_to_try=None):

        is_bi_connected= True

        if not edges_to_try:
            edges_to_try = self.topo.g.edges()

        for edge in edges_to_try:

            # Only try and break switch-switch edges
            if edge[0].startswith("h") or edge[1].startswith("h"):
                continue

            for (src_host, dst_host) in experiment_host_pairs_to_check:

                is_pingable_before_failure = self.is_host_pair_pingable(src_host, dst_host)

                if not is_pingable_before_failure:
                    print "src_host:", src_host, "dst_host:", dst_host, "are not connected."
                    is_bi_connected = False
                    break

                self.mininet_obj.configLinkStatus(edge[0], edge[1], 'down')
                self.wait_until_link_status(edge[0], edge[1], 'down')
                time.sleep(5)
                is_pingable_after_failure = self.is_host_pair_pingable(src_host, dst_host)
                self.mininet_obj.configLinkStatus(edge[0], edge[1], 'up')
                self.wait_until_link_status(edge[0], edge[1], 'up')

                time.sleep(5)
                is_pingable_after_restoration = self.is_host_pair_pingable(src_host, dst_host)

                if not is_pingable_after_failure == True:
                    is_bi_connected = False
                    print "Got a problem with edge:", edge, " for src_host:", src_host, "dst_host:", dst_host
                    break

        return is_bi_connected

    def is_bi_connected_manual_ping_test_all_hosts(self,  edges_to_try=None):

        is_bi_connected = True

        if not edges_to_try:
            edges_to_try = self.topo.g.edges()

        for edge in edges_to_try:

            # Only try and break switch-switch edges
            if edge[0].startswith("h") or edge[1].startswith("h"):
                continue

            is_pingable_before_failure = self.are_all_hosts_pingable()

            if not is_pingable_before_failure:
                is_bi_connected = False
                break

            self.mininet_obj.configLinkStatus(edge[0], edge[1], 'down')
            self.wait_until_link_status(edge[0], edge[1], 'down')
            time.sleep(5)
            is_pingable_after_failure = self.are_all_hosts_pingable()
            self.mininet_obj.configLinkStatus(edge[0], edge[1], 'up')
            self.wait_until_link_status(edge[0], edge[1], 'up')

            time.sleep(5)
            is_pingable_after_restoration = self.are_all_hosts_pingable()

            if not is_pingable_after_failure == True:
                is_bi_connected = False
                break

        return is_bi_connected

    def parse_iperf_output(self, iperf_output_string):
        data_lines =  iperf_output_string.split('\r\n')
        interesting_line_index = None
        for i in xrange(len(data_lines)):
            if data_lines[i].endswith('Server Report:'):
                interesting_line_index = i + 1
        data_tokens =  data_lines[interesting_line_index].split()
        print "Transferred Rate:", data_tokens[7]
        print "Jitter:", data_tokens[9]

    def parse_ping_output(self,ping_output_string):

        data_lines =  ping_output_string.split('\r\n')
        interesting_line_index = None
        for i in xrange(len(data_lines)):
            if data_lines[i].startswith('5 packets transmitted'):
                interesting_line_index = i + 1
        data_tokens =  data_lines[interesting_line_index].split()
        data_tokens =  data_tokens[3].split('/')
        print 'Min Delay:', data_tokens[0]
        print 'Avg Delay:', data_tokens[1]
        print 'Max Delay:', data_tokens[2]




