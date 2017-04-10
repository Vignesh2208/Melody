import sys
import numpy

sys.path.append("./")
from core.shared_buffer import *
from utils.dnp3_pcap_post_processing import DNP3PCAPPostProcessing
import matplotlib.pyplot as plt

data_dir = os.path.dirname(os.path.realpath(__file__))


def get_params_from_path_name(dir_name):
    pattern = "E_5_"
    idx = dir_name.find(pattern)
    val_idx = idx + len(pattern)
    rem_string = dir_name[val_idx:]

    split_ls = rem_string.split('_')
    assert len(split_ls) == 4

    periodicity = int(split_ls[1])
    n_nodes = int(split_ls[0])

    return n_nodes, periodicity


def get_all_directories(directory_name):
    return [x[0] for x in os.walk(directory_name)]


def get_stats(src_dir, stats_type):
    stats = {}

    periodicities = []
    nodes = []

    for subdir, dirs, files in os.walk(src_dir):
        for dir_name in dirs:
            sub_dir_path = os.path.join(subdir, dir_name)
            if len(get_all_directories(sub_dir_path)) == 1:

                try:
                    n_nodes, periodicity = get_params_from_path_name(sub_dir_path)
                    print "N_nodes = ", n_nodes, " Periodicity: ", periodicity
                    project_name = None

                    pcap_file_path = dir_name + "/h1.pcap"

                    dnp3_stats = measure_dnp3_stats(project_name, pcap_file_path, stats_type)

                    if periodicity not in stats.keys():
                        stats[periodicity] = {}

                    stats[periodicity][n_nodes] = (dnp3_stats[stats_type][1], dnp3_stats[stats_type][2])

                    if periodicity not in periodicities:
                        periodicities.append(periodicity)

                    if n_nodes not in nodes:
                        nodes.append(n_nodes)
                except Exception as err:
                    print "Exception in File: ", sub_dir_path
                    continue

    stats["periods"] = sorted(periodicities)
    stats["nodes"] = sorted(nodes)
    return stats


def measure_dnp3_stats(project_name, pcap_file_path, stats_type):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    idx = script_dir.index('NetPower_TestBed')
    base_dir = script_dir[0:idx] + "NetPower_TestBed"
    bro_dnp3_parser_dir = base_dir + "/src/utils/dnp3_timing/dnp3_parser_bro/"
    # bro_json_log_conf = "/home/user/bro/scripts/policy/tuning/json-logs.bro"
    bro_json_log_conf = "/usr/local/bro/share/bro/policy/tuning/json-logs.bro"
    bro_cmd = "/usr/local/bro/bin/bro"

    p = DNP3PCAPPostProcessing(
        base_dir,
        bro_dnp3_parser_dir,
        bro_cmd,
        bro_json_log_conf,
        project_name)

    stats = {}
    if stats_type == "periodicity":
        p.collect_data(None, pcap_file_path=pcap_file_path)

        if p.periodicity_data:

            stats["header"] = ["samples", "mean", "std", "min", "max", "data"]
            stats[stats_type] = [len(p.periodicity_data[5:-1]), numpy.mean(p.periodicity_data[5:-1]),
                                    numpy.std(p.periodicity_data[5:-1]), min(p.periodicity_data[5:-1]),
                                    max(p.periodicity_data[5:-1]), p.periodicity_data]

    elif stats_type == "data_rate":
        p.collect_data_rates(pcap_file_path, 1)

        if p.data_rate_data:
            stats["header"] = ["samples", "mean", "std", "min", "max", "data"]
            stats[stats_type] = [len(p.data_rate_data[1:-2]), numpy.mean(p.data_rate_data[1:-2]),
                                    numpy.std(p.data_rate_data[1:-2]), min(p.data_rate_data[1:-2]),
                                    max(p.data_rate_data[1:-2]), p.data_rate_data]
    return stats


