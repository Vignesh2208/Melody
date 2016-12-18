import time
import threading
import random

from timeit import default_timer as timer

NETWORK_SCAN_NMAP_PORT = 'Nmap-port'


class NetworkScanEvent(threading.Thread):

    def __init__(self, src_mn_node, dst_mn_node, type, offset, duration):
        '''
        'type' determines the following:
            - NETWORK_SCAN_NMAP_ARP:
            - NETWORK_SCAN_NMAP_PORT:

        'offset' determines how long after the thread started, the traffic is generated.

        'src_mn_node' defines where the scan traffic originates
        '''

        super(NetworkScanEvent, self).__init__()

        self.src_mn_node = src_mn_node
        self.dst_mn_node = dst_mn_node
        self.type = type
        self.offset = offset
        self.duration = duration

        self.start_time = None
        self.elasped_time = None

    def trigger_scan(self):

        cmd = None
        if self.type == NETWORK_SCAN_NMAP_PORT:
            cmd = "nmap -T5 --disable-arp-ping -p 1-65535 " + self.dst_mn_node.IP()

        print "Scan cmd:", cmd
        self.client_popen = self.src_mn_node.popen(cmd)

        print "Waiting for duration:", self.duration
        time.sleep(self.duration)

        print "Terminating cmd:", cmd
        self.client_popen.terminate()

    def run(self):

        print "Starting NetworkScanEvent thread..."

        self.start_time = timer()

        # First wait for offset seconds
        time.sleep(self.offset)

        # Start the server process
        self.trigger_scan()
