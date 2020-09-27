import dpkt
from argparse import ArgumentParser
from srcs.proto import css_pb2
import pandas as pd
import plotly.offline as py
import plotly.graph_objs as go


def process_pcap(pcap_file,keys_to_plot):
	
	pcap = dpkt.pcap.Reader(open(pcap_file))
	pkt_parsed = css_pb2.CyberMessage()

	unique_app_id_pairs = []

	data_fields = ['timestamp','src_dst'] + keys_to_plot

	pcap_dataframe = pd.DataFrame(columns=data_fields)

	for timestamp, buf in pcap:

		#unpack the ethernet frame
		eth = dpkt.ethernet.Ethernet(buf)
		ip = eth.data
		
		#we are only intersted in the UDP packets that follow our custom protocol
		if ip.p == dpkt.ip.IP_PROTO_UDP:
		
			udp_payload = ip.data.data
			pkt_parsed.ParseFromString(str(udp_payload))
			#extract the source-dst application ID pair
			src_application_id = pkt_parsed.src_application_id
			dst_application_id = pkt_parsed.dst_application_id

			pcap_dataframe_entry = [timestamp, (src_application_id,dst_application_id)]

			if (src_application_id,dst_application_id) not in unique_app_id_pairs:
				unique_app_id_pairs.append((src_application_id,dst_application_id))

			#Finish this function for when the key requested is not in the packet
			for key in keys_to_plot:
				for content in pkt_parsed.content:
					if content.key == key:
						pcap_dataframe_entry.append(float(content.value))
		
			df_append = pd.DataFrame([pcap_dataframe_entry], columns=data_fields)
			pcap_dataframe = pd.concat([pcap_dataframe, df_append], axis=0)
	
	start_time = pcap_dataframe['timestamp'].iloc[0]
	pcap_dataframe['rel_time'] = pcap_dataframe['timestamp'] - start_time
	#convert unix time to pandas datetime
	#pcap_dataframe['time'] = pd.to_datetime(pcap_dataframe['timestamp'],unit='ms',origin='unix')
	# Reset Index
	pcap_dataframe = pcap_dataframe.reset_index()
	# Drop old index column
	pcap_dataframe = pcap_dataframe.drop(columns="index")

	return pcap_dataframe, unique_app_id_pairs

def physical_measurement_plotter(dataframe, src_dst_pairs,keys_to_plot):

	#fix the code to work for multiple keys
	for key in keys_to_plot:
		data =[]
		for src_dst in src_dst_pairs:
			pcap_dataframe_src_dst = dataframe[dataframe.src_dst == src_dst]

			data.append(go.Scatter(x=pcap_dataframe_src_dst['rel_time'], y=pcap_dataframe_src_dst[key], name=str(src_dst[0] + ',' + src_dst[1])))

		layout = go.Layout(
		    xaxis=dict(
		        title='Time since start of emulation',
		        showticklabels=True,		        
		    ),
		    yaxis=dict(
		        title=key,
		        showticklabels=True,
		    )
		)
		fig = go.Figure(data=data, layout =layout)
	
	py.plot(fig, filename = 'physical_measurement_plot.html')
	
if __name__ == "__main__":

	parser = ArgumentParser(description='Visualize data from a given pcap file')
	parser.add_argument('-f','--filename', required=True, help="name of .pcap file that needs analysis")
	parser.add_argument('-k','--keys', action='append', help='keys that you wish to plot the time series for', required=True)
	args = parser.parse_args()
	pcap_file = args.filename
	keys_to_plot = args.keys
	pcap_dataframe, unique_app_id_pairs = process_pcap(pcap_file,keys_to_plot)
	physical_measurement_plotter(pcap_dataframe,unique_app_id_pairs,keys_to_plot)

