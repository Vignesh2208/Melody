This simple tool can be used to replace IP addresses in PCAPs and remove the ethernet frame
to create new pcaps suitable for replaying with Melody.

Usage:

python pcap_ip_tool.py --input_pcap_path= --output_pcap_path= --ip_mapping_json_path=

Example Usage:

	>> python pcap_ip_tool.py

	It Generates a new test_mapped.pcap in this directory.
	It uses example_mapping.json and test.pcap files as input and replaces 
	"10.0.2.15" with "10.0.0.1" and "52.90.208.251" with "10.0.0.3"
        to create a new test_mapped.pcap file.
