__author__ = 'Rakesh Kumar'

import json
import networkx as nx

from collections import defaultdict
from itertools import permutations

from srcs.cyber_network.synthesis.switch import Switch
from srcs.cyber_network.synthesis.host import Host
from srcs.cyber_network.synthesis.flow_table import FlowTable
from srcs.cyber_network.synthesis.group_table import GroupTable
from srcs.cyber_network.synthesis.port import Port


class NetworkGraphLinkData(object):

    def __init__(self, node1_id, node1_port, node2_id, node2_port, link_type):
        self.link_ports_dict = {str(node1_id): node1_port, str(node2_id): node2_port}
        self.link_type = link_type
        self.traffic_paths = []
        self.causes_disconnect = None

        self.forward_port_graph_edge = (str(node1_id) + ':' + "egress" + str(node1_port),
                                        str(node2_id) + ':' + "ingress" + str(node2_port))

        self.reverse_port_graph_edge = (str(node2_id) + ':' + "egress" + str(node2_port),
                                        str(node1_id) + ':' + "ingress" + str(node1_port))

        self.forward_link = (str(node1_id), str(node2_id))
        self.reverse_link = (str(node2_id), str(node1_id))

    def __str__(self):
        return str(self.forward_link)

    def __eq__(self, other):
        return (self.forward_link == other.forward_link and self.reverse_link == other.reverse_link) or \
               (self.forward_link == other.reverse_link and self.reverse_link == other.forward_link)


