import sys

sys.path.append("./")
from cyber_network.network_configuration import NetworkConfiguration
from cyber_network.traffic_flow import EmulatedTrafficFlow
from cyber_network.traffic_flow import TRAFFIC_FLOW_PERIODIC, TRAFFIC_FLOW_EXPONENTIAL, TRAFFIC_FLOW_ONE_SHOT
from cyber_network.network_scan_event import NetworkScanEvent
from cyber_network.network_scan_event import NETWORK_SCAN_NMAP_PORT
from Projects.main import Main

from Proxy.shared_buffer import *

from random import randint


class Microgrid(Main):

    def __init__(self,
                 run_time,
                 network_configuration,
                 script_dir,
                 base_dir,
                 replay_pcaps_dir,
                 emulated_background_traffic_flows,
                 emulated_network_scan_events,
                 emulated_dnp3_traffic_flows):

        super(Microgrid, self).__init__(run_time,
                                        network_configuration,
                                        script_dir,
                                        base_dir,
                                        replay_pcaps_dir,
                                        emulated_background_traffic_flows,
                                        emulated_network_scan_events,
                                        emulated_dnp3_traffic_flows)

'''
def get_emulated_background_traffic_flows(network_configuration, run_time, base_dir):
    emulated_background_traffic_flows = [
        EmulatedTrafficFlow(type=TRAFFIC_FLOW_PERIODIC,
                            offset=1,
                            inter_flow_period=1,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get("h7"),
                            dst_mn_node=network_configuration.mininet_obj.get("h1"),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd="",
                            client_expect_file=base_dir + '/src/cyber_network/ping_session.expect'),

        EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=5,
                            inter_flow_period=1,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get("h7"),
                            dst_mn_node=network_configuration.mininet_obj.get("h1"),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd="/usr/sbin/sshd -D -o ListenAddress=" + network_configuration.mininet_obj.get(
                                "h1").IP(),
                            client_expect_file=base_dir + '/src/cyber_network/ssh_session.expect',
                            long_running=False),

        EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=10,
                            inter_flow_period=2,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get("h1"),
                            dst_mn_node=network_configuration.mininet_obj.get("h2"),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd="sudo socat tcp-l:23,reuseaddr,fork exec:/bin/login,pty,setsid,setpgid,stderr,ctty",
                            client_expect_file=base_dir + '/src/cyber_network/socat_session.expect',
                            long_running=False),

        EmulatedTrafficFlow(type=TRAFFIC_FLOW_EXPONENTIAL,
                            offset=1,
                            inter_flow_period=run_time / 2,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get("h7"),
                            dst_mn_node=network_configuration.mininet_obj.get("h1"),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd="python -m SimpleHTTPServer",
                            client_expect_file=base_dir + '/src/cyber_network/http_session.expect'),

        EmulatedTrafficFlow(type=TRAFFIC_FLOW_EXPONENTIAL,
                            offset=1,
                            inter_flow_period=run_time / 2,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get("h7"),
                            dst_mn_node=network_configuration.mininet_obj.get("h1"),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd="/usr/sbin/sshd -D -o ListenAddress=" + network_configuration.mininet_obj.get(
                                "h1").IP(),
                            client_expect_file=base_dir + '/src/cyber_network/ssh_session.expect')
    ]

    return emulated_background_traffic_flows


def get_emulated_network_scan_events(network_configuration, run_time, base_dir):

    emulated_network_scan_events = [
        NetworkScanEvent(src_mn_node=network_configuration.mininet_obj.get("h1"),
                         dst_mn_node=network_configuration.mininet_obj.get("h2"),
                         type=NETWORK_SCAN_NMAP_PORT,
                         offset=5,
                         duration=15)
    ]

    return emulated_network_scan_events


def get_emulated_dnp3_traffic_flows(network_configuration, run_time, base_dir):

    emulated_dnp3_traffic_flows = [
        EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=1,
                            inter_flow_period=2,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get("h1"),
                            dst_mn_node=network_configuration.mininet_obj.get("h2"),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd='sudo python ' + base_dir + "/src/cyber_network/slave.py",
                            client_expect_file=base_dir + '/src/cyber_network/dnp3_master.expect',
                            long_running=True)
    ]

    return emulated_dnp3_traffic_flows
'''

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
                                                  #"switch_switch_link_latency_range": (10, 10),
                                                  #"host_switch_link_latency_range": (10, 10)
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
                                                 project_name="microgrid_with_background_traffic",
                                                 power_simulator_ip="127.0.0.1"
                                                 )

    network_configuration.setup_network_graph(mininet_setup_gap=1, synthesis_setup_gap=1)

    return network_configuration

