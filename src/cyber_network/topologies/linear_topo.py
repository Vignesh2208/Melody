from mininet import topo
from mininet.topo import Topo
import random


class LinearTopo(Topo):

    def __init__(self, params):
        self.params = params
        Topo.__init__(self)

        if params["num_switches"] < 2:
            print "Need to have at least 2 switches for a linear topology."
            raise

        self.num_switches = params["num_switches"]
        self.total_switches = params["num_switches"]
        self.num_hosts_per_switch = params["num_hosts_per_switch"]


        if "switch_switch_link_latency_range" in params:
            switch_switch_link_opts = \
                dict(delay=str(int(random.uniform(*params["switch_switch_link_latency_range"]))) + "ms")
        else:
            switch_switch_link_opts = dict()

        if "host_switch_link_latency_range" in params:
            host_switch_link_opts = \
                dict(delay=str(int(random.uniform(*params["host_switch_link_latency_range"]))) + "ms")
        else:
            host_switch_link_opts = dict()

        self.switch_names = []
        self.host_names = []
        self.host_cntr = 1

        last_switch = None
        for i in xrange(self.num_switches):
            curr_switch = self.addSwitch("s" + str(i + 1), protocols="OpenFlow14")
            self.switch_names.append(curr_switch)

            for j in xrange(self.num_hosts_per_switch) :
                curr_host = self.addHost("h" + str(self.host_cntr))
                self.host_names.append(curr_host)
                self.host_cntr += 1
                self.addLink(curr_switch, curr_host, **host_switch_link_opts)

            if last_switch :
                self.addLink(curr_switch,last_switch,**switch_switch_link_opts)
            last_switch = curr_switch


    def __str__(self):
        params_str = ''
        for k, v in self.params.items():
            params_str += "_" + str(k) + "_" + str(v)
        return self.__class__.__name__ + params_str
