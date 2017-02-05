import argparse
import pcapy
import dpkt
import time


class TCPDump(object):

    def __init__(self, intf_name, out_pcap_file_path):
        self.intf_name = intf_name
        self.out_pcap_file_path = out_pcap_file_path
        self.pcap_writer = None
        self.packet_count = 0

    def start_capture(self):
        self.pcap_writer = dpkt.pcap.Writer(open(self.out_pcap_file_path, "w"))
        p = pcapy.open_live(self.intf_name, 65536, True, 1)
        p.loop(-1, self.handle_packet)

    def handle_packet(self, header, data):
        ts = time.time()
        self.pcap_writer.writepkt(data, ts)
        self.packet_count += 1

    def __del__(self):
        self.pcap_writer.close()
        print "Wrote:", self.packet_count, "packets to file:", self.out_pcap_file_path


def main():
    parser = argparse.ArgumentParser(description="Capture packets from interfaces.")
    parser.add_argument('-i', dest="intf_name", help="Interface name.", required=True)
    parser.add_argument('-w', dest="out_pcap_file_path", help="Output PCAP file path.", required=True)

    args = parser.parse_args()

    print "Starting capture on intf:", args.intf_name, "saving to file:", args.out_pcap_file_path
    td = TCPDump(args.intf_name, args.out_pcap_file_path)
    td.start_capture()

if __name__ == "__main__":
    main()

