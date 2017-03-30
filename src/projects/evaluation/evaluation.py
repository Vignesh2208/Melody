import random
import sys

sys.path.append("./")
from cyber_network.network_configuration import NetworkConfiguration
from cyber_network.traffic_flow import EmulatedTrafficFlow
from cyber_network.traffic_flow import TRAFFIC_FLOW_ONE_SHOT, TRAFFIC_FLOW_PERIODIC
from core.core import Core

from core.shared_buffer import *


class Evaluation:

    def __init__(self,
                 run_time,
                 network_configurations,
                 script_dir,
                 base_dir,
                 replay_pcaps_dir,
                 background_specs):

        self.run_time = run_time
        self.network_configurations = network_configurations
        self.script_dir = script_dir
        self.base_dir = base_dir
        self.replay_pcaps_dir = replay_pcaps_dir
        self.background_specs = background_specs

    def configure(self, network_configuration, run_time, base_dir, background_spec, evaluation_type):

        emulated_background_traffic_flows = []
        emulated_network_scan_events = []

        if evaluation_type == "replay":
            with open(self.replay_pcaps_dir + "/attack_plan.txt", "w") as attack_plan_file:
                attack_plan_file.write("dnp3.pcap\n")

            emulated_dnp3_traffic_flows = []

        elif evaluation_type == "emulation":

            with open(self.replay_pcaps_dir + "/attack_plan.txt", "w") as attack_plan_file:
                attack_plan_file.write("#dnp3.pcap\n")

            emulated_dnp3_traffic_flows = [
                EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                                    offset=1,
                                    inter_flow_period=2,
                                    run_time=run_time,
                                    src_mn_node=network_configuration.mininet_obj.get("h1"),
                                    dst_mn_node=network_configuration.mininet_obj.get("h2"),
                                    root_user_name="ubuntu",
                                    root_password="ubuntu",
                                    server_process_start_cmd='sudo python ' + base_dir + "/src/cyber_network/dnp3_slave.py",
                                    client_expect_file=base_dir + '/src/cyber_network/dnp3_master.expect',
                                    long_running=True)]

        random_host_pairs = random.sample(list(network_configuration.ng.host_obj_pair_iter()), background_spec)

        for host_pair in random_host_pairs:

            print "ping, from", host_pair[0].node_id, "to:", host_pair[1].node_id

            flow = EmulatedTrafficFlow(type=TRAFFIC_FLOW_PERIODIC,
                                       offset=1,
                                       inter_flow_period=1,
                                       run_time=run_time,
                                       src_mn_node=network_configuration.mininet_obj.get(host_pair[0].node_id),
                                       dst_mn_node=network_configuration.mininet_obj.get(host_pair[1].node_id),
                                       root_user_name="ubuntu",
                                       root_password="ubuntu",
                                       server_process_start_cmd="",
                                       client_expect_file=base_dir + '/src/cyber_network/ping_session.expect')

            emulated_background_traffic_flows.append(flow)

        return emulated_background_traffic_flows, emulated_network_scan_events, emulated_dnp3_traffic_flows

    def trigger(self, evaluation_type):
        for nc in self.network_configurations:

            for spec in self.background_specs:

                nc.setup_network_graph(mininet_setup_gap=1, synthesis_setup_gap=1)
                background = self.configure(nc, self.run_time, self.base_dir, spec, evaluation_type)

                exp = Core(self.run_time,
                           nc,
                           self.script_dir,
                           self.base_dir,
                           self.replay_pcaps_dir,
                           self.base_dir + "/logs/" + str(nc.project_name) + "_" + evaluation_type + "_" + str(nc.link_latency) + "_" + str(spec),
                           background[0],
                           background[1],
                           background[2])

                exp.start_project()

                
def get_network_configurations(link_latencies):

    network_configurations = []

    for link_latency in link_latencies:

        network_configuration = NetworkConfiguration("ryu",
                                                     "127.0.0.1",
                                                     6633,
                                                     "http://localhost:8080/",
                                                     "admin",
                                                     "admin",
                                                     "clique_enterprise",
                                                     {"num_switches": 5,
                                                      "per_switch_links": 3,
                                                      "num_hosts_per_switch": 1,
                                                      "switch_switch_link_latency_range": (link_latency, link_latency),
                                                      "host_switch_link_latency_range": (link_latency, link_latency)
                                                      },
                                                     conf_root="configurations/",
                                                     synthesis_name="SimpleMACSynthesis",
                                                     synthesis_params={},
                                                     # Can map multiple power simulator objects to same cyber node.
                                                     roles=[
                                                         # internal field bus network. clique topology structure created only for this
                                                         ("controller_node",["control;1"]),
                                                         ("pilot_buses_set_1",["2","25","29"]),
                                                         ("pilot_buses_set_2",["22","23","19"]),
                                                         ("pilot_buses_set_3",["20","10","6", "9"]),
                                                         ("generator",["30;1","31;1","32;1","33;1","34;1","35;1","36;1","37;1","38;1","39;1"]),

                                                         # part of enterprise network. Linear topology which is attached to the clique at one switch
                                                         ("enterprise-1",["vpn-gateway;1"]),
                                                         ("enterprise-2",["attacker;1"])

                                                     ],
                                                     project_name="evaluation",
                                                     power_simulator_ip="127.0.0.1",
                                                     link_latency=link_latency
                                                     )

        network_configurations.append(network_configuration)

    return network_configurations


def main():

    # Vary the delays (in miilseconds) on the links
    link_latencies = [0]#, 10]

    # Vary the the amount of 'load' that is running by modifying the background emulation threads
    background_specs = [5]#, 10, 15, 20]

    run_time = 300

    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    replay_pcaps_dir = script_dir + "/attack_plan"

    network_configurations = get_network_configurations(link_latencies)

    exp = Evaluation(run_time,
                     network_configurations,
                     script_dir,
                     base_dir,
                     replay_pcaps_dir,
                     background_specs)

    #evaluation_type = "emulation"
    evaluation_type = "replay"
    exp.trigger(evaluation_type)

if __name__ == "__main__":
    main()
