"""Blank topology which may be used to build other topologies

.. moduleauthor:: Rakesh Kumar (gopchandani@gmail.com)
"""

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
        Topo.__init__(self)

    def build(self, *args, **params):
        """Build the topology here."""
        pass
