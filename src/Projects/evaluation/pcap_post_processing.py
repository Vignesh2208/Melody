import os
import csv
import json
import numpy as np
from scipy import stats as ss
from collections import defaultdict


import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


class PCAPPostProcessing:
    
    def __init__(self, base_dir, bro_dnp3_parser_dir, link_latencies, background_specs, evaluation_type):
        self.base_dir = base_dir
        self.bro_dnp3_parser_dir = bro_dnp3_parser_dir
        self.link_latencies = link_latencies
        self.background_specs = background_specs
        self.evaluation_type = evaluation_type
        self.data = defaultdict(defaultdict)

    def parse_latency_timing_using_bro(self, pcap_file_path):
        bro_json_log_conf = "/usr/local/bro/share/bro/policy/tuning/json-logs.bro"

        # Run bro parser
        os.system("/usr/local/bro/bin/bro -b -C -r " + pcap_file_path + " " + self.bro_dnp3_parser_dir + " " + bro_json_log_conf)

        # Move the file to pcap directory
        bro_log_file_path = pcap_file_path + ".log"
        os.system("mv dnp3.log " + bro_log_file_path)

        return bro_log_file_path

    def collect_data_point(self, load, latency, bro_log_file_path):
        self.data[load][latency] = []
        with open(bro_log_file_path, "r") as infile:
            for l in infile.readlines():
                bro_dict = json.loads(l)
                if "latency" in bro_dict:
                    self.data[load][latency].append(bro_dict['latency'] * 1000)
                else:
                    print "Missing latency entry in:", bro_log_file_path

    def collect_data(self):

        for latency in self.link_latencies:
            for spec in self.background_specs:
                dir = self.base_dir + "/logs/evaluation_" + self.evaluation_type + "_" + str(latency) + "_" + str(spec)
                pcap_file_path = dir + "/" + "s1-eth2-s2-eth2.pcap"

                print "Processing:", pcap_file_path

                bro_log_file_path = self.parse_latency_timing_using_bro(pcap_file_path)
                self.collect_data_point(str(spec), str(latency), bro_log_file_path)

    def process_plotly(self):

        field_names = ["Link Latency"]
        for spec in self.background_specs:
            field_names.append("Number of background ping flows:" + str(spec))

        with open('plotly.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(field_names)

            for latency in sorted(self.data["10"].keys(), key=int):
                field_values = [latency]
                for spec in sorted(self.data.keys(), key=int):
                    dir = self.base_dir + "/logs/evaluation_" + self.evaluation_type + "_" + latency + "_" + spec
                    pcap_file_path = dir + "/" + "s1-eth2-s2-eth2.pcap"
                    print "Processing:", pcap_file_path
                    bro_log_file_path = self.parse_latency_timing_using_bro(pcap_file_path)
                    sd = np.std(self.data[spec][latency])
                    field_values.append(sd)

                writer.writerow(field_values)

    def prepare_matplotlib_data(self, data_dict):

        if type(data_dict.keys()[0]) == int:
            x = sorted(data_dict.keys(), key=int)
        elif type(data_dict.keys()[0]) == str or type(data_dict.keys()[0]) == unicode:
            x = sorted(data_dict.keys())

        data_means = []
        data_sds = []
        data_sems = []

        for p in x:
            mean = np.mean(data_dict[p])
            sd = np.std(data_dict[p])
            sem = ss.sem(data_dict[p])

            data_means.append(mean)
            data_sds.append(sd)
            data_sems.append(sem)

        return x, data_means, data_sds, data_sems

    def plot_lines_with_error_bars(self,
                                   series,
                                   ax,
                                   x_label,
                                   y_label,
                                   subplot_title,
                                   y_scale,
                                   x_min_factor=1.0,
                                   x_max_factor=1.05,
                                   y_min_factor=0.1,
                                   y_max_factor=1.5,
                                   xticks=None,
                                   xtick_labels=None,
                                   yticks=None,
                                   ytick_labels=None):

        ax.set_xlabel(x_label, fontsize=10, labelpad=-0)
        ax.set_ylabel(y_label, fontsize=10, labelpad=0)
        ax.set_title(subplot_title, fontsize=10)

        markers = ['*', '.', 'v', '+', 'd', 'o', '^', 'H', ',', 's', '*']
        marker_i = 0

        for line_data_key in sorted(self.data.keys()):
            data_vals = self.data[line_data_key]
            x, mean, sd, sem = self.prepare_matplotlib_data(data_vals)
            y = None

            if series == "mean":
                y = mean
            elif series == "sd":
                y = sd
            elif series == "sem":
                y = sem

            ax.plot(x, y, color="black", marker=markers[marker_i], markersize=7.0, label=line_data_key, ls='none')

            marker_i += 1

        ax.tick_params(axis='x', labelsize=10)
        ax.tick_params(axis='y', labelsize=10)

        low_xlim, high_xlim = ax.get_xlim()
        ax.set_xlim(xmax=(high_xlim) * x_max_factor)
        ax.set_xlim(xmin=(low_xlim) * x_min_factor)

        if y_scale == "linear":
            low_ylim, high_ylim = ax.get_ylim()
            ax.set_ylim(ymin=low_ylim*y_min_factor)
            ax.set_ylim(ymax=high_ylim*y_max_factor)
        elif y_scale == "log":
            ax.set_ylim(ymin=1)
            ax.set_ylim(ymax=10000)

        ax.set_yscale(y_scale)

        xa = ax.get_xaxis()
        xa.set_major_locator(MaxNLocator(integer=True))

        if xticks:
            ax.set_xticks(xticks)

        if xtick_labels:
            ax.set_xticklabels(xtick_labels)

        if yticks:
            ax.set_yticks(yticks)

        if ytick_labels:
            ax.set_yticklabels(ytick_labels)

    def plot_data(self, series):

        f, (ax1) = plt.subplots(1, 1, sharex=True, sharey=False, figsize=(5.0, 4.0))

        data_xtick_labels = self.data["10"].keys()
        data_xticks = [int(x) for x in data_xtick_labels]

        ylabel = None
        if series == "mean":
            ylabel = "Mean Latency"
        elif series == "sd":
            ylabel = "Standard Deviation of Latency"
        elif series == "sem":
            ylabel = "Standard Error of Mean of Latency"

        self.plot_lines_with_error_bars(series,
                                        ax1,
                                        "Per Link Latency",
                                        ylabel,
                                        "",
                                        y_scale='linear',
                                        x_min_factor=0.75,
                                        x_max_factor=1.1,
                                        y_min_factor=0.9,
                                        y_max_factor=1,
                                        xticks=data_xticks,
                                        xtick_labels=data_xtick_labels)

        xlabels = ax1.get_xticklabels()
        plt.setp(xlabels, rotation=0, fontsize=10)

        # Shrink current axis's height by 25% on the bottom
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0 + box.height * 0.3, box.width, box.height * 0.7])
        handles, labels = ax1.get_legend_handles_labels()

        ax1.legend(handles, labels, shadow=True, fontsize=10, loc='upper center', ncol=2, markerscale=1.0,
                   frameon=True, fancybox=True, columnspacing=0.5, bbox_to_anchor=[0.5, -0.25])

        plt.savefig(series + "_latency_evaluation_" + self.evaluation_type + ".png", dpi=1000)
        plt.show()


def main():

    # # Vary the delays (in miilseconds) on the links
    link_latencies = [5, 10, 15, 20, 25]

    # Vary the the amount of 'load' that is running by modifying the background emulation threads
    background_specs = [0, 10, 20, 30, 40]

    evaluation_type = "replay"

    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    bro_dnp3_parser_dir = base_dir + "/dnp3_timing/dnp3_parser_bro/"

    p = PCAPPostProcessing(base_dir, bro_dnp3_parser_dir, link_latencies, background_specs, evaluation_type)
    p.collect_data()

    for series in ["mean", "sd", "sem"]:
        p.plot_data(series)

    #p.process_plotly()


if __name__ == "__main__":
    main()

