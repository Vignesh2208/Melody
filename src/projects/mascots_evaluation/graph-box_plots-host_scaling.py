"""
Script for box plots of latency and periodicity.
Run with Python 3.4.
Modeled after box_plot_demo.py
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
import scipy as sp
import scipy.stats
import argparse

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m, (m-h, m+h)

parser = argparse.ArgumentParser()
parser.add_argument("--path", dest="path", help="Pathname for data files")
args = parser.parse_args()

# read in data from src files
# Specify the path where all of the csv files are grouped together.
if args.path:
	pathname = args.path
else:
	pathname = ""
	#pathname = "C:\\Users\\Elizabeth\\Documents\\Research Notes\\Siebel\\data\\scaling\\"

# List of files to be read... these are assorted because of the modification in file naming during the process of running the experiments.
# To be standardized later when file naming is decided.
filename_lst = ["1_146_h1_h3_0.5_sw10_l2_latency.csv","1_486_h1_h5_0.5_sw10_l2_latency.csv","1_1026_h1_h7_0.5_sw10_l2_latency.csv","1_1_h1_h9_sw10_h40_latency.csv","1_146_h1_h3_0.5_sw10_l2_periodicity.csv","1_486_h1_h5_0.5_sw10_l2_periodicity.csv","1_1026_h1_h7_0.5_sw10_l2_periodicity.csv","1_1_h1_h9_sw10_h40_periodicity.csv"]

# Could also update this to be dynamic later based on input parameter.
labels = ['10 Hosts','20 Hosts','30 Hosts','40 Hosts']
# Also have data for 50 hosts.

list_sample_counts = []
list_means = []
list_stds = []
list_mins = []
list_maxs = []
list_data_sets = []

# This variable indicates how many different host counts the experiment was run on.
num_sets = 4

for filename in filename_lst:
        with open(pathname+filename) as fp:
                #print ("Opened file: "+pathname+filename)
                for i, line in enumerate(fp):
                        #print (i)
                        if i == 1:
                                # first split line on "["
                                line_stats, line_data = line.split("[")
                                #print (line_stats[:-2])
                                #print (line_data[:-1])
                                
                                # split the comma separated line
                                samples, mean, std, dmin, dmax = line_stats[:-2].split(",")

                                data = []
                                # store data in array
                                for element in line_data[:-1].split(","):
                                        data.append(float(element))
        
        list_sample_counts.append(samples)
        list_means.append(mean)
        list_stds.append(std)
        list_mins.append(dmin)
        list_maxs.append(dmax)
        print ("Num Samples: ",samples,", Mean: ",mean,", StDev: ",std,", Min: ",dmin,", Max: ",dmax)
        #print (data)
        # convert array to numpy array and append
        # remove the first five samples
        list_data_sets.append(np.array(data[5:]))   

# group data sets
conf_intervals = []

# data1 for latency
data1 = []
conf_int_list = []
for i in range(num_sets):
        data1.append(list_data_sets[i])
        d_mean, dCI = mean_confidence_interval(list_data_sets[i])
        conf_int_list.append(dCI)
#print (conf_int_list)
conf_intervals.append(conf_int_list)

# data2 for periodicity
conf_int_list = []
data2 = []
for i in range(num_sets,num_sets*2):
        #print (i)
        data2.append(list_data_sets[i])
        d_mean, dCI = mean_confidence_interval(list_data_sets[i])
        conf_int_list.append(dCI)
#print (conf_int_list)
conf_intervals.append(conf_int_list)

print ("Confidence Intervals: ",conf_intervals)

data_set = [data1, data2]
graph_title = ['Latency of DNP Traffic','Periodicity of DNP Traffic']
xlabels = ['Number of Hosts in Topology','Number of Hosts in Topology']
ylabels = ['Latency (ms)', 'Periodicity (ms)']
outfilename = 'graph_latency_periodicity-40_hosts.png'

fig, (ax1,ax2) = plt.subplots(2)

#print (data)
pos = np.array(range(len(data1))) + 1

numBoxes = len(data1)
medians = list(range(numBoxes))

bp = ax1.boxplot(data_set[0], sym='+', positions=pos, notch=1, conf_intervals=conf_intervals[0], vert=1, whis=1.5)
#
plt.setp(bp['boxes'], color='black')
plt.setp(bp['whiskers'], color='black', linestyle='-')
plt.setp(bp['fliers'], markersize=3.0)

bp2 = ax2.boxplot(data_set[1], sym='+', positions=pos, notch=1, conf_intervals=conf_intervals[1], vert=1, whis=1.5)
#
plt.setp(bp2['boxes'], color='red')
plt.setp(bp2['whiskers'], color='red', linestyle='-')
plt.setp(bp2['fliers'], markersize=3.0)

# Adds a horizontal grid to the plot.
ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',alpha=0.5)

# Hide the grid behind plot objects
ax1.set_axisbelow(True)
#ax1.set_title(graph_title[0])
#ax1.set_xlabel(xlabels[0])
ax1.set_ylabel(ylabels[0])

ax2.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',alpha=0.5)
# Hide the grid behind plot objects
ax2.set_axisbelow(True)
#ax2.set_title(graph_title[1])
ax2.set_xlabel(xlabels[1])
ax2.set_ylabel(ylabels[1])


# Set the axes ranges and axes labels
ax1.set_xlim(0.5, numBoxes + 0.5)
top = 15
bottom = 0
ax1.set_ylim(bottom, top)
xtickNames = plt.setp(ax1, xticklabels=labels)
plt.setp(xtickNames, fontsize=8)


ax2.set_xlim(0.5, numBoxes + 0.5)
#top = 15
#bottom = 0
#ax2.set_ylim(bottom, top)
xtickNames = plt.setp(ax2, xticklabels=labels)
plt.setp(xtickNames, fontsize=8)

plt.savefig(pathname+outfilename)
plt.show()

