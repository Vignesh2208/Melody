__author__ = 'Rakesh Kumar'

from collections import defaultdict


class Switch:

    def __init__(self, sw_id, network_graph):

        self.node_id = sw_id
        self.network_graph = network_graph
        self.attached_hosts = []
        self.flow_tables = []
        self.group_table = None
        self.ports = None
        self.host_ports = []

        # Synthesis stuff
        self.intents = defaultdict(dict)
        try:
            self.synthesis_tag = int(self.node_id[1:])
        except ValueError:
            self.synthesis_tag = self.node_id

        # Analysis stuff
        self.port_graph = None

    def non_host_port_iter(self):
        for port_num in self.ports:
            if port_num not in self.host_ports:
                yield self.ports[port_num]

    def host_port_iter(self):
        for port_num in self.host_ports:
            yield self.ports[port_num]
