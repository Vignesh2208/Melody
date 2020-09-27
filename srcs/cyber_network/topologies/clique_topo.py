"""Sample clique topology

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
        
        if params["num_switches"] < 2:
            logging.info("Need to have at least three switches for a ring.")
            raise Exception

        if params["per_switch_links"] < 2 and params["per_switch_links"] > params["num_switches"] - 1:
            logging.info(
                "Cannot have less than 2 and more than %d links."
                %(params["num_switches"] -1))

        print ("Initializing Clique Topology ...")
        self.num_switches = params["num_switches"]
        self.total_switches = params["num_switches"]
        self.num_hosts_per_switch = params["num_hosts_per_switch"]
        self.per_switch_links = params["per_switch_links"]

        if "switch_switch_link_latency_range" in params:
            self.switch_switch_link_opts = \
                dict(delay=str(int(random.uniform(*params["switch_switch_link_latency_range"]))) + "ms")
        else:
            self.switch_switch_link_opts = dict()

        if "host_switch_link_latency_range" in params:
            self.host_switch_link_opts = \
                dict(delay=str(int(random.uniform(*params["host_switch_link_latency_range"]))) + "ms")
        else:
            self.host_switch_link_opts = dict()

        self.switch_names = []
        self.host_names = []
        self.host_cntr = 1

        Topo.__init__(self)

    def build(self, *args, **params):
        print ("Building Clique Topology ...")
        #  Add switches and hosts under them
        for i in range(self.num_switches):
            curr_switch = self.addSwitch("s" + str(i+1), protocols="OpenFlow14")
            self.switch_names.append(curr_switch)

            for j in range(self.num_hosts_per_switch):
                curr_host = self.addHost("h" + str(self.host_cntr))

                self.host_names.append(curr_host)
                self.host_cntr += 1
                self.addLink(curr_switch, curr_host, **self.host_switch_link_opts)

        #  Add links between switches
        for i in range(self.num_switches - 1):

            dst_switch_offsets = range(1, self.per_switch_links)
            for j in dst_switch_offsets:

                try:
                    l = self.g[self.switch_names[i]][self.switch_names[(i + j) % self.num_switches]]
                    print (l)
                except KeyError:

                    self.addLink(self.switch_names[i], self.switch_names[(i + j) % self.num_switches],
                                 **self.switch_switch_link_opts)

        #  Form a ring only when there are more than two switches
        self.addLink(self.switch_names[0], self.switch_names[-1], **self.switch_switch_link_opts)

    def __str__(self):
        params_str = ''
        for k, v in self.params.items():
            params_str += "_" + str(k) + "_" + str(v)
        return self.__class__.__name__ + params_str

