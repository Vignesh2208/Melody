import sys
import os
import time
sys.path.append("./")


from cyber_network.network_configuration import NetworkConfiguration
from cyber_network.traffic_flow import EmulatedTrafficFlow
from cyber_network.traffic_flow import TRAFFIC_FLOW_PERIODIC, TRAFFIC_FLOW_EXPONENTIAL, TRAFFIC_FLOW_ONE_SHOT
from cyber_network.network_scan_event import NetworkScanEvent
from cyber_network.network_scan_event import NETWORK_SCAN_NMAP_PORT
from core.net_power import NetPower

from core.shared_buffer import *

from random import randint

ENABLE_TIMEKEEPER = 1
TDF = 2


class TimeKeeperIntegration(NetPower):

    def __init__(self,
                 run_time,
                 network_configuration,
                 script_dir,
                 base_dir,
                 replay_pcaps_dir,
                 log_dir,
                 emulated_background_traffic_flows,
                 emulated_network_scan_events,
                 emulated_dnp3_traffic_flows):

        super(TimeKeeperIntegration, self).__init__(run_time,
                                                    network_configuration,
                                                    script_dir,
                                                    base_dir,
                                                    replay_pcaps_dir,
                                                    log_dir,
                                                    emulated_background_traffic_flows,
                                                    emulated_network_scan_events,
                                                    emulated_dnp3_traffic_flows,
                                                    ENABLE_TIMEKEEPER,
                                                    TDF
                                                    )



def get_network_configuration():

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
                                                  "switch_switch_link_latency_range": (5, 5),
                                                  "host_switch_link_latency_range": (5, 5)
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
                                                     ("generator",		["30;1","31;1","32;1","33;1","34;1","35;1","36;1","37;1","38;1","39;1"]),

                                                     # part of enterprise network. Linear topology which is attached to the clique at one switch
                                                     ("enterprise-1",["vpn-gateway;1"]),
                                                     ("enterprise-2",["attacker;1"])

                                                 ],
                                                 project_name="timekeeper_integration",
                                                 power_simulator_ip="127.0.0.1"
                                                 )

    network_configuration.setup_network_graph(mininet_setup_gap=1, synthesis_setup_gap=1)

    return network_configuration




def main():

    run_time = 15
    flow_count = 3

    emulated_flow_definitions = {'dnp3': [('h1','h2','h3','h4','h5'),
                                          ('h1','h2','h3','h4','h5')],
                                 'ping':[('h1','h6','h7'),
                                         ('h1','h2','h3','h4','h5','h6')],
                                 'http':[('h1','h7'),('h1','h7')],
                                 'ssh':[('h7',),('h1',)],
                                 'telnet':[('h1',),('h2','h3','h4','h5')],
                                 'nmap': [('h1','h6','h7'), ('h1','h2','h3','h4','h5','h6')]}

    background_flows = ['ssh', 'telnet', 'http', 'ping']
    scans = ['nmap']
    control_flows = ['dnp3']

    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    replay_pcaps_dir = script_dir + "/attack_plan"

    network_configuration = get_network_configuration()
    log_dir = base_dir + "/logs/" + str(network_configuration.project_name)

    bg_flows = [
                
                #EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                #                    offset=1,
                #                    inter_flow_period=0,
                #                    run_time=run_time,
                #                    src_mn_node=network_configuration.mininet_obj.get("h1"),
                #                    dst_mn_node=network_configuration.mininet_obj.get("h2"),
                #                    root_user_name="ubuntu",
                #                    root_password="ubuntu",
                #                    server_process_start_cmd="",
                #                    client_expect_file='ping -c8 10.0.0.2'),
                
                EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=1,
                            inter_flow_period=0,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get("h1"),
                            dst_mn_node=network_configuration.mininet_obj.get("h2"),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd='python ' + base_dir + "/src/cyber_network/slave.py",
                            client_expect_file='python ' + base_dir + "/src/cyber_network/master.py",
                            long_running=True)
                

                #EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                #                    offset=1,
                #                    inter_flow_period=0,
                #                    run_time=run_time,
                #                    src_mn_node=network_configuration.mininet_obj.get("h1"),
                #                    dst_mn_node=network_configuration.mininet_obj.get("h2"),
                #                    root_user_name="ubuntu",
                #                    root_password="ubuntu",
                #                    server_process_start_cmd="",
                #                    client_expect_file=base_dir + "/src/core/bin/timerfd_test &"),
                ]

    exp = TimeKeeperIntegration(run_time,
                                network_configuration,
                                script_dir,
                                base_dir,
                                replay_pcaps_dir,
                                log_dir,
                                bg_flows,
                                [],
                                [])

    exp.start_project()

if __name__ == "__main__":
    main()