def plot_periodicity():

    stats = get_stats(data_dir, "periodicity")

    nodes = stats["nodes"]
    periodicities = stats["periods"]
    labels = []
    for period in periodicities:
        labels.append("Periodicity " + str(period) + " ms")

    fig = plt.figure()
    ax = plt.subplot(111)
    line_styles = ['-.', '--', '-', ':']
    marker = ['o', '<', '^', '+', '>']
    # matplotlib.rcParams.update({'font.size':15})
    plt.rc('legend', **{'fontsize': 15})
    xtics = [0]
    xtics.extend(nodes)

    for i in xrange(0, len(labels)):

        period = periodicities[i]
        stats[period]["mu"] = []
        stats[period]["std"] = []
        for j in xrange(0, len(nodes)):
            n_nodes = nodes[j]

            stats[period]["mu"].append(stats[period][n_nodes][0])
            stats[period]["std"].append(stats[period][n_nodes][1])

        # print stats[period]["std"]
        style = line_styles[i % len(line_styles)]
        mark = marker[i % len(marker)]
        ax.errorbar(x=nodes, y=stats[period]["mu"], xerr=0.0, yerr=stats[period]["std"], label=labels[i], linestyle=style,
                    marker=mark, linewidth=2)

        for j in xrange(0, len(nodes)):
            n_nodes = nodes[j]
            xy = (n_nodes, stats[period]["mu"][j])

            x_disp = -10
            y_disp = 2
            if period == 100:
                x_disp = x_disp + 5
            if period == 1000:
                x_disp = x_disp + 10

            ax.annotate("," + str(round(stats[period]["std"][j], 2)) + ")", xy=xy, xytext=(x_disp, 10),
                        textcoords='offset points')
            ax.annotate('(' + str(round(stats[period]["mu"][j], 2)), xy=xy, xytext=(-45, 10), textcoords='offset points')
        ax.set_xticks(xtics)

    ax.set_title("Periodicity in Replay Mechanism vs Number of Nodes")
    ax.set_yscale('log', nonposy='clip')
    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height * 1.1])
    # Put a legend to the right of the current axis
    leg = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # leg = ax.legend(loc=0,bbox_to_anchor=(0.5, 1))
    # leg.get_frame().set_alpha(0.5)
    ax.set_xlabel("Number of Nodes")
    ax.set_ylabel("Periodicity (ms)")

    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(15)
    plt.show()


def plot_date_rate():
    stats = get_stats(data_dir, "data_rate")

    nodes = stats["nodes"]
    periodicities = stats["periods"]
    labels = []
    for period in periodicities:
        labels.append("Periodicity " + str(period) + " ms")

    #fig = plt.figure()
    fig, ax = plt.subplots(1, 1, sharex=False, sharey=False, figsize=(15, 8.0))
    line_styles = ['-.', '--', '-', ':']
    marker = ['o', '<', '^', '+', '>']
    # matplotlib.rcParams.update({'font.size':15})
    plt.rc('legend', **{'fontsize': 15})
    xtics = [0]
    xtics.extend(nodes)

    for i in xrange(0, len(labels)):

        period = periodicities[i]
        stats[period]["mu"] = []
        stats[period]["std"] = []
        for j in xrange(0, len(nodes)):
            n_nodes = nodes[j]

            stats[period]["mu"].append(stats[period][n_nodes][0])
            stats[period]["std"].append(stats[period][n_nodes][1])

        # print stats[period]["std"]
        style = line_styles[i % len(line_styles)]
        mark = marker[i % len(marker)]
        ax.errorbar(x=nodes,
                    y=stats[period]["mu"],
                    xerr=0.0,
                    yerr=stats[period]["std"],
                    label=labels[i],
                    linestyle=style,
                    marker=mark,
                    linewidth=2)

        for j in xrange(0, len(nodes)):
            n_nodes = nodes[j]
            xy = (n_nodes, stats[period]["mu"][j])

            x_disp = -10
            y_disp = 2
            if period == 100:
                x_disp = x_disp + 5
            if period == 1000:
                x_disp = x_disp + 10

            ax.annotate("       ," + str(round(stats[period]["std"][j], 2)) + ")",
                        xy=xy,
                        xytext=(x_disp, 10),
                        textcoords='offset points')
            ax.annotate('(' + str(round(stats[period]["mu"][j], 2)),
                        xy=xy,
                        xytext=(-45, 10),
                        textcoords='offset points')

        ax.set_xticks(xtics)

    ax.set_title("Data Rate in Replay Mechanism vs Number of Nodes")
    ax.set_yscale('log', nonposy='clip')

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 * 1.3, box.width * 1.0, box.height * 1.0])

    # Put a legend to the right of the current axis
    leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=3)

    ax.set_xlabel("Number of Nodes")
    ax.set_ylabel("Data Rate (Bytes per second)")

    ax.set_xlim(xmin=4)
    ax.set_xlim(xmax=26)

    ax.set_ylim(ymin=100)
    ax.set_ylim(ymax=20000)

    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(15)
    plt.show()


def display_parsed_pcaps(pcap_file_path_list):
    for pcap_file_path in pcap_file_path_list:
        print "PCAP file path:", pcap_file_path

        dnp3_stats = measure_dnp3_stats(None, pcap_file_path, "data_rate")
        print "-- Data Rate", "Mean:", dnp3_stats["data_rate"][1], "SD:", dnp3_stats["data_rate"][2]

        dnp3_stats = measure_dnp3_stats(None, pcap_file_path, "periodicity")
        print "-- Periodicity", "Mean:", dnp3_stats["periodicity"][1], "SD:", dnp3_stats["periodicity"][2]


#display_parsed_pcaps(["original/dnp3_rate_10.pcap", "original/dnp3_rate_100.pcap", "original/dnp3_rate_1000.pcap"])
#plot_periodicity()
plot_date_rate()