def get_emulated_background_flow(flow_type, src, dst, network_configuration, run_time, base_dir, offset, inter_flow_period):
    emulated_background_flows = {
                        'ping': EmulatedTrafficFlow(type=TRAFFIC_FLOW_PERIODIC,
                            offset=offset,
                            inter_flow_period=inter_flow_period,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get(src),
                            dst_mn_node=network_configuration.mininet_obj.get(dst),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd="",
                            client_expect_file=base_dir + '/src/cyber_network/ping_session.expect'),

                        'http': EmulatedTrafficFlow(type=TRAFFIC_FLOW_EXPONENTIAL,
                            offset=offset,
                            inter_flow_period=inter_flow_period,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get(src),
                            dst_mn_node=network_configuration.mininet_obj.get(dst),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd="python -m SimpleHTTPServer",
                            client_expect_file=base_dir + '/src/cyber_network/http_session.expect'),

                        'ssh': EmulatedTrafficFlow(type=TRAFFIC_FLOW_EXPONENTIAL,
                            offset=offset,
                            inter_flow_period=inter_flow_period,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get(src),
                            dst_mn_node=network_configuration.mininet_obj.get(dst),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd="/usr/sbin/sshd -D -o ListenAddress=" + network_configuration.mininet_obj.get(
                                "h1").IP(),
                            client_expect_file=base_dir + '/src/cyber_network/ssh_session.expect'),

                        'telnet': EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=offset,
                            inter_flow_period=inter_flow_period,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get(src),
                            dst_mn_node=network_configuration.mininet_obj.get(dst),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd="sudo socat tcp-l:23,reuseaddr,fork exec:/bin/login,pty,setsid,setpgid,stderr,ctty",
                            client_expect_file=base_dir + '/src/cyber_network/socat_session.expect',
                            long_running=False)
                        }

    return emulated_background_flows[flow_type]

def get_emulated_control_flow(flow_type, src, dst, network_configuration, run_time, base_dir, offset, inter_flow_period):
    emulated_control_flows = {
                        'dnp3': EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=offset,
                            inter_flow_period=inter_flow_period,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get(src),
                            dst_mn_node=network_configuration.mininet_obj.get(dst),
                            root_user_name="ubuntu",
                            root_password="ubuntu",
                            server_process_start_cmd='sudo python ' + base_dir + "/src/cyber_network/slave.py",
                            client_expect_file=base_dir + '/src/cyber_network/dnp3_master.expect',
                            long_running=True)
                        }
    return emulated_control_flows[flow_type]

def get_emulated_network_scan_event(flow_type, src, dst, network_configuration, run_time, offset):
    emulated_network_scans = {
                        'nmap': NetworkScanEvent(src_mn_node=network_configuration.mininet_obj.get(src),
                             dst_mn_node=network_configuration.mininet_obj.get(dst),
                             type=NETWORK_SCAN_NMAP_PORT,
                             offset=offset,
                             duration=15)
                        }

def dataset_flow_generator(flow_count,run_time,emulated_flow_definitions,background_flows,scans,control_flows,network_configuration,base_dir):
    picked_protocols = []
    #picked_host_pairs = []
    
    dataset_emulated_flows = []

    for i in range (0,flow_count,1):
        picked_protocols.append(emulated_flow_definitions.keys()[randint(0,(len(emulated_flow_definitions)-1))])

    print picked_protocols

    for protocol in picked_protocols:
        #print emulated_flow_definitions[protocol]
        src = emulated_flow_definitions[protocol][0][randint(0,(len(emulated_flow_definitions[protocol][0])-1))]
        dst = src #emulated_flow_definitions[protocol][1][randint(0,(len(emulated_flow_definitions[protocol][1])-1))]
        while (src == dst):
            dst = emulated_flow_definitions[protocol][1][randint(0,(len(emulated_flow_definitions[protocol][1])-1))]


        offset = randint(0,run_time/2)
        inter_flow_period = randint(0,run_time/2)

        if protocol in background_flows:
            dataset_emulated_flows.append(get_emulated_background_flow(protocol,src,dst,network_configuration,run_time,base_dir,offset,inter_flow_period))
        
        elif protocol in control_flows:
            dataset_emulated_flows.append(get_emulated_control_flow(protocol,src,dst,network_configuration,run_time,base_dir,offset,inter_flow_period))

        elif protocol in scans:
            dataset_emulated_flows.append(get_emulated_network_scan_event(protocol,src,dst,network_configuration,run_time,offset))

        else:
            print ("Protocol not implemented or not found: " + protocol)

    return dataset_emulated_flows


def main():

    run_time = 80
    flow_count = 3

    emulated_flow_definitions = {'dnp3': [('h1','h2','h3','h4','h5'),('h1','h2','h3','h4','h5')], 'ping':[('h1','h6','h7'), ('h1','h2','h3','h4','h5','h6')], 'http':[('h1','h7'),('h1','h7')], 'ssh':[('h7',),('h1',)], 'telnet':[('h1',),('h2','h3','h4','h5')], 'nmap': [('h1','h6','h7'), ('h1','h2','h3','h4','h5','h6')]}
    background_flows = ['ssh', 'telnet', 'http', 'ping']
    scans = ['nmap']
    control_flows = ['dnp3']

    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    replay_pcaps_dir = script_dir + "/attack_plan"
    
    network_configuration = get_network_configuration()
    log_dir = base_dir + "/logs/" + str(network_configuration.project_name)
    #emulated_background_traffic_flows = get_emulated_background_traffic_flows(network_configuration,run_time,base_dir)

    #emulated_network_scan_events = get_emulated_network_scan_events(network_configuration,run_time,base_dir)

    #emulated_dnp3_traffic_flows = get_emulated_dnp3_traffic_flows(network_configuration,run_time,base_dir)

    dataset_flows =  dataset_flow_generator(flow_count,run_time,emulated_flow_definitions,background_flows,scans,control_flows,network_configuration,base_dir)
  
    exp = Main(run_time,
               network_configuration,
               script_dir,
               base_dir,
               replay_pcaps_dir,
	       log_dir,
               dataset_flows,
               [],
               [])

    exp.start_project()
    
if __name__ == "__main__":
    main()

