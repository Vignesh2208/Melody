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

ENABLE_TIMEKEEPER = 1
TDF = 2
# set of CPUs to run emulation/replay processes on when timekeeper is not
# enabled
CPUS_SUBSET = "2-3"
#CPUS_SUBSET = "2-50"


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



def measure_dnp3_stats(project_name, pcap_file_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    bro_dnp3_parser_dir = base_dir + "/src/utils/dnp3_timing/dnp3_parser_bro/"
    bro_json_log_conf = "/home/moses/bro/scripts/policy/tuning/json-logs.bro"
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

def write_stats_to_file(project_name,pcap_file_name,write_file_name,base_dir,proj_ext,flag_filtered):
    #dir_to_write = base_dir + "/src/projects/mascots_evaluation/experimental_results/"
    #dir_to_write = base_dir + "/src/projects/mascots_evaluation/experimental_results/tdf_and_poll_tests/" + "TDF_" + str(TDF) + "/" + "poll_"
    #dir_to_write = base_dir + "/src/projects/mascots_evaluation/experimental_results/motivation-blocker_only/"
    #dir_to_write = base_dir + "/src/projects/mascots_evaluation/experimental_results/motivation-blocker_only-tk/"
    #dir_to_write = base_dir + "/logs/" + proj_ext + "/logs/"

    dir_to_write = base_dir + "/logs/" + proj_ext
    
    #stats = measure_dnp3_stats(project_name, pcap_file_name)
    stats = measure_dnp3_stats(proj_ext, pcap_file_name)
    if (flag_filtered):
	periodicity_data_file = dir_to_write + write_file_name + "filtered-periodicity.csv"
	latency_data_file = dir_to_write + write_file_name + "filtered-latency.csv"
    else:
	periodicity_data_file = dir_to_write + write_file_name + "periodicity.csv"
	latency_data_file = dir_to_write + write_file_name + "latency.csv"

    with open(periodicity_data_file, 'w') as f:
        f.write(str(stats["header"])[1:-1]+'\n')
        f.write(str(stats["periodicity"])[1:-1])

    with open(latency_data_file, 'w') as f:
        f.write(str(stats["header"])[1:-1]+'\n')
        f.write(str(stats["latency"])[1:-1])


def main():

    #measure_dnp3_stats("timekeeper_integration","s1-eth2-s2-eth2.pcap")
    #sys.exit(0)

    parser = argparse.ArgumentParser()
    parser.add_argument("--flow_count", dest="flow_count", help="Number of UDP requests you want to emulate")
    parser.add_argument("--version", dest="version", help="Version Number for result file")
    parser.add_argument("--runtime", dest="runtime", help="Run time in seconds")
    parser.add_argument("--dnp3int", dest="dnp3int", help="Interval for DNP3 polling in milliseconds", required=True)
    parser.add_argument("--sw", dest="sw", help="Number of Switches in Topology")
    parser.add_argument("--l", dest="links_per_sw", help="Number of Links per Switch")
    parser.add_argument("--h", dest="hosts_per_sw", help="Number of Hosts per Switch")
    parser.add_argument("--filtered", dest="filtered", action="store_true", help="Use filtered pcap")
    args = parser.parse_args()

    if (args.dnp3int):
	dnp3_interval = int(args.dnp3int)
    else:
	dnp3_interval = 10

    if (args.runtime):
        run_time = int(args.runtime)
    else:
        #run_time = 20
	#run_time = int(dnp3_interval * 2)
	if (dnp3_interval <= 10):
	    run_time = int(dnp3_interval/2)
	elif (dnp3_interval > 200):
	    run_time = int(dnp3_interval/20)
	else: 
	    run_time = int(dnp3_interval/10)

    # Number of Switches
    if (args.sw):
	num_sw = int(args.sw)
    else:
	num_sw = 10 
    # Number of Per Switch Links
    if (args.links_per_sw):
	num_links_per_sw = int(args.links_per_sw)
    else:
	num_links_per_sw = 2 
    # Number of Hosts per Switch
    if (args.hosts_per_sw):
	num_hosts_per_sw = int(args.hosts_per_sw)
    else: 
	num_hosts_per_sw = 4

    # print experiment settings:
    if (ENABLE_TIMEKEEPER):
	print "TimeKeeper Enabled"
    print "TDF: " + str(TDF)
    print "Run Time: " + str(run_time) + " seconds"
    print "DNP3 Polling Interval: " + str(dnp3_interval) + " milliseconds"
    print "Number of Switches: " + str(num_sw) 
    print "Number of Links per Switch: " + str(num_links_per_sw)
    print "Number of Hosts per Switch: " + str(num_hosts_per_sw)

    buffer_time = 1
    run_time = run_time + buffer_time

    root_user_name = "moses"
    root_password = "passwd"

    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    replay_pcaps_dir = script_dir + "/attack_plan"

    project_name = "mascots_evaluation"

    #project_name = "tdf_and_poll_tests"
    proj_ext = "tdf_"+str(TDF)+"-50cores-dnp3_"+str(dnp3_interval)+"ms-sw_"+str(num_sw)+"-h_"+str(num_hosts_per_sw)
    #proj_dir = base_dir + "/logs/"+str(project_name)+"/50_cores/TDF_" + str(TDF) + "/" + "poll_" + str(dnp3_interval)
    #proj_ext = str(project_name)+"/50_cores/TDF_" + str(TDF) + "/poll_" + str(dnp3_interval)
    #log_dir = base_dir + "/logs/" + str(network_configuration.project_name)
    #log_dir = base_dir + "/logs/" + proj_ext
    log_dir = base_dir + "/logs/" + proj_ext

    print "Log Directory: ",log_dir

    dnp3_host2 = 2*num_hosts_per_sw + 1	# the index of the 2nd DNP3 host
    print "DNP3 Hosts: h1, h"+str(dnp3_host2)

    #print "Number of background flows: ", len(bg_flows)
    bg_flows = [0]

    # generic:
    write_file_name = "_"
    #write_file_name = str(ENABLE_TIMEKEEPER) + "_" + str(len(bg_flows)+1) + "_" + "h1" + "_" + "h" + str(dnp3_host2) + "_" + str(dnp3_interval) + "_" + "sw" + str(num_sw) + "_" + "l" + str(num_links_per_sw) + "_"
    #write_file_name = str(ENABLE_TIMEKEEPER) + "_" + str(len(bg_flows)+1) + "_" + "h1" + "_" + "h" + str(dnp3_host2) + "_" + str(dnp3_interval) + "_" + "sw" + str(num_sw) + "_" + "l" + str(num_links_per_sw) + "_"

    if (args.version):
        write_file_name = write_file_name + "v" + str(args.version) + "_"

    # Parse DNP3 packet results:
    pcap_index = num_hosts_per_sw+1
    if (args.filtered):
	write_stats_to_file(project_name, "s1-eth"+str(pcap_index)+"-s2-eth"+str(pcap_index)+"-filtered.pcap", write_file_name, base_dir, proj_ext, args.filtered)
    else:
	write_stats_to_file(project_name, "s1-eth"+str(pcap_index)+"-s2-eth"+str(pcap_index)+".pcap", write_file_name, base_dir, proj_ext, False)

    # original: for 2 switches per link, 1 host per switch:
    #write_stats_to_file(exp.project_name, "s1-eth2-s2-eth2.pcap", write_file_name, base_dir)
    # 10 switches; 2 switches per link, 2 hosts per switch.
    #write_stats_to_file(exp.project_name, "s1-eth3-s2-eth3.pcap", write_file_name, base_dir)
    # 10 sw; 2 sw/link; 3 hosts per switch
    #write_stats_to_file(exp.project_name, "s1-eth4-s2-eth4.pcap", write_file_name, base_dir)
    # 10 sw; 2 sw/link; 4 hosts per switch
    #write_stats_to_file(exp.project_name, "s1-eth5-s2-eth5.pcap", write_file_name, base_dir)
    # for 4 switches per link:
    #write_stats_to_file(exp.project_name, "s1-eth6-s3-eth6.pcap", write_file_name, base_dir)
    #write_stats_to_file(exp.project_name, "s1-eth7-s2-eth7.pcap", write_file_name, proj_dir)
    # 10 sw; 3 switches per link, 1 host per switch:
    #write_stats_to_file(exp.project_name, "s1-eth3-s3-eth2.pcap", write_file_name, base_dir)

if __name__ == "__main__":
    main()
