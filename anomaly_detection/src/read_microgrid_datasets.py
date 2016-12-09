import network_features as nf
from utils import *
from power_features import power_features as pf
import os
from os.path import dirname
import numpy as np

scriptDir = os.path.dirname(os.path.realpath(__file__))


def extract_features(filepath=dirname(scriptDir)+ "/datasets/microgrid_datasets",scenario_name="all_taps"):
	train_folder = filepath + '/train/' + scenario_name + "/"
	attack_folder = filepath + '/attack/' + scenario_name + "/"
	data = {}

	pcap_files_train = os.listdir(train_folder)
	pcap_attack_subdirs = []
	for d in os.listdir(attack_folder) :
		if os.path.isdir(attack_folder + d) :
			pcap_attack_subdirs.append(d)


	print "Extracting features for Training ..."

	feature_list = []
	for i in range(0,len(pcap_files_train)):
		current_file = train_folder+pcap_files_train[i]
		power_series = pf(current_file)
		dst_list, start, end = nf.dst_list(current_file)
		network_series = nf.network_features(current_file, dst_list, start,end)

		for node in power_series:
			feature_list.append(np.array(power_series[node]))
		for node in network_series:
			feature_list.append(np.array(network_series[node][0]))
			feature_list.append(np.array(network_series[node][1]))
			feature_list.append(np.array(network_series[node][2]))



	trainfeatureTimeSeries = []
	nSamples = len(feature_list[0])
	nFeatures = len(feature_list)



	for feature in xrange(0,nFeatures) :

		if nSamples > len(feature_list[feature]) :
			nSamples = len(feature_list[feature])

	print "nSamples = ", nSamples

	for idx in xrange(0,nSamples) :
		curr_idx_values = []
		for feature in xrange(0,nFeatures) :
			curr_idx_values.append(feature_list[feature][idx])

		trainfeatureTimeSeries.append(curr_idx_values)


	data['Attack'] = {}

	print "Number of Training Samples = ", nSamples, " Number of Features = ", len(trainfeatureTimeSeries[0])
	print "Normalizing Training samples ..."
	nFeatures = len(trainfeatureTimeSeries[0])
	featureMax = []
	i = 0
	while i < nFeatures:
		maxVal = max(np.array(map(itemgetter(i), trainfeatureTimeSeries)), key=abs)
		if maxVal == 0:
			maxVal = 1
		featureMax.append(maxVal)
		i = i + 1




	for attackType in pcap_attack_subdirs :

		print "Extracting features for attack type: ", attackType
		attk_type_dir = attack_folder + attackType
		pcap_files_attack = os.listdir(attk_type_dir)
		data['Attack'][attackType] = []
		for i in range(0,len(pcap_files_attack)):
			current_file = attk_type_dir +pcap_files_attack[i]
			power_series = pf(current_file)
			dst_list, start, end = nf.dst_list(current_file)
			network_series = nf.network_features(current_file, dst_list, start,end)

			for node in power_series:
				data['Attack'][attackType].append(power_series[node])
			for node in network_series:
				data['Attack'][attackType].append(network_series[node][0])
				data['Attack'][attackType].append(network_series[node][1])
				data['Attack'][attackType].append(network_series[node][2])


		curr_attack_timeseries = []
		for idx in xrange(0, nSamples):
			curr_idx_values = []
			for feature in xrange(0, nFeatures):
				curr_idx_values.append(feature_list[feature][idx])

			curr_attack_timeseries.append(curr_idx_values)
			print "Normalizing samples for Attack Type :", attackType
			curr_attack_data = normalize(curr_attack_timeseries,featureMax)
		data['Attack'][attackType] = curr_attack_data



	print "Feature Extraction Completed ..."
	trainingData = normalize(trainfeatureTimeSeries, featureMax)
	data['Train'] = trainingData
	return data,0

#print feature_list(filepath)