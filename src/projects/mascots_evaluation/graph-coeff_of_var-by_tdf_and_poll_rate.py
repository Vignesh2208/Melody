"""
Script for coefficients of variation for latency and periodicity.
Run with Python 3.4.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import pylab as pl
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
	#pathname = "C:\\Users\\Elizabeth\\Documents\\Research Notes\\Siebel\\server_backup\\tdf_data\\"

# dnp3 polling intervals
dnp3ints = [10,100,1000]
# tdf values
tdf_vals = [1,5,10]
# measurement types 
measurement_list = ["latency","periodicity"]

# topology information 
sw = 10 			# number of switches 
hosts_per_sw = 4 	# number of hosts per switch

filename_lst = []
for m in measurement_list:
	for tdf in tdf_vals:
		for i in dnp3ints:
			filename_lst.append("tdf_"+str(tdf)+"-dnp3_"+str(i)+"ms-sw_"+str(sw)+"-h_"+str(hosts_per_sw)+"_"+str(m)+".csv")

print("Filenames:")
for filename in filename_lst:
	print("  "+filename)
			
labels = []
for i in dnp3ints:
	labels.append(str(i)+" ms")
print("DNP3 Interval Labels:")
for lbl in labels:
	print("  "+lbl)
	
list_sample_counts = []
list_means = []
list_stds = []
list_mins = []
list_maxs = []
list_data_sets = []

num_tdf_sets = len(tdf_vals)
num_dnp3_sets = len(dnp3ints)

for filename in filename_lst:
        #file = open(filename, “r”) 
        #print file.read()
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

# data1 for latency
#data1 = [list_data_sets[0], list_data_sets[1], list_data_sets[2], list_data_sets[3]]
latency_data = []
latency_by_tdf = []
tmp_results = []
num_tests = num_tdf_sets*num_dnp3_sets
print("\nLatency Calculations: ")
for i in range(num_tests):
		latency_data.append(list_data_sets[i])
		tmp_results.append(float(list_stds[i])/float(list_means[i]))
		print ("StDev: ",str(list_stds[i]),", Mean: ",str(list_means[i]),"; Result: ",str(tmp_results[int(i % num_dnp3_sets)]))
		if (((i+1) % num_dnp3_sets) == 0):
			latency_by_tdf.append(tmp_results)
			tmp_results = []

# data2 for periodicity
periodicity_data = []
periodicity_by_tdf = []
tmp_results = []
print("\nPeriodicity Calculations: ")
for i in range(num_tests,num_tests*2):
		periodicity_data.append(list_data_sets[i])
		tmp_results.append(float(list_stds[i])/float(list_means[i]))
		print ("StDev: ",str(list_stds[i]),", Mean: ",str(list_means[i]),"; Result: ",str(tmp_results[i%num_dnp3_sets]))
		if (((i+1) % num_dnp3_sets) == 0):
			periodicity_by_tdf.append(tmp_results)
			tmp_results = []

outfilename = 'graph_of_coeffs_of_var-log_scale.png'
lbl_size = 10
lbl_size2 = 10
dnp3_rates = [10, 100, 1000]

#fig, (ax1, ax2) = plt.subplots(1, 2)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6,5))

plot1 = ax1.plot(dnp3_rates, latency_by_tdf[0], 'r')
plot1b = ax1.plot(dnp3_rates, latency_by_tdf[0], 'ro', label = 'TDF = 1')
plot2 = ax1.plot(dnp3_rates, latency_by_tdf[1], 'g')
plot2b = ax1.plot(dnp3_rates, latency_by_tdf[1], 'go', label = 'TDF = 5')
plot3 = ax1.plot(dnp3_rates, latency_by_tdf[2], 'b')
plot3b = ax1.plot(dnp3_rates, latency_by_tdf[2], 'bo', label = 'TDF = 10')

ax1.set_title('Latency', fontsize=lbl_size)
ax1.set_xlabel('Poll Interval (ms)', fontsize=lbl_size)
ax1.set_ylabel('Coefficient of Variation (σ/μ)', fontsize=lbl_size)
ax1.set_ylim([-0.1,0.9])
ax1.set_xscale('log')
zed = [tick.label.set_fontsize(lbl_size2) for tick in ax1.xaxis.get_major_ticks()]
zed = [tick.label.set_fontsize(lbl_size2) for tick in ax1.yaxis.get_major_ticks()]

plot4 = ax2.plot(dnp3_rates, periodicity_by_tdf[0], 'r')
plot4b = ax2.plot(dnp3_rates, periodicity_by_tdf[0], 'ro', label = 'TDF = 1')
plot5 = ax2.plot(dnp3_rates, periodicity_by_tdf[1], 'g')
plot5b = ax2.plot(dnp3_rates, periodicity_by_tdf[1], 'go', label = 'TDF = 5')
plot6 = ax2.plot(dnp3_rates, periodicity_by_tdf[2], 'b')
plot6b = ax2.plot(dnp3_rates, periodicity_by_tdf[2], 'bo', label = 'TDF = 10')

ax2.set_title('Periodicity', fontsize=lbl_size)
ax2.set_xlabel('Poll Interval (ms)', fontsize=lbl_size)
ax2.set_xscale('log')
zed = [tick.label.set_fontsize(lbl_size2) for tick in ax2.xaxis.get_major_ticks()]
zed = [tick.label.set_fontsize(lbl_size2) for tick in ax2.yaxis.get_major_ticks()]

ax1.legend(loc = 'upper right')
plt.legend(loc = 'upper right')

plt.savefig(pathname+outfilename)
plt.show()