class NetworkGraph(object):

    def __init__(self, network_configuration):

        self.network_configuration = network_configuration
        self.total_flow_rules = 0

        self.OFPP_CONTROLLER = 0xfffffffd
        self.OFPP_ALL = 0xfffffffc
        self.OFPP_IN = 0xfffffff8
        self.OFPP_NORMAL = 0xfffffffa

        self.GROUP_FF = "group-ff"
        self.GROUP_ALL = "group-all"

        # Initialize the self.graph
        self.graph = nx.Graph()

        # Initialize lists of host and switch ids
        self.host_ids = set()
        self.switch_ids = []

        self.controller = self.network_configuration.controller

    # Gets a switch-only multi-di-graph for the present topology
    def get_mdg(self):

        mdg = nx.MultiDiGraph(self.graph)

        for n in self.graph:
            node_type = self.get_node_type(n)

            # Remove all host nodes
            if node_type == "host":
                mdg.remove_node(n)

        return mdg

    def onos_sw_device_id_to_node_id_mapping(self, onos_node_id):
        node_id = "s" + str(int(onos_node_id.split(":")[1]))
        return node_id

    def node_id_to_onos_sw_device_id_mapping(self, node_id):
        id_num = node_id[1:]
        onos_sw_device_id = "of:" + id_num.zfill(16)
        return onos_sw_device_id

    def parse_onos_group_id(self, onos_group_id_str):
        tokens = onos_group_id_str.split("=")
        id_token = tokens[1][0:-1]
        return int(id_token, 16)

    def parse_mininet_host_nodes(self):

        mininet_host_nodes = None
        mininet_port_links = None

        with open(self.network_configuration.conf_path + "mininet_host_nodes.json", "r") as in_file:
            mininet_host_nodes = json.loads(in_file.read())

        with open(self.network_configuration.conf_path + "mininet_port_links.json", "r") as in_file:
            mininet_port_links = json.loads(in_file.read())

        for sw in mininet_host_nodes:

            # For every host
            for mininet_host_dict in mininet_host_nodes[sw]:

                host_switch_obj = self.get_node_object(mininet_host_dict["host_switch_id"])

                # Add the host to the graph
                self.host_ids.add(mininet_host_dict["host_name"])
                sw_obj = self.get_node_object(sw)

                #try:
                h_obj = Host(mininet_host_dict["host_name"],
                             self,
                             mininet_host_dict["host_IP"],
                             mininet_host_dict["host_MAC"],
                             host_switch_obj,
                             sw_obj.ports[mininet_port_links[mininet_host_dict["host_name"]]['0'][1]])


                # Make the connections both on switch and host side
                sw_obj.host_ports.append(mininet_port_links[mininet_host_dict["host_name"]]['0'][1])
                sw_obj.attached_hosts.append(h_obj)
                sw_obj.ports[mininet_port_links[mininet_host_dict["host_name"]]['0'][1]].attached_host = h_obj

                self.graph.add_node(mininet_host_dict["host_name"], node_type="host", h=h_obj)

    def parse_onos_host_nodes(self):
        onos_hosts = None

        with open(self.network_configuration.conf_path + "onos_hosts.json", "r") as in_file:
            onos_hosts = json.loads(in_file.read())

        for onos_host_dict in onos_hosts:
            host_switch_id = self.onos_sw_device_id_to_node_id_mapping(onos_host_dict["location"]["elementId"])
            host_switch_obj = self.get_node_object(host_switch_id)

            # Onos links do not give host-switch links, so need to add Port to each switch
            host_port_json = {"port": onos_host_dict["location"]["port"]}
            host_switch_port = Port(host_switch_obj, port_json=host_port_json)
            host_switch_obj.ports[int(host_switch_port.port_number)] = host_switch_port

            # Add the host to the graph
            host_id = "h" + host_switch_id[1:] + onos_host_dict["location"]["port"]
            self.host_ids.add(host_id)

            h_obj = Host(host_id,
                         self,
                         onos_host_dict["ipAddresses"][0],
                         onos_host_dict["mac"],
                         host_switch_obj,
                         host_switch_port)

            # Make the connections both on switch and host side
            host_switch_obj.host_ports.append(int(onos_host_dict["location"]["port"]))
            host_switch_obj.attached_hosts.append(h_obj)
            host_switch_port.attached_host = h_obj

            self.graph.add_node(host_id, node_type="host", h=h_obj)

            self.add_link(host_id,
                          int(0),
                          host_switch_id,
                          int(host_switch_port.port_number))

    def parse_host_nodes(self):
        if self.controller == "ryu":
            self.parse_mininet_host_nodes()
        elif self.controller == "onos":
            self.parse_onos_host_nodes()
        elif self.controller == "sel":
            raise NotImplementedError
        else:
            raise NotImplementedError

    def parse_mininet_links(self):

        mininet_port_links = None

        with open(self.network_configuration.conf_path + "mininet_port_links.json", "r") as in_file:
            mininet_port_links = json.loads(in_file.read())

        for src_node in mininet_port_links:
            for src_node_port in mininet_port_links[src_node]:
                dst_list = mininet_port_links[src_node][src_node_port]
                dst_node = dst_list[0]
                dst_node_port = dst_list[1]

                self.add_link(src_node,
                              int(src_node_port),
                              dst_node,
                              int(dst_node_port))

    def parse_onos_links(self):

        onos_links = None

        with open(self.network_configuration.conf_path + "onos_links.json", "r") as in_file:
            onos_links = json.loads(in_file.read())

        for link in onos_links:

            self.add_link(self.onos_sw_device_id_to_node_id_mapping(link["src"]["device"]),
                          int(link["src"]["port"]),
                          self.onos_sw_device_id_to_node_id_mapping(link["dst"]["device"]),
                          int(link["dst"]["port"]))

    def parse_links(self):
        if self.controller == "ryu":
            self.parse_mininet_links()
        elif self.controller == "onos":
            self.parse_onos_links()
        elif self.controller == "sel":
            raise NotImplementedError
        else:
            raise NotImplementedError

    def add_link(self, node1_id, node1_port, node2_id, node2_port):

        link_type = None

        if self.graph.node[node1_id]["node_type"] == "switch" and self.graph.node[node2_id]["node_type"] == "switch":
            link_type = "switch"
        elif self.graph.node[node1_id]["node_type"] == "host" and self.graph.node[node2_id]["node_type"] == "switch":
            link_type = "host"
        elif self.graph.node[node1_id]["node_type"] == "switch" and self.graph.node[node2_id]["node_type"] == "host":
            link_type = "host"
        else:
            raise Exception("Unknown Link Type")

        link_data = NetworkGraphLinkData(node1_id, node1_port, node2_id, node2_port, link_type)

        self.graph.add_edge(node1_id,
                            node2_id,
                            link_data=link_data)

        # Ensure that the ports are set up
        if self.graph.node[node1_id]["node_type"] == "switch":
            self.graph.node[node1_id]["sw"].ports[node1_port].state = "up"

        if self.graph.node[node2_id]["node_type"] == "switch":
            self.graph.node[node2_id]["sw"].ports[node2_port].state = "up"

    def remove_link(self, node1_id, node1_port, node2_id, node2_port):

        self.graph.remove_edge(node1_id, node2_id)

        if self.graph.node[node1_id]["node_type"] == "switch":
            self.graph.node[node1_id]["sw"].ports[node1_port].state = "down"

        if self.graph.node[node2_id]["node_type"] == "switch":
            self.graph.node[node2_id]["sw"].ports[node2_port].state = "down"

    def parse_ryu_switches(self):

        ryu_switches = None

        with open(self.network_configuration.conf_path + "ryu_switches.json", "r") as in_file:
            ryu_switches = json.loads(in_file.read())

        #  Go through each node and grab the ryu_switches and the corresponding hosts associated with the switch
        for dpid in ryu_switches:

            #  prepare a switch id
            switch_id = "s" + str(dpid)

            # Check to see if a switch with this id already exists in the graph,
            # if so grab it, otherwise create it
            sw = self.get_node_object(switch_id)
            if not sw:
                sw = Switch(switch_id, self)
                self.graph.add_node(switch_id, node_type="switch", sw=sw)
                self.switch_ids.append(switch_id)

            # Parse out the information about all the ports in the switch
            switch_ports = {}
            for port in ryu_switches[dpid]["ports"]:
                if port["port_no"] == 4294967294:
                    continue

                if port["port_no"] == "LOCAL":
                    continue

                switch_ports[int(port["port_no"])] = Port(sw, port_json=port)

            if (not ryu_switches[dpid]["ports"]):
                #import pdb; pdb.set_trace()
                ovs_sw = self.network_configuration.mininet_obj.get(switch_id)
                for intf in ovs_sw.intfList():
                    if intf.name != 'lo':
                        new_port_obj = Port(sw, None, intf)
                        switch_ports[new_port_obj.port_number] = new_port_obj

            sw.ports = switch_ports

            # Parse group table if one is available
            if "groups" in ryu_switches[dpid]:
                sw.group_table = GroupTable(sw, ryu_switches[dpid]["groups"])

            # Parse all the flow tables and sort them by table_id in the list
            switch_flow_tables = []
            for table_id in ryu_switches[dpid]["flow_tables"]:
                switch_flow_tables.append(FlowTable(sw, table_id, ryu_switches[dpid]["flow_tables"][table_id]))
                sw.flow_tables = sorted(switch_flow_tables, key=lambda flow_table: flow_table.table_id)

    def parse_onos_switches(self):

        onos_switches = None

        with open(self.network_configuration.conf_path + "onos_switches.json", "r") as in_file:
            onos_switches = json.loads(in_file.read())

        for onos_switch in onos_switches["devices"]:

            #  prepare a switch id
            switch_id = self.onos_sw_device_id_to_node_id_mapping(onos_switch["id"])

            # Check to see if a switch with this id already exists in the graph,
            # if so grab it, otherwise create it
            sw = self.get_node_object(switch_id)
            if not sw:
                sw = Switch(switch_id, self)
                self.graph.add_node(switch_id, node_type="switch", sw=sw)
                self.switch_ids.append(switch_id)

            # Parse out the information about all the ports in the switch
            switch_ports = {}
            for port_num in onos_switch["ports"]:
                switch_ports[int(port_num)] = Port(sw, port_json=onos_switch["ports"][port_num])

            sw.ports = switch_ports

            # Parse group table if one is available
            if "groups" in onos_switch:
                sw.group_table = GroupTable(sw, onos_switch["groups"])

            # Parse all the flow tables and sort them by table_id in the list
            switch_flow_tables = []
            for table_id in onos_switch["flow_tables"]:
                switch_flow_tables.append(FlowTable(sw, table_id, onos_switch["flow_tables"][table_id]))
                sw.flow_tables = sorted(switch_flow_tables, key=lambda flow_table: flow_table.table_id)

    def print_sel_flow_stats(self):
       # for each in OperationalTree.flowStatsHttpAccess(self.sel_session).read_collection():
       for each in OperationalTree.FlowStatsEntityAccess(self.sel_session).read_collection():
            print (each.to_pyson())

    def get_sel_switches(self):
       # nodes = OperationalTree.nodesHttpAccess(self.sel_session)
        nodes = ConfigTree.NodesEntityAccess(self.sel_session)
        sel_switches = {}
        for each in nodes.read_collection():
            this_switch = {}
            if each.linked_key.startswith("OpenFlow"):
                switch_id = each.linked_key.split(':')[1]

                #ports = OperationalTree.portsHttpAccess(self.sel_session)
                ports = OperationalTree.PortsEntityAccess(self.sel_session)
                sw_ports = []

                for port in ports.read_collection():
                    if isinstance(port, OperationalTree.OpenFlowPort):
                        if port.parent_node == each.linked_key:
                            sw_ports.append(port.to_pyson())

                this_switch["ports"] = sw_ports

              #  groups = ConfigTree.groupsHttpAccess(self.sel_session)
                groups = ConfigTree.GroupsEntityAccess(self.sel_session)

                sw_groups = []
                for group in groups.read_collection():
                    if group.node == each.id:
                        sw_groups.append(group.to_pyson())

                this_switch["groups"] = sw_groups

                #flow_tables = ConfigTree.flowsHttpAccess(self.sel_session)
                flow_tables = ConfigTree.FlowsEntityAccess(self.sel_session)
                switch_flow_tables = defaultdict(list)
                for flow_rule in flow_tables.read_collection():
                    if flow_rule.node == each.id:
                        flow_rule = flow_rule.to_pyson()
                        switch_flow_tables[flow_rule["tableId"]].append(flow_rule)

                this_switch["flow_tables"] = switch_flow_tables

                sel_switches[switch_id] = this_switch

        if self.network_configuration.save_config:
            with open(self.network_configuration.conf_path + "sel_switches.json", "w") as outfile:
                json.dump(sel_switches, outfile)

        return sel_switches

    def parse_sel_switches(self, sel_switches):
        for each_id, switch in sel_switches.iteritems():
            # prepare the switch id
            switch_id = "s" + str(each_id)

            sw = self.get_node_object(switch_id)
            # Check to see if a switch with this id already exists in the graph,
            # if so grab it, otherwise create it
            if not sw:
                sw = Switch(switch_id, self)
                self.graph.add_node(switch_id, node_type="switch", sw=sw)
                self.switch_ids.append(switch_id)
            # Parse out the information about all the ports in the switch
            switch_ports = {}
            for port in switch["ports"]:
                switch_ports[port["portId"]] = Port(sw, port_json=port)

            sw.ports = switch_ports

            # Parse group table if one is available
            if "groups" in sel_switches[each_id]:
                sw.group_table = GroupTable(sw, sel_switches[each_id]["groups"])

            # Parse all the flow tables and sort them by table_id in the list
            switch_flow_tables = []
            for table_id in sel_switches[each_id]["flow_tables"]:
                switch_flow_tables.append(FlowTable(sw, table_id,
                                                    sel_switches[each_id]["flow_tables"][table_id]))

            sw.flow_tables = sorted(switch_flow_tables, key=lambda flow_table: flow_table.table_id)

    def parse_switches(self):
        self.total_flow_rules = 0

        if self.network_configuration.controller == "ryu":
            self.parse_ryu_switches()
        elif self.network_configuration.controller == "onos":
            self.parse_onos_switches()
        elif self.network_configuration.controller == "sel":
            raise NotImplementedError
        else:
            raise NotImplementedError

    def parse_network_graph(self):

        self.parse_switches()
        self.parse_host_nodes()
        self.parse_links()

    def get_node_graph(self):
        return self.graph

    def get_switches(self):
        for switch_id in self.switch_ids:
            yield self.get_node_object(switch_id)

    def get_link_ports_dict(self, node1_id, node2_id):
        link_data = self.graph[node1_id][node2_id]['link_data']
        return link_data.link_ports_dict

    def get_link_data(self, node1_id, node2_id):
        link_data = self.graph[node1_id][node2_id]['link_data']
        return link_data

    def get_switch_link_data(self):
        for edge in self.graph.edges():
            link_data = self.graph[edge[0]][edge[1]]['link_data']
            if link_data.link_type == "switch":
                yield link_data

    def get_adjacent_switch_link_data(self, switch_id):
        for link_data in self.get_switch_link_data():
            if switch_id in link_data.link_ports_dict:

                adjacent_sw_id = None
                if switch_id == link_data.forward_link[0]:
                    adjacent_sw_id = link_data.forward_link[1]
                else:
                    adjacent_sw_id = link_data.forward_link[0]

                yield adjacent_sw_id, link_data

    def get_node_object(self, node_id):
        node_obj = None

        if self.graph.has_node(node_id):

            graph_node = self.graph.node[node_id]
            if graph_node["node_type"] == "switch":
                node_obj = graph_node["sw"]

            elif graph_node["node_type"] == "host":
                node_obj = graph_node["h"]

        return node_obj

    def get_node_type(self, node_id):
        node_type = None

        if self.graph.has_node(node_id):
            node_type = self.graph.node[node_id]["node_type"]

        return node_type

    def get_num_rules(self):

        num_rules = 0

        for sw in self.get_switches():
            for flow_table in sw.flow_tables:
                num_rules += len(flow_table.flows)

        return num_rules

    def host_obj_pair_iter(self):
        for host_id_pair in permutations(self.host_ids, 2):
            host_obj_pair = (self.get_node_object(host_id_pair[0]), self.get_node_object(host_id_pair[1]))
            yield host_obj_pair
