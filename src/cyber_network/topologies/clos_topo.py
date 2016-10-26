__author__ = 'Rakehs Kumar'

from mininet.topo import Topo


class ClosTopo(Topo):

    def __init__(self, params):
        
        # Initialize topology and default options
        Topo.__init__(self)

        self.params = params

        self.total_core_switches = self.params["core"]
        self.total_agg_switches = self.total_core_switches * self.params["fanout"]
        self.total_edge_switches = self.total_agg_switches * self.params["fanout"]

        self.total_switches = 0

        self.core_switches = {}
        self.agg_switches = {}
        self.edge_switches = {}

        for x in xrange(1, self.total_core_switches + 1):
            self.total_switches += 1
            self.core_switches[x] = self.addSwitch('s%i' % self.total_switches, protocols="OpenFlow14")
            
        print "Core switches:", self.core_switches
        
        for x in xrange(1, self.total_agg_switches + 1):
            self.total_switches += 1
            self.agg_switches[x] = self.addSwitch('s%i' % self.total_switches, protocols="OpenFlow14")
            
        print "Aggregate switches:", self.agg_switches

        for x in self.core_switches:
            for y in self.agg_switches:
                self.addLink(self.core_switches[x], self.agg_switches[y])

        for x in xrange(1, self.total_edge_switches + 1):
            self.total_switches += 1
            edge_switch_name = 's%i' % self.total_switches
            self.edge_switches[x] = self.addSwitch('s%i' % self.total_switches, protocols="OpenFlow14")
            
        print "Edge switches:",  self.edge_switches

        for x in self.agg_switches:
            for y in self.edge_switches:
                self.addLink(self.agg_switches[x], self.edge_switches[y])

        for edge_switch_num in self.edge_switches:
            edge_switch_name = self.edge_switches[edge_switch_num]
            for y in xrange(self.params["num_hosts_per_switch"]):
                host_name = self.addHost("h" + edge_switch_name[1:] + str(y+1))
                self.addLink(host_name, self.edge_switches[edge_switch_num])

    def get_switches_with_hosts(self):
        return self.edge_switches.keys()

    def __str__(self):
        params_str = ''
        for k, v in self.params.items():
            params_str += "_" + str(k) + "_" + str(v)
        return self.__class__.__name__ + params_str
