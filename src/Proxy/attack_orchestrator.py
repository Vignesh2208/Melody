import sys
import os
from pcapfile import savefile
import fnmatch
import shared_buffer
from shared_buffer import *

scriptDir = os.path.dirname(os.path.realpath(__file__))
if scriptDir not in sys.path:
    sys.path.append(scriptDir)

srcDir = scriptDir + "/.."
if srcDir not in sys.path:
    sys.path.append(srcDir)

from logger import *
import time
import getopt
import socket
from defines import *
import dpkt
from dpkt.loopback import Loopback
from dpkt.ethernet import Ethernet

DUMMY_ID = 0


def usage():
    print "python attack_dispatcher.py <options>"
    print "Options:"
    print "-h or --help"
    print "-c or --pcap-file-dir=    Absolute path to directory containing pcap replay files <required>"
    print "-l or --netcfg-file=     Absolute path to netcfg File <required>"
    print "-r or --run-time=    Run time of host in seconds before it is shut-down <optional - default forever>"
    print "-p or --proxy-ip=     IP Address of proxy <optional - default 127.0.0.1>"

    sys.exit(0)

def parseOpts():
    netcfgFile = None
    runTime = 0
    proxyIP = DEFAULT_PROXY_IP
    pcapsDirPath = "/home/ubuntu/Desktop/Workspace/NetPower_TestBed"

    try:
        (opts, args) = getopt.getopt(sys.argv[1:],
                                     "hc:l:r:p:",
                                     ["help", "pcap-file-dir=", "netcfg-file=", "run-time=", "proxy-ip="])
    except getopt.GetoptError as e:
        print (str(e))
        usage()
        return 1
    for (o, v) in opts:
        if o in ("-h", "--help"):
            usage()

        if o in ("-c", "--pcap-file-dir="):
            pcapsDirPath = str(v)
        if o in ("-l", "--netcfg-file="):
            netcfgFile = str(v)
        if o in ("-r", "--run-time="):
            runTime = int(v)

        if o in ("-p", "--proxy-ip="):
            proxyIP = str(v)

    assert (pcapsDirPath != None)
    return (pcapsDirPath, netcfgFile, runTime, proxyIP)


