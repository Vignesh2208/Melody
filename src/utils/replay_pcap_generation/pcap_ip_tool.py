import dpkt
import sys
import argparse
import socket
import json
from dpkt.loopback import Loopback
from dpkt.ethernet import Ethernet
from dpkt.sll import SLL


def defines.inet_to_str(inet):
    """Convert inet object to a string
        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)


def defines.str_to_inet(str):
    """Convert string object to an inet
        Args:
            str: Printable/readable IP address
        Returns:
            inet (inet struct): inet network address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_pton(socket.AF_INET, str)
    except ValueError:
        return socket.inet_pton(socket.AF_INET6, str)


def get_src_dst_ip_str(ip):
    """
    :param buf: A string buffer containing the entire packet
    :return: A tuple with source and destination IP strings
    """

    return defines.inet_to_str(ip.src), defines.inet_to_str(ip.dst)


class PCAPIPTool(object):

    def __init__(self, input_pcap_file_path):
        self.input_pcap_file_path = input_pcap_file_path

    def generate_mapped_pcap(self, ip_mappings, output_pcap_file_path):
        """
        :param ip_mappings: A dictionary where keys are IP address strings desired to be mapped to value strings
        :param mapped_pcap_file_path: The path of output PCAP file.
        :return: None
        """

        pcap_reader = dpkt.pcap.Reader(open(self.input_pcap_file_path, "rb"))
        l2_type = pcap_reader.datalink()

        pcap_writer = dpkt.pcap.Writer(open(output_pcap_file_path, "w"), linktype=l2_type)

        for ts, buf in pcap_reader:

            l2 = None

            # Unpack the data within the Ethernet frame (the IP packet)
            # Pulling out src, dst, length, fragment info, TTL, and Protocol
            
            if l2_type == dpkt.pcap.DLT_NULL:
                l2 = Loopback(buf)
            elif l2_type == dpkt.pcap.DLT_LINUX_SLL:
                l2 = SLL(buf)
            else:
                l2 = Ethernet(buf)

            l2.unpack(buf)
            modified_ip = l2.data

            src_ip_str, dst_ip_str = get_src_dst_ip_str(l2.data)
            print ("IP: %s -> %s ' % (src_ip_str, dst_ip_str))

            if src_ip_str in ip_mappings:
                modified_ip.src = defines.str_to_inet(ip_mappings[src_ip_str])

            if dst_ip_str in ip_mappings:
                modified_ip.dst = defines.str_to_inet(ip_mappings[dst_ip_str])

            modified_ip.len = len(modified_ip)
            modified_ip.sum = 0x0000

            l2.data = str(modified_ip)

            pcap_writer.writepkt(str(l2), ts)

        pcap_writer.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_pcap_path', dest="input_pcap_path", default="test.pcap")
    parser.add_argument('--output_pcap_path', dest="output_pcap_path", default="test_modified.pcap")
    parser.add_argument('--ip_mapping_json_path', dest="ip_mapping_json_path", default="example_mapping.json")

    args = parser.parse_args()
    in_filepath = args.input_pcap_path
    out_filepath = args.output_pcap_path

    with open(args.ip_mapping_json_path) as f:
        ip_mapping_dict = json.load(f)
        t = PCAPIPTool(in_filepath)
        t.generate_mapped_pcap(ip_mapping_dict, out_filepath)

if __name__ == "__main__":
    main()
