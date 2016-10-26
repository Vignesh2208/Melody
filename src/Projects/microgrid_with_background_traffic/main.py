
from cyber_network.network_configuration import NetworkConfiguration


class Main:

    def __init__(self, network_configuration):
        self.network_configuration = network_configuration

    def start_project(self):
        ng = self.network_configuration.setup_network_graph(mininet_setup_gap=1, synthesis_setup_gap=1)
        print "Done..."


def main():

    # network_configuration = NetworkConfiguration("ryu",
    #                                              "127.0.0.1",
    #                                              6633,
    #                                              "http://localhost:8080/",
    #                                              "admin",
    #                                              "admin",
    #                                              "clique",
    #                                              {"num_switches": 5,
    #                                               "per_switch_links": 3,
    #                                               "num_hosts_per_switch": 1},
    #                                              conf_root="configurations/",
    #                                              synthesis_name="AboresceneSynthesis",
    #                                              synthesis_params={"apply_group_intents_immediately": True})
    #

    network_configuration = NetworkConfiguration("ryu",
                                                 "127.0.0.1",
                                                 6633,
                                                 "http://localhost:8080/",
                                                 "admin",
                                                 "admin",
                                                 "clique",
                                                 {"num_switches": 5,
                                                  "per_switch_links": 3,
                                                  "num_hosts_per_switch": 1},
                                                 conf_root="configurations/",
                                                 synthesis_name="SimpleMACSynthesis",
                                                 synthesis_params={})

    exp = Main(network_configuration)
    exp.start_project()

if __name__ == "__main__":
    main()
