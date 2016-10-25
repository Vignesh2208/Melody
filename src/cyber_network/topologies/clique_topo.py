__author__ = 'Rakesh Kumar'

from mininet.topo import Topo


class CliqueTopo(Topo):
    
    def __init__(self, params):
        
        Topo.__init__(self)

        if params["num_switches"] < 2:
            print "Need to have at least three switches for a ring."
            raise

        if params["per_switch_links"] < 2 and params["per_switch_links"] > params["num_switches"] - 1:
            print "Cannot have less than 2 and more than " + str(params["num_switches"] -1) + " links."

        self.num_switches = params["num_switches"]
        self.total_switches = params["num_switches"]
        self.num_hosts_per_switch = params["num_hosts_per_switch"]
        self.per_switch_links = params["per_switch_links"]
        self.switch_names = []
        self.host_names = []
        self.host_cntr = 1

        #  Add switches and hosts under them
        for i in xrange(self.num_switches):
            curr_switch = self.addSwitch("s" + str(i+1), protocols="OpenFlow14")
            self.switch_names.append(curr_switch)

            for j in xrange(self.num_hosts_per_switch):
                curr_host = self.addHost("h" + str(self.host_cntr))
                self.addLink(curr_switch, curr_host)
                self.host_names.append(curr_host)
                self.host_cntr += 1

        #  Add links between switches
        for i in xrange(self.num_switches - 1):

            dst_switch_offsets = xrange(1, self.per_switch_links)
            for j in dst_switch_offsets:

                try:
                    l = self.g[self.switch_names[i]][self.switch_names[(i + j) % self.num_switches]]
                    print l
                except KeyError:
                    self.addLink(self.switch_names[i], self.switch_names[(i + j) % self.num_switches])

        #  Form a ring only when there are more than two switches
        self.addLink(self.switch_names[0], self.switch_names[-1])

topos = {"cliquetopo": (lambda: CliqueTopo())}
