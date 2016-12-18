import dpkt
from array import array

#filename='/Users/kartik/Desktop/Siebel Project/microgrid_with_background_traffic/s1-eth2-s2-eth2.pcap'

def power_features(filename):
	node_measures = {}
	node_id_list = []

	i = 0
	start_ts = 0

	for ts, pkt in dpkt.pcap.Reader(open(filename,'r')):
		if i == 0:
			start_ts = ts
		end_ts = ts
		i+=1

	for ts, pkt in dpkt.pcap.Reader(open(filename,'r')):
		eth=dpkt.ethernet.Ethernet(pkt) 
		
		if eth.type!=dpkt.ethernet.ETH_TYPE_IP:
			continue

		ip=eth.data

		if ip.p == dpkt.ip.IP_PROTO_UDP and ip.data.dport == 5100:
			node_id_length = int(ip.data.data[:10])
			node_id = ip.data.data[10:(10+node_id_length)]
			measurement = float(ip.data.data[(10+node_id_length):])

			if node_id in node_measures.keys():
				pass
			else:
				node_measures[node_id] = [0] * (int(end_ts-start_ts)+1)
				node_id_list.append(node_id)

			#print node_measures[node_id][]
			node_measures[node_id][int(ts-start_ts)] = measurement

	for node in node_id_list:
		for i in range(0,int(end_ts-start_ts)+1):
			if node_measures[node][i] == 0:
				node_measures[node][i] = node_measures[node][i-1]

	return node_measures
