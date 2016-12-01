import network_features as nf
from power_features import power_features as pf
import os

filepath = '/Users/kartik/Desktop/Siebel Project/microgrid_with_background_traffic/tapped/'

def feature_list(filepath):
	train_folder = filepath + 'train/'
	attack_folder = filepath + 'attack/'
	data = {}

	pcap_files_train = os.listdir(train_folder)
	pcap_files_attack = os.listdir(attack_folder)

	feature_list = []
	for i in range(0,len(pcap_files_train)):
		current_file = train_folder+pcap_files_train[i]
		power_series = pf(current_file)
		dst_list, start, end = nf.dst_list(current_file)
		network_series = nf.network_features(current_file, dst_list, start,end)

		for node in power_series:
			feature_list.append(power_series[node])
		for node in network_series:
			feature_list.append(network_series[node][0])
			feature_list.append(network_series[node][1])
			feature_list.append(network_series[node][2])

	data['train'] = feature_list	

	feature_list = []
	for i in range(0,len(pcap_files_attack)):
		current_file = attack_folder+pcap_files_attack[i]
		power_series = pf(current_file)
		dst_list, start, end = nf.dst_list(current_file)
		network_series = nf.network_features(current_file, dst_list, start,end)

		for node in power_series:
			feature_list.append(power_series[node])
		for node in network_series:
			feature_list.append(network_series[node][0])
			feature_list.append(network_series[node][1])
			feature_list.append(network_series[node][2])	
	data['attack'] = feature_list
	
	return data

#print feature_list(filepath)