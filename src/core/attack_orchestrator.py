import json
import getopt
import dpkt
from utils.sleep_functions import *
from timekeeper_functions import *
from shared_buffer import *
from logger import *
from defines import *


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


class AttackOrchestrator:

    def __init__(self, attkPlanDirPath, netCfgFile, runTime, proxyIP):
        self.attkPlanDirPath = attkPlanDirPath
        self.netCfgFile = netcfgFile
        self.runTime = runTime
        self.proxyIP = proxyIP
        self.extractIPMapping()
        self.init_shared_buffers()
        self.involved_replay_nodes = {}

    def extractIPMapping(self):
        self.mininet_node_ids = []
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

            self.mininet_node_ids.append(splitLs[0])

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

        for node_id in self.mininet_node_ids:
            result = self.sharedBufferArray.open(bufName=node_id + "-replay" + "main-cmd-channel-buffer", isProxy=True)
            if result == BUF_NOT_INITIALIZED or result == FAILURE:
                print "Cmd channel buffer open failed! "
                sys.exit(0)

    def send_to_main_process(self, msg):
        ret = 0
        while ret <= 0:
            ret = self.sharedBufferArray.write("cmd-channel-buffer", msg, 0)

    def recv_from_main_process(self):
        recv_msg = ''
        dummy_id, recv_msg = self.sharedBufferArray.read("cmd-channel-buffer")
        return recv_msg

    def signal_pcap_replay_trigger(self, node_id, pcap_file_path):
        ret = 0
        while ret <= 0:
            ret = self.sharedBufferArray.write(node_id + "-replay" + "main-cmd-channel-buffer", pcap_file_path, 0)
        #print "Signalled start of replay phase to node:", node_id

    def extract_involved_replay_nodes(self, replay_pcap_f_name):
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

    def run_emulation_phase(self, emulation_phase_id):

        hostIDs = self.PowerSimIdMapping.keys()

        return_val = FINISH

        print "Attack Orchestrator: Starting Emulation Phase with ID = ", emulation_phase_id
        for host in hostIDs :
            ret = 0
            while ret <= 0:
                ret = self.sharedBufferArray.write(str(host) + "attk-channel-buffer","EMULATE:" + str(emulation_phase_id), 0)

        print "Attack Orchestrator: Waiting for Emulation Phase to Complete ..."
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
                sleep(0.5)

        return return_val

    def wait_for_loaded_pcap_msg(self):
        outstanding_node_ids = self.mininet_node_ids[:]
        print "outstanding_node_ids:", outstanding_node_ids

        while outstanding_node_ids:
            for node_id in outstanding_node_ids:
                msg = ''
                dummy_id, msg = self.sharedBufferArray.read(str(node_id) + "-replay" + "main-cmd-channel-buffer")
                if msg == "LOADED":
                    outstanding_node_ids.remove(node_id)
                    print "Got a message from node:", node_id, "outstanding_node_ids now:", outstanding_node_ids

    def run(self):
        self.start_time = get_current_virtual_time()
        self.wait_for_loaded_pcap_msg()
        self.send_to_main_process("PCAPS-LOADED")

        while True:
            recv_msg = self.recv_from_main_process()
            if recv_msg == "START":
                break
            sleep(0.5)


        with open(self.attkPlanDirPath + "/attack_plan.json", "r") as f:
            self.attack_plan = json.load(f)

        #print "Attack plan:", self.attack_plan

        for stage_dict in self.attack_plan:

            if stage_dict["active"] == "false":
                continue

            if stage_dict["type"] == "replay":
                
                self.send_to_main_process("START-REPLAY")
                print "Attack Orchestrator: Signalled Start of Next Replay Phase: Pcap = ", stage_dict["pcap_file_path"]
                while True:
                    recv_msg = self.recv_from_main_process()
                    if recv_msg == "ACK":
                        break
                    sleep(0.5)
                
                for node_id in stage_dict["involved_nodes"]:
                    self.signal_pcap_replay_trigger(node_id, stage_dict["pcap_file_path"])
                    
                print "Attack Orchestrator: Waiting for Replay Phase to complete ..."
                for node_id in stage_dict["involved_nodes"]:
                    recv_msg = ''
                    while recv_msg != "DONE":
                        if get_current_virtual_time() - self.start_time >= self.runTime:
                            print "Attack Orchestrator: Run time Expired. Stopping ..."
                            sys.exit(0)                    
                        dummy_id, recv_msg = self.sharedBufferArray.read(node_id + "-replay" + "main-cmd-channel-buffer")
                        sleep(0.5)

                self.send_to_main_process("END-REPLAY")
                print "Attack Orchestrator: Signalled End of Last Replay Phase"
                while True:
                    recv_msg = self.recv_from_main_process()
                    if recv_msg == "ACK":
                        break
                    sleep(0.5)

            if stage_dict["type"] == "emulation":
                result = self.run_emulation_phase(stage_dict["emulation_phase_id"])

        print "Attack Orchestrator: Finished Executing Attack Plan. Stopping Attack Orchestrator..."
        sys.exit(0)


if __name__ == "__main__":
    attkPlanDirPath, netcfgFile, runTime, proxyIP = parseOpts()
    attk_orchestrator = AttackOrchestrator(attkPlanDirPath, netcfgFile, runTime, proxyIP)
    assert attk_orchestrator != None
    sys.exit(attk_orchestrator.run())
