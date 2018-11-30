import sys
import numpy
import argparse
sys.path.append("./")

from cyber_network.network_configuration import NetworkConfiguration
from cyber_network.traffic_flow import EmulatedTrafficFlow
from cyber_network.traffic_flow import TRAFFIC_FLOW_PERIODIC, TRAFFIC_FLOW_EXPONENTIAL, TRAFFIC_FLOW_ONE_SHOT
from cyber_network.network_scan_event import NetworkScanEvent
from cyber_network.network_scan_event import NETWORK_SCAN_NMAP_PORT
from core.net_power import NetPower
from core.shared_buffer import *
from utils.dnp3_pcap_post_processing import DNP3PCAPPostProcessing


# set of CPUs to run emulation/replay processes on when Kronos is not
# enabled
CPUS_SUBSET = "1-12"


class KronosIntegration(NetPower):

    def __init__(self,
                 run_time,
                 network_configuration,
                 script_dir,
                 base_dir,
                 replay_pcaps_dir,
                 log_dir,
                 emulated_background_traffic_flows,
                 enable_kronos,
		 relative_cpu_speed):

        super(
            KronosIntegration,
            self).__init__(
            run_time,
            network_configuration,
            script_dir,
            base_dir,
            replay_pcaps_dir,
            log_dir,
            emulated_background_traffic_flows,
            enable_kronos,
            relative_cpu_speed,
            CPUS_SUBSET)


def get_network_configuration(project_name):

    network_configuration = NetworkConfiguration(
                                                 controller="ryu",
                                                 controller_ip="127.0.0.1",
                                                 controller_port=6633,
                                                 controller_api_base_url="http://localhost:8080/",
                                                 controller_api_user_name="admin",
                                                 controller_api_password="admin",
                                                 topo_name="clique_enterprise",
                                                 topo_params={"num_switches": 5,
                                                  "per_switch_links": 2,
                                                  "num_hosts_per_switch": 1,
                                                  "switch_switch_link_latency_range": (1, 1),
                                                  "host_switch_link_latency_range": (1, 1)
                                                  },
                                                 conf_root="configurations/",
                                                 synthesis_name="SimpleMACSynthesis",
                                                 synthesis_params={},
                                                 # Can map multiple power
                                                 # simulator objects to same
                                                 # cyber node.
                                                 roles=[
                                                     # internal field bus
                                                     # network. clique topology
                                                     # structure created only
                                                     # for this
                                                     ("controller_node",
                                                      ["control;1"]),
                                                     ("pilot_buses_set_1",
                                                      ["2", "25", "29"]),
                                                     ("pilot_buses_set_2",
                                                      ["22", "23", "19"]),
                                                     ("pilot_buses_set_3", [
                                                      "20", "10", "6", "9"]),
                                                     ("generator",
                                                      ["30;1", "31;1", "32;1",
                                                       "33;1", "34;1", "35;1",
                                                       "36;1", "37;1", "38;1",
                                                       "39;1"]),

                                                     # part of enterprise
                                                     # network. Linear topology
                                                     # which is attached to the
                                                     # clique at one switch
                                                     ("enterprise-1",
                                                      ["vpn-gateway;1"]),
                                                     ("enterprise-2",
                                                      ["attacker;1"])

                                                 ],
                                                 project_name=project_name,
                                                 power_simulator_ip="127.0.0.1"
                                                 )

    network_configuration.setup_network_graph(
        mininet_setup_gap=1, synthesis_setup_gap=1)

    return network_configuration


