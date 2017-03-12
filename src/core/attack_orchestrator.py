import sys
import os
from pcapfile import savefile
import fnmatch
import shared_buffer
from shared_buffer import *
from logger import *
import time
import getopt
import socket
from defines import *
import dpkt

from dpkt.loopback import Loopback
from dpkt.ethernet import Ethernet
from timekeeper_functions import *

DUMMY_ID = 0
FINISH = 1
STOP = -1


def usage():
    print "python attack_dispatcher.py <options>"
    print "Options:"
    print "-h or --help"
    print "-c or --attkplan-file-dir=    Absolute path to directory containing attack plan file <required>"
    print "-l or --netcfg-file=     Absolute path to netcfg File <required>"
    print "-r or --run-time=    Run time of host in seconds before it is shut-down <optional - default forever>"
    print "-p or --proxy-ip=     IP Address of proxy <optional - default 127.0.0.1>"

    sys.exit(0)

def parseOpts():
    netcfgFile = None
    runTime = 0
    proxyIP = DEFAULT_PROXY_IP
    attkPlanDirPath = "/home/ubuntu/Desktop/Workspace/NetPower_TestBed"

    try:
        (opts, args) = getopt.getopt(sys.argv[1:],
                                     "hc:l:r:p:",
                                     ["help", "attkplan-file-dir=", "netcfg-file=", "run-time=", "proxy-ip="])
    except getopt.GetoptError as e:
        print (str(e))
        usage()
        return 1
    for (o, v) in opts:
        if o in ("-h", "--help"):
            usage()

        if o in ("-c", "--attkplan-file-dir="):
            attkPlanDirPath = str(v)
        if o in ("-l", "--netcfg-file="):
            netcfgFile = str(v)
        if o in ("-r", "--run-time="):
            runTime = int(v)

        if o in ("-p", "--proxy-ip="):
            proxyIP = str(v)

    assert (attkPlanDirPath != None)
    return (attkPlanDirPath, netcfgFile, runTime, proxyIP)


