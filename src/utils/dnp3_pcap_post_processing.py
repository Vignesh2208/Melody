import os
import json
import string
import subprocess


class DNP3PCAPPostProcessing:

    def __init__(self, base_dir, bro_dnp3_parser_dir, bro_cmd, bro_json_log_conf, project_name):

        self.base_dir = base_dir
        self.bro_dnp3_parser_dir = bro_dnp3_parser_dir
        self.bro_cmd = bro_cmd
        self.bro_json_log_conf = bro_json_log_conf
        self.project_name = project_name

        self.data = []
        self.periodicity_data = []
        self.data_rate_data = []

    def parse_latency_timing_using_bro(self, pcap_file_path):
        cmd = self.bro_cmd + " -b -C -r " + pcap_file_path + " " + self.bro_dnp3_parser_dir + " " + self.bro_json_log_conf

        # Run bro parser
        os.system(cmd)

        # Move the file to pcap directory
        bro_log_file_path = pcap_file_path + ".log"
        os.system("mv dnp3.log " + bro_log_file_path)

        return bro_log_file_path

    def collect_bro_data_points(self, bro_log_file_path):
        if not os.path.exists(bro_log_file_path):
            print "Nothing to collect dnp3 data from. "
            return

        with open(bro_log_file_path, "r") as infile:
            for l in infile.readlines():
                bro_dict = json.loads(l)
                if "latency" in bro_dict:
                    self.data.append(bro_dict['latency'] * 1000)
                elif "periodicity" in bro_dict:
                    self.periodicity_data.append(bro_dict['periodicity'] * 1000)
                else:
                    print "Missing latency/periodicity entry in:", bro_log_file_path

    def collect_data(self, pcap_file_name, output_file_path=None, pcap_file_path=None):

        if not pcap_file_path:
            dir = self.base_dir + "/logs/" + self.project_name
            pcap_file_path = dir + "/" + pcap_file_name

        #print "Processing:", pcap_file_path
        # Note: The following will collect both latency and periodicity data.
        bro_log_file_path = self.parse_latency_timing_using_bro(pcap_file_path)
        self.collect_bro_data_points(bro_log_file_path)

    def collect_data_rates(self, pcap_file_path, interval):
        cmd = "python trace-summary " + pcap_file_path + " -i " + str(interval) + " -b -n 1 -E excluded"

        # Run bro parser
        output = subprocess.check_output(cmd, shell=True)
        output_lines = string.split(output, "\n")

        for i in range(len(output_lines)):
            prev_line_tokes = string.split(output_lines[i-1], " ")
            this_line_tokens = string.split(output_lines[i], " ")

            if prev_line_tokes[0] == ">==" and prev_line_tokes[2] == "===":
                if this_line_tokens[5]:
                    kbytes_str = this_line_tokens[5]
                    kbytes_int = float(kbytes_str[0:len(kbytes_str) - 1])
                    self.data_rate_data.append(kbytes_int * 1024)
                else:
                    bytes_str = this_line_tokens[6]
                    self.data_rate_data.append(float(bytes_str))


def main():

    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    bro_dnp3_parser_dir = base_dir + "/src/utils/dnp3_timing/dnp3_parser_bro/"
    #bro_json_log_conf = "/home/rakesh/bro/scripts/policy/tuning/json-logs.bro"
    bro_json_log_conf = "/usr/local/bro/share/bro/policy/tuning/json-logs.bro"
    #bro_cmd = "/usr/bin/bro"
    bro_cmd = "/usr/local/bro/bin/bro"
    project_name = "timekeeper_integration"

    p = DNP3PCAPPostProcessing(base_dir, bro_dnp3_parser_dir, bro_cmd, bro_json_log_conf, project_name)
    # p.collect_data("s1-eth2-s2-eth2.pcap")

    rate_pcap = "/home/ubuntu/NetPower_TestBed/src/projects/mascots_evaluation/attack_plan/dnp3_rate_10.pcap"
    p.collect_data_rates(rate_pcap, 1)
    print p.data


if __name__ == "__main__":
    main()

