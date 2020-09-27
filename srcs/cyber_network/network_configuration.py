"""Network configuration object

.. moduleauthor:: Rakesh Kumar (gopchandani@gmail.com)
"""

import json
import httplib2
import subprocess
import logging
import os
import sys
import time

from itertools import permutations
from collections import defaultdict
from functools import partial
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.node import OVSSwitch
from mininet.node import OVSKernelSwitch
from mininet.link import TCLink

import mininet.cli
from srcs.cyber_network.controller_man import ControllerMan
from srcs.cyber_network.synthesis.network_graph import NetworkGraph
from srcs.cyber_network.synthesis.match import Match
from srcs.cyber_network.synthesis.simple_mac_synthesis import SimpleMACSynthesis
from srcs.cyber_network.synthesis.synthesis_lib import SynthesisLib
from srcs.cyber_network.synthesis.flow_specification import FlowSpecification


CLI = None

#setLogLevel('debug')


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
                 project_name="test"):

        self.controller = controller
        self.topo_name = topo_name
        self.topo_params = topo_params
        self.topo_name = topo_name
        self.conf_root = conf_root
        self.synthesis_name = synthesis_name
        self.synthesis_params = synthesis_params
        self.roles = roles
        self.project_name = project_name

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

        topo_class_file = os.path.dirname(os.path.realpath(__file__)) + "/topologies/" + self.topo_name + ".py"

        if not os.path.isfile(topo_class_file):
            raise NotImplementedError("Topology: %s" % self.topo_name)

        topo_cls = __import__("srcs.cyber_network.topologies.%s" %self.topo_name, globals(), locals(),
                              ['CyberTopology'], 0)
        self.topo = topo_cls.CyberTopology(self.topo_params)

    def init_synthesis(self):
        self.synthesis = SimpleMACSynthesis(self.synthesis_params)

    def prepare_all_flow_specifications(self):

        flow_specs = []
        flow_match = Match(is_wildcard=True)
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
        self.synthesis.network_graph = self.ng
        self.synthesis.synthesis_lib = SynthesisLib("localhost", "8181", self.ng)
        flow_specs = self.prepare_all_flow_specifications()
        self.synthesis.synthesize_flow_specifications(flow_specs)

        if synthesis_setup_gap:
            time.sleep(synthesis_setup_gap)

    def get_ryu_switches(self):
        ryu_switches = {}
        # Get all the ryu_switches from the inventory API
        remaining_url = 'stats/switches'
        resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")
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
                logging.error("Error pulling switch flows from RYU.")

            # Get the ports
            remaining_url = 'stats/portdesc' + "/" + str(dpid)
            resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

            if resp["status"] == "200":
                switch_ports = json.loads(content)
                this_ryu_switch["ports"] = switch_ports[str(dpid)]
            else:
                logging.error("Error pulling switch ports from RYU.")

            # Get the groups
            remaining_url = 'stats/groupdesc' + "/" + str(dpid)
            resp, content = self.h.request(self.controller_api_base_url + remaining_url, "GET")

            if resp["status"] == "200":
                switch_groups = json.loads(content)
                this_ryu_switch["groups"] = switch_groups[str(dpid)]
            else:
                logging.error("Error pulling switch ports from RYU.")

            ryu_switches[dpid] = this_ryu_switch

        with open(self.conf_path + "ryu_switches.json", "w") as outfile:
            json.dump(ryu_switches, outfile)

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

    def get_host_nodes(self):
        if self.controller == "ryu":
            self.get_mininet_host_nodes()
        else:
            raise NotImplementedError

    def get_mininet_links(self):
        mininet_port_links = {}
        with open(self.conf_path + "mininet_port_links.json", "w") as outfile:
            json.dump(self.topo.ports, outfile)

        return mininet_port_links

    def get_links(self):
        if self.controller == "ryu":
            self.get_mininet_links()
        else:
            raise NotImplementedError

    def get_switches(self):
        if self.controller == "ryu":
            self.get_ryu_switches()
        else:
            raise NotImplementedError

    def setup_network_graph(self, mininet_setup_gap=None, synthesis_setup_gap=None):

        if not self.load_config and self.save_config:

            if self.controller == "ryu":

                self.cm = ControllerMan(controller=self.controller)
                self.cm.start_controller()
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
        else:
            self.ng = NetworkGraph(network_configuration=self)
            self.ng.parse_network_graph()

        return self.ng

    def start_mininet(self):

        self.cleanup_mininet()

        if self.controller == "ryu":
            self.mininet_obj = Mininet(topo=self.topo,
                                       cleanup=True,
                                       autoStaticArp=True,
                                       autoSetMacs=True,
                                       link=TCLink,
                                       controller=RemoteController("ryu", ip=self.controller_ip, port=self.controller_port),
                                       switch=partial(OVSSwitch, protocols="OpenFlow14"))
            self.mininet_obj.start()
           

    def cleanup_mininet(self):

        if self.mininet_obj:
            logging.info("Melody >> Cleaning up mininet ...")
            clean_up_cmd = ["sudo", "mn", "-c"]
            p = subprocess.Popen(clean_up_cmd)
            p.wait()

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