class attack_orchestrator():


    def __init__(self, pcapDirPath, netCfgFile, runTime, proxyIP):
        self.pcapsDirPath = pcapDirPath
        self.netCfgFile = netcfgFile
        self.runTime = runTime
        self.proxyIP = proxyIP
        self.extractIPMapping()
        self.init_shared_buffers()



    def extractIPMapping(self):
        self.IPMapping = {}
        self.PowerSimIdMapping = {}
        self.IPToHostMapping = {}
        assert (os.path.isfile(self.netCfgFile) == True)
        lines = [line.rstrip('\n') for line in open(self.netCfgFile)]

        for line in lines:
            line = ' '.join(line.split())
            line = line.replace(" ", "")
            splitLs = line.split(',')
            assert (len(splitLs) >= 3)
            hostID = int(splitLs[0][1:])
            IPAddr = splitLs[1]
            Port = int(splitLs[2])

            self.IPMapping[hostID] = (IPAddr, Port)
            self.IPToHostMapping[IPAddr] = hostID
            for i in xrange(3, len(splitLs)):
                PowerSimId = str(splitLs[i])
                if hostID not in self.PowerSimIdMapping.keys():
                    self.PowerSimIdMapping[hostID] = []
                self.PowerSimIdMapping[hostID].append(PowerSimId)





    def init_shared_buffers(self):
        self.shared_bufs = {}
        hostIDS = self.PowerSimIdMapping.keys()
        self.sharedBufferArray = shared_buffer_array()
        for hostID in hostIDS :

            #sharedBufName = str(hostID) + "attk-channel-buffer"
            #self.shared_bufs[hostID] = shared_buffer(bufName=str(hostID) + "attk-channel-buffer", isProxy=True)
            result = self.sharedBufferArray.open(bufName=str(hostID) + "attk-channel-buffer", isProxy=True)
            #result = self.shared_bufs[hostID].open()
            if result == BUF_NOT_INITIALIZED or result == FAILURE:
                print "Shared Buffer open failed! Buffer not initialized for host: " + str(hostID)
                sys.exit(0)




    def replay_pkt(self,l2_type,curr_pkt,pkt_no):

        idx = pkt_no

        if l2_type == dpkt.pcap.DLT_NULL:
            src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt, 0)
            raw_ip_pkt = get_raw_ip_pkt(curr_pkt, 0)
        else:
            src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt)
            raw_ip_pkt = get_raw_ip_pkt(curr_pkt)

        try:
            srchostID = self.IPToHostMapping[src_ip]
            dstHostID = self.IPToHostMapping[dst_ip]
            print "Dispatching Next Attack pkt no = ", idx, " Len = ", len(raw_ip_pkt), "Src Host = ", srchostID, " Dst Host = ", dstHostID
            ret = 0

            pkt_hex_str = binascii.hexlify(raw_ip_pkt.__str__())
            #print "ip_payload = ", pkt_hex_str

            while ret <= 0:
                # ret = self.shared_bufs[dstHostID].write("RX:" + str(raw_ip_pkt),DUMMY_ID)
                ret = self.sharedBufferArray.write(str(dstHostID) + "attk-channel-buffer", "RX:" + str(pkt_hex_str), 0)

            ret = 0
            while ret <= 0:
                # ret = self.shared_bufs[srchostID].write("TX:" + str(raw_ip_pkt),DUMMY_ID)
                ret = self.sharedBufferArray.write(str(srchostID) + "attk-channel-buffer", "TX:" + str(pkt_hex_str), 0)

            print "Waiting for attk pkt simulation completion"

            recv_msg = ''
            while recv_msg != "ACK":
                if time.time() - self.start_time >= self.runTime:
                    print "run time Expired. Stopping ..."
                    sys.exit(0)
                # dummy_id, recv_msg = self.shared_bufs[dstHostID].read()
                dummy_id, recv_msg = self.sharedBufferArray.read(str(dstHostID) + "attk-channel-buffer")


        except Exception as e:
            print "Error in replaying pkt no: ", idx, " Error = ", str(e)
            sys.exit(0)


    def signal_end_of_replay_phase(self):


        hostIDS = self.PowerSimIdMapping.keys()
        for hostID in hostIDS :
            ret = 0
            while ret <= 0:
                ret = self.sharedBufferArray.write(str(hostID) + "attk-channel-buffer", "END", 0)

        print "Signalled end of replay phase ..."
        time.sleep(5.0)



    def run(self):
        assert os.path.exists(self.pcapsDirPath)


        replay_pcaps = fnmatch.filter(os.listdir(self.pcapsDirPath), 'replay*.pcap')
        replay_pcaps = sorted(replay_pcaps)
        self.start_time = time.time()
        for replay_pcap_f_name in replay_pcaps:
            pcapFilePath = self.pcapsDirPath + "/" + replay_pcap_f_name
            assert os.path.isfile(pcapFilePath)
            replay_pcap_reader = dpkt.pcap.Reader(open(pcapFilePath, 'rb'))

            print "Current Replay file = ", replay_pcap_f_name
            idx = 0
            l2_type = replay_pcap_reader.datalink()

            for ts,curr_pkt in replay_pcap_reader:

                if time.time() - self.start_time >= self.runTime:
                    print "Stopping ..."
                    sys.exit(0)

                self.replay_pkt(l2_type=l2_type,curr_pkt=curr_pkt,pkt_no=idx)
                idx = idx + 1


        self.signal_end_of_replay_phase()



if __name__ == "__main__":
    pcapDirPath, netcfgFile, runTime, proxyIP = parseOpts()

    attk_orchestrator = attack_orchestrator(pcapDirPath, netcfgFile, runTime, proxyIP)
    assert attk_orchestrator != None
    sys.exit(attk_orchestrator.run())
