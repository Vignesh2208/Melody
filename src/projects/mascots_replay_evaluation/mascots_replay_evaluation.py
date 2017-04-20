import sys
import numpy
sys.path.append("./")

from cyber_network.network_configuration import NetworkConfiguration
from cyber_network.traffic_flow import EmulatedTrafficFlow
from cyber_network.traffic_flow import TRAFFIC_FLOW_PERIODIC, TRAFFIC_FLOW_EXPONENTIAL, TRAFFIC_FLOW_ONE_SHOT
from cyber_network.network_scan_event import NetworkScanEvent
from cyber_network.network_scan_event import NETWORK_SCAN_NMAP_PORT
from core.net_power import NetPower
from core.shared_buffer import *
from utils.dnp3_pcap_post_processing import DNP3PCAPPostProcessing
import argparse
import time

ENABLE_TIMEKEEPER = 1
TDF = 5
CPUS_SUBSET = "2-3"

if ENABLE_TIMEKEEPER == 1:
    enabled = "E_" + str(TDF)
else:
    enabled = "D_"
    
dnp3_replay_rate = 10
n_hosts = 5
project_name = "mascots_evaluation_" + str(enabled) + "_" + str(n_hosts) + "_" + str(dnp3_replay_rate) + "_" + str(time.time())


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

        super(
            TimeKeeperIntegration,
            self).__init__(
            run_time,
            network_configuration,
            script_dir,
            base_dir,
            replay_pcaps_dir,
            log_dir,
            emulated_background_traffic_flows,
            emulated_network_scan_events,
            emulated_dnp3_traffic_flows,
            ENABLE_TIMEKEEPER,
            TDF,
            CPUS_SUBSET)

def generate_roles(params) :
    roles = [("controller_node",["control;1"])]
    num_hosts = params["num_switches"] * params["num_hosts_per_switch"] - 1

    i = 0
    for i in xrange(num_hosts) :
        curr_role = ("job_" + str(i), ["id_" + str(i)+ ";1"])
        roles.append(curr_role)

    return roles

def get_network_configuration():

    params = {"num_switches": 1,
              "num_hosts_per_switch": n_hosts,
              "switch_switch_link_latency_range": (0, 0),
              "host_switch_link_latency_range": (0.08, 0.08)}
              
    roles = generate_roles(params)   
    network_configuration = NetworkConfiguration("ryu",
                                                 "127.0.0.1",
                                                 6633,
                                                 "http://localhost:8080/",
                                                 "admin",
                                                 "admin",
                                                 "linear",
                                                 params,
                                                 conf_root="configurations/",
                                                 synthesis_name="SimpleMACSynthesis",
                                                 synthesis_params={},
                                                 roles=roles,
                                                 project_name="mascots_replay_evaluation",
                                                 power_simulator_ip="127.0.0.1"
                                                 )

    network_configuration.setup_network_graph(
        mininet_setup_gap=1, synthesis_setup_gap=1)

    return network_configuration


def measure_dnp3_stats(project_name, pcap_file_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    bro_dnp3_parser_dir = base_dir + "/src/utils/dnp3_timing/dnp3_parser_bro/"
    bro_json_log_conf = "/home/user/bro/scripts/policy/tuning/json-logs.bro"
    bro_cmd = "/usr/local/bro/bin/bro"

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
            print "sum:", sum(p.periodicity_data[5:])
        print "------------------------"

        stats = {}
        stats["header"] = ["samples", "mean", "std", "min", "max", "data"]
        stats["latency"] = [len(p.data[5:]),numpy.mean(p.data[5:]),numpy.std(p.data[5:]),min(p.data[5:]),max(p.data[5:]),p.data]
        stats["periodicity"] = [len(p.periodicity_data[5:]),numpy.mean(p.periodicity_data[5:]),numpy.std(p.periodicity_data[5:]),min(p.periodicity_data[5:]),max(p.periodicity_data[5:]),p.periodicity_data]
        return stats

def write_stats_to_file(project_name,log_dir_name,pcap_file_name,write_file_name,base_dir):
    #dir_to_write = base_dir + "/src/projects/mascots_evaluation/experimental_results/"
    dir_to_write = base_dir + "/src/projects/mascots_evaluation/experimental_results/4_cpus_blocker/"
    stats = measure_dnp3_stats(log_dir_name, pcap_file_name)
    periodicity_data_file = dir_to_write + write_file_name + "periodicity.csv"
    latency_data_file = dir_to_write + write_file_name + "latency.csv"

    with open(periodicity_data_file, 'w') as f:
        f.write(str(stats["header"])[1:-1]+'\n')
        f.write(str(stats["periodicity"])[1:-1])

    with open(latency_data_file, 'w') as f:
        f.write(str(stats["header"])[1:-1]+'\n')
        f.write(str(stats["latency"])[1:-1])

def get_emulated_ping(network_configuration,src,dst,root_user_name,root_password,run_time,interval):
    return EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                               offset=1,
                               inter_flow_period=0,
                               run_time=run_time,
                               src_mn_node=network_configuration.mininet_obj.get(src),
                               dst_mn_node=network_configuration.mininet_obj.get(dst),
                               root_user_name=root_user_name,
                               root_password=root_password,
                               server_process_start_cmd="",
                               client_expect_file="ping -w " + str(run_time) + " -i "+ str(interval) +" " + network_configuration.mininet_obj.get(dst).IP(),
                               long_running=True)