class attack_orchestrator():


    def __init__(self, attkPlanDirPath, netCfgFile, runTime, proxyIP):
        self.attkPlanDirPath = attkPlanDirPath
        self.netCfgFile = netcfgFile
        self.runTime = runTime
        self.proxyIP = proxyIP
        self.extractIPMapping()
        self.init_shared_buffers()
        self.involved_replay_nodes = {}



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

            result = self.sharedBufferArray.open(bufName=str(hostID) + "attk-channel-buffer", isProxy=True)
            if result == BUF_NOT_INITIALIZED or result == FAILURE:
                print "Shared Buffer open failed! Buffer not initialized for host: " + str(hostID)
                sys.exit(0)

        result = self.sharedBufferArray.open(bufName="cmd-channel-buffer",isProxy=True)

        if result == BUF_NOT_INITIALIZED or result == FAILURE:
            print "Cmd channel buffer open failed! "
            sys.exit(0)

    def signal_end_of_replay_phase(self):

        ret = 0
        while ret <= 0 :
            ret = self.sharedBufferArray.write("cmd-channel-buffer","END",0)

        print "Signalled end of replay phase ..."

    def signal_start_of_replay_phase(self):

        ret = 0
        while ret <= 0 :
            ret = self.sharedBufferArray.write("cmd-channel-buffer","START",0)
        print "Signalled start of replay phase ..."


    def extract_involved_replay_nodes(self,replay_pcap_f_name):
        assert os.path.isfile(self.attkPlanDirPath + "/" + replay_pcap_f_name)
        self.involved_replay_nodes[replay_pcap_f_name] = []

        pcapFilePath = self.attkPlanDirPath + "/" + replay_pcap_f_name
        replay_pcap_reader = dpkt.pcap.Reader(open(pcapFilePath, 'rb'))


        l2_type = replay_pcap_reader.datalink()

        for ts, curr_pkt in replay_pcap_reader:

            if l2_type == dpkt.pcap.DLT_NULL:
                src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt, dpkt.pcap.DLT_NULL)
            elif l2_type == dpkt.pcap.DLT_LINUX_SLL:
                src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt, dpkt.pcap.DLT_LINUX_SLL)
            else:
                src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt)

            try:
                srchostID = self.IPToHostMapping[src_ip]
                dstHostID = self.IPToHostMapping[dst_ip]

                if srchostID not in self.involved_replay_nodes[replay_pcap_f_name]:
                    self.involved_replay_nodes[replay_pcap_f_name].append(srchostID)

                if dstHostID not in self.involved_replay_nodes[replay_pcap_f_name]:
                    self.involved_replay_nodes[replay_pcap_f_name].append(dstHostID)

            except:
                pass




    def run_replay_phase(self,replay_pcap_f_name):


        print "Loading Replay Phase for Pcap File = ", replay_pcap_f_name
        return_val = FINISH

        print "Involved Nodes = ", self.involved_replay_nodes[replay_pcap_f_name]
        for nodeID in self.involved_replay_nodes[replay_pcap_f_name] :
            ret = 0
            while ret <= 0 :
                ret = self.sharedBufferArray.write(str(nodeID) + "attk-channel-buffer", "REPLAY:" + str(self.attkPlanDirPath + "/" + replay_pcap_f_name), 0)



        for nodeID in self.involved_replay_nodes[replay_pcap_f_name] :

            if return_val == STOP:
                break

            recv_msg = ''
            while "LOADED" not in recv_msg:
                if get_current_virtual_time() - self.start_time >= self.runTime:
                    print "Run time Expired. Stopping ..."
                    return_val = STOP
                    break
                dummy_id, recv_msg = self.sharedBufferArray.read(str(nodeID) + "attk-channel-buffer")


        print "Loaded pcap for the current stage ..."
        for nodeID in self.involved_replay_nodes[replay_pcap_f_name] :
            ret = 0
            while ret <= 0 :
                ret = self.sharedBufferArray.write(str(nodeID) + "attk-channel-buffer", "START", 0)
                time.sleep(0.1)


        print "Waiting for Replay Phase to Complete ..."
        for nodeID in self.involved_replay_nodes[replay_pcap_f_name] :

            if return_val == STOP:
                break
            recv_msg = ''
            while "DONE" not in recv_msg:
                if get_current_virtual_time() - self.start_time >= self.runTime:
                    print "Run time Expired. Stopping ..."
                    return_val = STOP
                    break
                dummy_id, recv_msg = self.sharedBufferArray.read(str(nodeID) + "attk-channel-buffer")

        return return_val


    def run_emulation_phase(self,emulation_phase_id):

        hostIDs = self.PowerSimIdMapping.keys()
        return_val = FINISH

        print "Starting Emulation Phase with ID = ", emulation_phase_id
        for host in hostIDs :
            ret = 0
            while ret <= 0:
                ret = self.sharedBufferArray.write(str(host) + "attk-channel-buffer","EMULATE:" + str(emulation_phase_id), 0)

        print "Waiting for Emulation Phase to Complete ..."
        for host in hostIDs :
            if return_val == STOP:
                break
            recv_msg = ''
            while recv_msg != "DONE":
                if get_current_virtual_time() - self.start_time >= self.runTime:
                    print "Run time Expired. Stopping ..."
                    return_val = STOP
                    break
                dummy_id, recv_msg = self.sharedBufferArray.read(str(host) + "attk-channel-buffer")

        return return_val

    def run(self):

        time.sleep(5)
        assert os.path.exists(self.attkPlanDirPath)
        assert os.path.isfile(self.attkPlanDirPath + "/attack_plan.txt")

        with open(self.attkPlanDirPath + "/attack_plan.txt", "r") as f:
            stages = f.readlines()

        self.start_time = get_current_virtual_time()

        for stage in stages :
            curr_stage = stage.rstrip('\r\n')

            if curr_stage.startswith("#"):
                continue
            elif curr_stage.endswith(".pcap") :
                replay_pcap_f_name = curr_stage
                self.extract_involved_replay_nodes(replay_pcap_f_name)
                self.signal_start_of_replay_phase()
                result = self.run_replay_phase(replay_pcap_f_name)
                self.signal_end_of_replay_phase()
            else:

                print "curr_stage:", curr_stage

                emulation_phase_id = curr_stage
                result = self.run_emulation_phase(emulation_phase_id)

            if result == STOP:
                print "Stopping Attack Orchestrator at: ", curr_stage, " stage due to Run time Expiry"
                sys.exit(0)

        print "Finished Executing Attack Plan. Stopping Attack Orchestrator..."
        sys.exit(0)





if __name__ == "__main__":
    attkPlanDirPath, netcfgFile, runTime, proxyIP = parseOpts()
    attk_orchestrator = attack_orchestrator(attkPlanDirPath, netcfgFile, runTime, proxyIP)
    assert attk_orchestrator != None
    sys.exit(attk_orchestrator.run())
