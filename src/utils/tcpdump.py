import argparse
import pcapy
import dpkt
import time
import datetime
import os
from sleep_functions import *
import socket

class TCPDump(object):

    def __init__(self, intf_name, out_pcap_file_path):
        self.intf_name = intf_name
        self.out_pcap_file_path = out_pcap_file_path
        self.pcap_writer = None
        self.packet_count = 0
        pid = str(os.getpid())
        file('tcpdump'+self.intf_name, 'w').write(pid)

    def start_capture(self):
        self.pcap_writer = dpkt.pcap.Writer(open(self.out_pcap_file_path, "w"))
        p = pcapy.open_live(self.intf_name, 65535, True, 1)
        #p.setnonblock(0)
        while True :
            try:
                header,data = p.next()
                if header != None :
                    self.handle_packet(header,data)
                #time.sleep(0.5)
            except socket.timeout:
                #time.sleep(0.01)
                continue
                

        #try:
        #p.loop(-1, self.handle_packet)
        #except:
        #    self.pcap_writer.close()
        #    print "Wrote:", self.packet_count, "packets to file:", self.out_pcap_file_path

    def handle_packet(self, header, data):
        #ts = (datetime.datetime.now() - datetime.datetime(1970,1,1)).total_seconds()
        ts = get_current_vt()
        #ts = get_current_vt_specified_pid(os.getppid())
        #ts = time.time()
        pid = str(os.getpid())
        file('tcpdump'+self.intf_name, 'w').write(pid)
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
    time.sleep(2)
    td.start_capture()

if __name__ == "__main__":
    main()

