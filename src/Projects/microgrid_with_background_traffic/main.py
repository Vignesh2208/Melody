import json
from cyber_network.network_configuration import NetworkConfiguration


class Main:

    def __init__(self, network_configuration):
        self.network_configuration = network_configuration

        # Dictionary containing mappings, keyed by the id of the mininet host
        # Value is a tuple -- (IP Address, Role)

        self.node_mappings = {}

    def generate_node_mappings(self, roles):
        for i in range(len(self.network_configuration.mininet_obj.hosts)):
            mininet_host = self.network_configuration.mininet_obj.hosts[i]
            self.node_mappings[mininet_host.name] = (mininet_host.IP(), roles[i])

        with open('node_mappings.json', 'w') as outfile:
            json.dump(self.node_mappings, outfile)

    def start_project(self):
        ng = self.network_configuration.setup_network_graph(mininet_setup_gap=1, synthesis_setup_gap=1)

        self.generate_node_mappings(self.network_configuration.roles)

        print "Stopping project..."


def main():

    network_configuration = NetworkConfiguration("ryu",
                                                 "127.0.0.1",
                                                 6633,
                                                 "http://localhost:8080/",
                                                 "admin",
                                                 "admin",
                                                 "clique",
                                                 {"num_switches": 5,
                                                  "per_switch_links": 3,
                                                  "num_hosts_per_switch": 1,
                                                  "switch_switch_link_latency_range": (40, 100),
                                                  "host_switch_link_latency_range": (10, 20)
                                                  },
                                                 conf_root="configurations/",
                                                 synthesis_name="SimpleMACSynthesis",
                                                 synthesis_params={},
                                                 roles=["controller_node",
                                                        "operations_node",
                                                        "distribution_ied",
                                                        "renewable_generator_ied",
                                                        "thermal_generator_ied"])

    exp = Main(network_configuration)
    exp.start_project()

if __name__ == "__main__":
    main()
