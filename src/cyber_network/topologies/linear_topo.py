"""Linear topology

.. moduleauthor:: Rakesh Kumar (gopchandani@gmail.com)
"""

import random
import logging

from mininet.topo import Topo

class CyberTopology(Topo):

    def __init__(self, params):
        """Initialization of topology

        :param params: A dictionary created from project_configuration.prototxt. It will contain all required
                       parameters "num_hosts", "num_switches", "switch_switch_link_latency_range"
                       and "host_switch_link_latency_range". In addition, any additional parameters defined
                       in configuration will also be included.
        :type params: dict
        """
        self.params = params

        if params["num_switches"] < 1 :
            logging.info("Need to have at least 2 switches for a linear topology.")
            raise Exception

        self.num_switches = params["num_switches"]
        self.total_switches = params["num_switches"]
        self.num_hosts_per_switch = params["num_hosts_per_switch"]


        if "switch_switch_link_latency_range" in params:
            switch_switch_link_opts = \
                dict(delay=str(float(random.uniform(*params["switch_switch_link_latency_range"]))) + "ms")
        else:
            switch_switch_link_opts = dict()

        if "host_switch_link_latency_range" in params:
            host_switch_link_opts = \
                dict(delay=str(float(random.uniform(*params["host_switch_link_latency_range"]))) + "ms")
        else:
            host_switch_link_opts = dict()

        self.switch_names = []
        self.host_names = []
        self.host_cntr = 1
        Topo.__init__(self)

    def build(self, *args, **params):
        print ("Building Linear Topology ...")

        last_switch = None
        for i in range(self.num_switches):
            curr_switch = self.addSwitch("s" + str(i + 1), protocols="OpenFlow14")
            self.switch_names.append(curr_switch)

            for j in range(self.num_hosts_per_switch) :
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
