import os
import json


class DNP3PCAPPostProcessing:

    def __init__(self, base_dir, bro_dnp3_parser_dir, bro_cmd, bro_json_log_conf, project_name):

        self.base_dir = base_dir
        self.bro_dnp3_parser_dir = bro_dnp3_parser_dir
        self.bro_cmd = bro_cmd
        self.bro_json_log_conf = bro_json_log_conf
        self.project_name = project_name

        self.data = []
        self.periodicity_data = []

    def parse_latency_timing_using_bro(self, pcap_file_path):
        cmd = self.bro_cmd + " -b -C -r " + pcap_file_path + " " + self.bro_dnp3_parser_dir + " " + self.bro_json_log_conf

	print "Bro Command: ", cmd

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

    def collect_data(self, pcap_file_name, output_file_path=None):

        dir = self.base_dir + "/logs/" + self.project_name
        pcap_file_path = dir + "/" + pcap_file_name

        print "Processing:", pcap_file_path

        # Note: The following will collect both latency and periodicity data.
        bro_log_file_path = self.parse_latency_timing_using_bro(pcap_file_path)
        self.collect_bro_data_points(bro_log_file_path)

	print "Bro_Log_File_Path: ",bro_log_file_path

def main():

    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('Melody')
    base_dir = script_dir[0:idx] + "Melody"
    bro_dnp3_parser_dir = base_dir + "/src/utils/dnp3_timing/dnp3_parser_bro/"
    bro_json_log_conf = "/home/rakesh/bro/scripts/policy/tuning/json-logs.bro"
    bro_cmd = "/usr/bin/bro"
    project_name = "kronos_integration"

    p = DNP3PCAPPostProcessing(base_dir, bro_dnp3_parser_dir, bro_cmd, bro_json_log_conf, project_name)
    #p.collect_data("s1-eth2-s2-eth2.pcap")
    p.collect_data("s1-eth5-s2-eth5.pcap")
    print p.data


if __name__ == "__main__":
    main()

