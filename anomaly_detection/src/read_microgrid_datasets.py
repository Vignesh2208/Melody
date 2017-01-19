import network_features as nf
from utils import *
from power_features import power_features as pf
import os
from os.path import dirname
import numpy as np

scriptDir = os.path.dirname(os.path.realpath(__file__))


def extract_features(filepath=dirname(scriptDir)+ "/datasets/microgrid_datasets",scenario_name="all_taps", feature_subsets = 'all'):
	train_folder = filepath + '/train/' + scenario_name + "/"
	attack_folder = filepath + '/attack/'
	data = {}

	pcap_files_train = os.listdir(train_folder)
	pcap_attack_subdirs = []
	for d in os.listdir(attack_folder) :
		if os.path.isdir(attack_folder + d) :
			pcap_attack_subdirs.append(d)


	print "Extracting features for Training ..."

	feature_list = []
	train_power_series_keys = {}
	train_network_series_keys = {}
	n_network_features = {}
	for i in range(0,len(pcap_files_train)):
		current_file = train_folder+pcap_files_train[i]
		train_power_series = pf(current_file)

		train_power_series_keys[i] = []
		train_network_series_keys[i] = []

		train_dst_list, start, end = nf.dst_list(current_file)
		train_network_series = nf.network_features(current_file, train_dst_list, start,end)


		if feature_subsets != 'network':
			for node in train_power_series:

				train_power_series_keys[i].append(node)
				feature_list.append(np.array(train_power_series[node]))

		if feature_subsets != 'power' :

			for node in train_network_series:

				train_network_series_keys[i].append(node)
				n_network_features[node] = len(train_network_series[node])

				for k in xrange(0, len(train_network_series[node])) :
					feature_list.append(np.array(train_network_series[node][k]))




	trainfeatureTimeSeries = []
	nSamples = len(feature_list[0])
	#nSamples = 300
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


	nAttkSamples = {}

	for attackType in pcap_attack_subdirs :

		print "Extracting features for attack type: ", attackType
		attk_type_dir = attack_folder + attackType + "/" + scenario_name + "/"
		pcap_files_attack = os.listdir(attk_type_dir)

		if attackType == "breaker":
			continue

		data['Attack'][attackType] = []
		nAttkSamples[attackType] = 1000000

		print "nAttk pcap files = ", len(pcap_files_attack)
		for i in range(0,len(pcap_files_attack)):
			current_file = attk_type_dir + pcap_files_attack[i]
			power_series = pf(current_file)
			dst_list, start, end = nf.dst_list(current_file)
			network_series = nf.network_features(current_file, dst_list, start,end)


			if feature_subsets != 'power' :
				for node in network_series :

					for k in xrange(0,len(network_series[node])) :
						if nAttkSamples[attackType] > len(network_series[node][k]) :
							nAttkSamples[attackType] = len(network_series[node][k])


			if feature_subsets != 'network' :
				for node in power_series :
					if len(power_series[node]) < nAttkSamples[attackType]:
						nAttkSamples[attackType] = len(power_series[node])

				for node in train_power_series_keys[i]:


					if node not in power_series.keys() :
						data['Attack'][attackType].append([0.0]*nAttkSamples[attackType])
					else:
						data['Attack'][attackType].append(np.array(power_series[node][0:nAttkSamples[attackType]]))


			if feature_subsets != 'power' :
				for node in train_network_series_keys[i]:

					if node not in network_series.keys():
						for k in xrange(0,n_network_features[node]) :
							data['Attack'][attackType].append([0.0]*nAttkSamples[attackType])
					else:

						for k in xrange(0,len(network_series[node])) :
							data['Attack'][attackType].append(np.array(network_series[node][k][0:nAttkSamples[attackType]]))


		curr_attack_timeseries = []
		print "Normalizing samples for Attack Type :", attackType
		feature_list = data['Attack'][attackType]
		print "Attk Samples = ", nAttkSamples[attackType], " nFeatures = ", nFeatures

		for idx in xrange(0, nAttkSamples[attackType]):
			curr_idx_values = []
			for feature in xrange(0, nFeatures):
				curr_idx_values.append(feature_list[feature][idx])

			curr_attack_timeseries.append(curr_idx_values)
			curr_attack_data = curr_attack_timeseries
			curr_attack_data = normalize(curr_attack_timeseries,featureMax)

		data['Attack'][attackType] = curr_attack_data



	print "Feature Extraction Completed ..."
	trainingData = trainfeatureTimeSeries
	trainingData = normalize(trainfeatureTimeSeries, featureMax)
	data['Train'] = trainingData

	return data,0