def get_emulated_dnp3(network_configuration,controller,dst,root_user_name,root_password,run_time,base_dir):
    return  EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=1,
                            inter_flow_period=0,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get(controller),
                            dst_mn_node=network_configuration.mininet_obj.get(dst),
                            root_user_name=root_user_name,
                            root_password=root_password,
                            server_process_start_cmd='python ' + base_dir + "/src/cyber_network/dnp3_slave.py --slave_ip " + \
                            network_configuration.mininet_obj.get(dst).IP() + " --life_time " + str(run_time) + " --vt " + str(ENABLE_TIMEKEEPER),
                            client_expect_file='python ' + base_dir + "/src/cyber_network/dnp3_master.py --slave_ip " + \
                            network_configuration.mininet_obj.get(dst).IP() + " --life_time " + str(run_time) +" --vt " + str(ENABLE_TIMEKEEPER),
                            long_running=True)


def get_emulated_udp(network_configuration,src,dst,root_user_name,root_password,run_time,base_dir,port,interval):
        # UDP 1->3
        return EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=1,
                            inter_flow_period=0,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get(src),
                            dst_mn_node=network_configuration.mininet_obj.get(dst),
                            root_user_name=root_user_name,
                            root_password=root_password,
                            server_process_start_cmd='sudo nice -20 python ' + base_dir + "/src/cyber_network/simple_udp_server.py --serv_ip " + network_configuration.mininet_obj.get(dst).IP() + " --port " + str(port),
                            client_expect_file='sudo nice -20 python ' + base_dir + "/src/cyber_network/simple_udp_client.py --serv_ip " + network_configuration.mininet_obj.get(dst).IP() + " --port " + str(port) + " --freq " + str(interval),
                            long_running=True)

def get_emulated_blocker(network_configuration,src,dst,root_user_name,root_password,run_time,base_dir):
        # blocker script
        return EmulatedTrafficFlow(type=TRAFFIC_FLOW_ONE_SHOT,
                            offset=5,
                            inter_flow_period=0,
                            run_time=run_time,
                            src_mn_node=network_configuration.mininet_obj.get(src),
                            dst_mn_node=network_configuration.mininet_obj.get(dst),
                            root_user_name=root_user_name,
                            root_password=root_password,
                            server_process_start_cmd="python " + base_dir + "/src/cyber_network/blocker.py ",
                            client_expect_file='python ' + base_dir + "/src/cyber_network/blocker.py ",
                            long_running=True)

def main():

    global project_name
    global n_hosts

    parser = argparse.ArgumentParser()
    parser.add_argument("--flow_count", dest="flow_count", help="Number of UDP requests you want to emulate", required=True)
    parser.add_argument("--version", dest="version", help="Version Number for result file")
    parser.add_argument("--runtime", dest="runtime", help="Run time in seconds")
    args = parser.parse_args()
    
    project_name = project_name + "_" + str(args.flow_count)

    if (args.runtime):
        run_time = int(args.runtime)
    else:
        run_time = 5

    root_user_name = "user"
    root_password = "passwd"

    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    replay_pcaps_dir = script_dir + "/attack_plan"

    network_configuration = get_network_configuration()
    os.system("sudo chmod -R 777 " + base_dir + "/logs")
    log_dir = base_dir + "/logs/" + str(project_name)
    mn_h1 = network_configuration.mininet_obj.get("h1")
    mn_h2 = network_configuration.mininet_obj.get("h2")
    mn_h3 = network_configuration.mininet_obj.get("h3")
    bg_flows = []
    interval = 0.1

    src = 1
    for i in range(0,int(args.flow_count)):
    
        
        if src % n_hosts == 0 :
            src_host = "h" + str(n_hosts)
        else:
            src_host = "h" + str(src)
        
            
        if (src + 1) % n_hosts == 0 :
            dst_host = "h" + str(n_hosts)
        else:
            dst_host = "h" + str((src + 1) % n_hosts)
           
        src = src + 1

        bg_flows.append(get_emulated_blocker(network_configuration,src_host,dst_host,root_user_name,root_password,run_time,base_dir))


    print len(bg_flows)

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


    try:
        write_file_name = str(ENABLE_TIMEKEEPER) + "_" + str(len(bg_flows)*2) + "_" + str(src) + "_" + str(dst) + "_" + str(interval) + "_"
        if (args.version):
            write_file_name = write_file_name + "v" + str(args.version) + "_"
        write_stats_to_file(exp.project_name, project_name, "h1.pcap", write_file_name, base_dir)
    except:
        measure_dnp3_stats(project_name,"h1.pcap")
        
    
    os.system("sudo chmod -R 777 " + log_dir)    
    os.system("sudo killall -9 python")


if __name__ == "__main__":
    main()