def measure_dnp3_latencies(project_name, pcap_file_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    bro_dnp3_parser_dir = base_dir + "/src/utils/dnp3_timing/dnp3_parser_bro/"
    bro_json_log_conf = "/home/moses/bro/scripts/policy/tuning/json-logs.bro"
    bro_cmd = "/usr/local/bro/bin/bro"

    try:
        p = DNP3PCAPPostProcessing(
            base_dir,
            bro_dnp3_parser_dir,
            bro_cmd,
            bro_json_log_conf,
         project_name)
        p.collect_data(pcap_file_name)

        if p.data:
            print "------------------------"
            print " DNP3 Latency Data:"
            print "------------------------"
            print p.data
            if (p.data[5:]): # print stats if there are more than 5 samples
                print "Num samples:", len(p.data[5:])
                print "mean:", numpy.mean(p.data[5:])
                print "std:", numpy.std(p.data[5:])
                print "min:", min(p.data[5:])
                print "max:", max(p.data[5:])

        if p.periodicity_data:
            print "------------------------"
            print " DNP3 Periodicity Data:"
            print "------------------------"
            print p.periodicity_data
            if (p.periodicity_data[5:]): # print stats if there are more than 5 samples
                print "Num samples:", len(p.periodicity_data[5:])
                print "mean:", numpy.mean(p.periodicity_data[5:])
                print "std:", numpy.std(p.periodicity_data[5:])
                print "min:", min(p.periodicity_data[5:])
                print "max:", max(p.periodicity_data[5:])
            print "------------------------"

    except:
        print "No DNP3 packets were transmitted ..."


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--run_time', dest="run_time", type=int, default=10, help = "Running time for the experiment (in virtual time)")
    parser.add_argument('--root_user_name', dest="root_user_name", default="moses", help = "Root User Name")
    parser.add_argument('--root_password', dest="root_password", default="davidmnicol", help = "Root Password")
    parser.add_argument('--project_name', dest="project_name", default="kronos_integration", help = "Name of the project. Logs will be created under this")
    parser.add_argument('--enable_kronos', dest="enable_kronos", default=0, type=int, help = "Enable Kronos ?")
    parser.add_argument('--rel_cpu_speed', dest="rel_cpu_speed", default=1, type=int, help = "Relatice cpu speed of processes if kronos is enabled")

    run_time = args.run_time
    root_user_name = args.root_user_name
    root_password = args.root_password

    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    replay_pcaps_dir = script_dir + "/attack_plan"

    network_configuration = get_network_configuration(args.project_name)
    log_dir = base_dir + "/logs/" + str(network_configuration.project_name)
    mn_h1 = network_configuration.mininet_obj.get("h1")
    mn_h2 = network_configuration.mininet_obj.get("h2")
    mn_h3 = network_configuration.mininet_obj.get("h3")

    bg_flows = [

        # Ping 1->2
        EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=1,
                            inter_flow_period=0,
                            run_time=run_time,
                            src_mn_node=mn_h1,
                            dst_mn_node=mn_h2,
                            root_user_name=root_user_name,
                            root_password=root_password,
                            server_process_start_cmd="",
                            client_expect_file="ping -w " + \
                            str(run_time-1) + " -i 0.2 10.0.0.2",
                            long_running=True),

        # Dnp3 1->3
        EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=1,
                            inter_flow_period=0,
                            run_time=run_time,
                            src_mn_node=mn_h1,
                            dst_mn_node=mn_h3,
                            root_user_name=root_user_name,
                            root_password=root_password,
                            server_process_start_cmd='python ' + base_dir + "/src/cyber_network/dnp3_slave.py --slave_ip " + \
                            network_configuration.mininet_obj.get("h3").IP() + " --life_time " + str(run_time),
                            client_expect_file='python ' + base_dir + "/src/cyber_network/dnp3_master.py --slave_ip " + \
                            network_configuration.mininet_obj.get("h3").IP() + " --life_time " + str(run_time),
                            long_running=True),

        # UDP 1->3
        EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=1,
                            inter_flow_period=0,
                            run_time=run_time,
                            src_mn_node=mn_h1,
                            dst_mn_node=mn_h3,
                            root_user_name=root_user_name,
                            root_password=root_password,
                            server_process_start_cmd='python ' + base_dir + "/src/cyber_network/simple_udp_server.py",
                            client_expect_file='python ' + base_dir + "/src/cyber_network/simple_udp_client.py",
                            long_running=True),

        # SSH 1->2
        EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=1,
                            inter_flow_period=0,
                            run_time=run_time,
                            src_mn_node=mn_h1,
                            dst_mn_node=mn_h2,
                            root_user_name=root_user_name,
                            root_password=root_password,
                            server_process_start_cmd="/usr/sbin/sshd -D -p 22 -o ListenAddress=" + \
                            network_configuration.mininet_obj.get("h2").IP(),
                            client_expect_file='python ' + base_dir + "/src/cyber_network/ssh_session.py --dest_ip " + \
                            mn_h2.IP() + " --username " + root_user_name + " --password " + root_password,
                            long_running=True),

        # Telnet 1->2
        EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=1,
                            inter_flow_period=0,
                            run_time=run_time,
                            src_mn_node=mn_h1,
                            dst_mn_node=mn_h2,
                            root_user_name=root_user_name,
                            root_password=root_password,
                            server_process_start_cmd="sudo socat tcp-l:23,reuseaddr,fork exec:/bin/login,pty,setsid,setpgid,stderr,ctty",
                            client_expect_file='python ' + base_dir + "/src/cyber_network/telnet_session.py --dest_ip " + mn_h2.IP(),
                            long_running=True),
    ]

    exp = KronosIntegration(run_time=run_time,
                            network_configuration=network_configuration,
                            script_dir=script_dir,
                            base_dir=base_dir,
                            replay_pcaps_dir=replay_pcaps_dir,
                            log_dir=log_dir,
                            emulated_background_traffic_flows=bg_flows,
                            enable_kronos=args.enable_kronos,
		            relative_cpu_speed=args.rel_cpu_speed)

    exp.start_project()
    #measure_dnp3_latencies(args.project_name, "s1-eth2-s2-eth2.pcap")
    os.system("sudo killalll -9 python")


if __name__ == "__main__":
    main()
