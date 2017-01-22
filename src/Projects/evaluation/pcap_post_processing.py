import os
import csv
import json
import numpy as np
from scipy import stats
from collections import defaultdict

class PCAPPostProcessing:
    
    def __init__(self, base_dir, bro_dnp3_parser_dir, link_latencies, background_specs, evaluation_type):
        self.base_dir = base_dir
        self.bro_dnp3_parser_dir = bro_dnp3_parser_dir
        self.link_latencies = link_latencies
        self.background_specs = background_specs
        self.evaluation_type = evaluation_type

    def parse_latency_timing_using_bro(self, pcap_file_path):
        bro_json_log_conf = "/usr/local/bro/share/bro/policy/tuning/json-logs.bro"

        # Run bro parser
        os.system("/usr/local/bro/bin/bro -b -C -r " + pcap_file_path + " " + self.bro_dnp3_parser_dir + " " + bro_json_log_conf)

        # Move the file to pcap directory
        bro_log_file_path = pcap_file_path + ".log"
        os.system("mv dnp3.log " + bro_log_file_path)

        return bro_log_file_path

    def collect_data(self, bro_log_file_path):
        x = []
        with open(bro_log_file_path, "r") as infile:
            for l in infile.readlines():
                bro_dict = json.loads(l)
                if "latency" in bro_dict:
                    x.append(bro_dict['latency'] * 1000)
                else:
                    print "Missing latency entry in:", bro_log_file_path
        return x

    def process(self):

        for latency in self.link_latencies:
            for spec in self.background_specs:
                dir = self.base_dir + "/logs/evaluation_" + self.evaluation_type + "_" + str(latency) + "_" + str(spec)
                pcap_file_path = dir + "/" + "s1-eth2-s2-eth2.pcap"

                print "Processing:", pcap_file_path

                bro_log_file_path = self.parse_latency_timing_using_bro(pcap_file_path)
                x = self.collect_data(bro_log_file_path)

                print pcap_file_path + " Mean Latency:", np.mean(x)
                print pcap_file_path + " Stdev Latency:", np.std(x)
                print pcap_file_path + " Sterr Latency:", stats.sem(x)

    def process_plotly(self):

        field_names = ["Link Latency"]
        for spec in self.background_specs:
            field_names.extend(["Lower-Load-" + str(spec), "Number of background ping flows:" + str(spec), "Upper-Load-" + str(spec)])

        plotly_data = defaultdict(defaultdict)
        with open('plotly.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(field_names)

            for latency in self.link_latencies:
                field_values = [latency]
                for spec in self.background_specs:
                    dir = self.base_dir + "/logs/evaluation_" + self.evaluation_type + "_" + str(latency) + "_" + str(spec)
                    pcap_file_path = dir + "/" + "s1-eth2-s2-eth2.pcap"

                    print "Processing:", pcap_file_path

                    bro_log_file_path = self.parse_latency_timing_using_bro(pcap_file_path)
                    x = self.collect_data(bro_log_file_path)

                    mu = np.mean(x)
                    sd = np.std(x)
                    se = stats.sem(x)

                    field_values.extend([mu - sd, mu, mu + sd])

                writer.writerow(field_values)


def main():

    # # Vary the delays (in miilseconds) on the links
    link_latencies = [5, 10, 15, 20, 25]

    # Vary the the amount of 'load' that is running by modifying the background emulation threads
    background_specs = [10, 20, 30, 40]

    evaluation_type = "replay"

    # Vary the delays (in miilseconds) on the links
    # link_latencies = [5, 10, 15, 20, 25]
    #
    # # Vary the the amount of 'load' that is running by modifying the background emulation threads
    # background_specs = [10, 20, 30, 40]
    #
    # evaluation_type = "emulation"

    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    bro_dnp3_parser_dir = base_dir + "/dnp3_timing/dnp3_parser_bro/"

    p = PCAPPostProcessing(base_dir, bro_dnp3_parser_dir, link_latencies, background_specs, evaluation_type)
    #p.process()
    p.process_plotly()


if __name__ == "__main__":
    main()

