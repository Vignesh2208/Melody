import socket
import sys
import threading
import logger
from datetime import datetime

from defines import *


class basicHostAttackLayer(threading.Thread):
    def __init__(self, hostID, logFile, IPCLayer, NetworkServiceLayer,sharedBufferArray):

        threading.Thread.__init__(self)
        self.threadCmdLock = threading.Lock()
        self.threadCallbackLock = threading.Lock()

        self.threadCmdQueue = []
        self.threadCallbackQueue = {}
        self.nPendingCallbacks = 0
        self.sharedBufferArray = sharedBufferArray
        self.hostID = hostID
        self.log = logger.Logger(logFile, "Host " + str(hostID) + " Attack Layer Thread")
        self.IPCLayer = IPCLayer
        self.NetServiceLayer = NetworkServiceLayer
        self.IPMapping = self.NetServiceLayer.IPMap
        self.myIP = self.IPMapping[self.hostID][0]

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.rx_pkt_check = None
        self.rx_pkt_check_updated = False
        self.stopping = False

        self.attack_playback_thread_started = False
        self.running_emulate_stage = False
        self.running_replay_stage = False
        self.emulate_stage_id = "None"
        self.send_events = []
        self.recv_events = {}
        self.init_shared_attk_playback_buffer()

    def getcurrCmd(self):
        self.threadCmdLock.acquire()
        try:
            currCmd = self.threadCmdQueue.pop()
        except:
            currCmd = None
        self.threadCmdLock.release()
        return currCmd

    def cancelThread(self):
        self.threadCmdLock.acquire()
        self.threadCmdQueue.append(CMD_QUIT)
        self.threadCmdLock.release()

    def sendUDPMsg(self, pkt, IPAddr, Port):
        UDP_IP = IPAddr
        UDP_PORT = Port
        MESSAGE = str(pkt)
        self.log.info("%s  SEND_TO=%s:%s  PKT=%s" % (datetime.now(), str(UDP_IP), str(UDP_PORT), str(MESSAGE)))
        # str(datetime.now()) + " <SEND PKT> TO=" + str(UDP_IP) + ":" + str(UDP_PORT) + " FROM: " + str(self.hostID) + " PKT= " + str(MESSAGE))

        self.sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    def txPkt(self, pkt, dstNodeID):
        if dstNodeID in self.NetServiceLayer.IPMap.keys():
            IPAddr, Port = self.NetServiceLayer.IPMap[dstNodeID]
            self.sendUDPMsg(pkt, IPAddr, Port)

    def txAsyncNetServiceLayer(self, pkt, dstNodeID):
        self.txPkt(pkt, dstNodeID)

    def txAsyncIPCLayer(self, pkt):
        self.IPCLayer.runOnThread(self.IPCLayer.onRxPktFromAttackLayer, extractPowerSimIdFromPkt(pkt), pkt)

    # default - benign Attack Layer
    def onRxPktFromNetworkLayer(self, pkt):
        self.IPCLayer.runOnThread(self.IPCLayer.onRxPktFromAttackLayer, extractPowerSimIdFromPkt(pkt), pkt)

    # default - benign Attack Layer
    def onRxPktFromIPCLayer(self, pkt, dstNodeID):
        self.txAsyncNetServiceLayer(pkt, dstNodeID)

    def runOnThread(self, function, powerSimNodeID, *args):
        self.threadCallbackLock.acquire()
        if powerSimNodeID not in self.threadCallbackQueue.keys():
            self.threadCallbackQueue[powerSimNodeID] = []
            self.threadCallbackQueue[powerSimNodeID].append((function, args))
        else:
            if len(self.threadCallbackQueue[powerSimNodeID]) == 0:
                self.threadCallbackQueue[powerSimNodeID].append((function, args))
            else:
                self.threadCallbackQueue[powerSimNodeID][0] = (function, args)
        self.nPendingCallbacks = self.nPendingCallbacks + 1
        self.threadCallbackLock.release()

    def signal_end_of_emulate_stage(self):
        self.running_emulate_stage = False

        print "ENDING EMULATION STAGE: ", self.emulate_stage_id
        self.emulate_stage_id = "None"
        ret = 0
        while ret <= 0:
            ret = self.sharedBufferArray.write(self.attk_channel_bufName, "DONE", 0)

    def init_shared_attk_playback_buffer(self):
        self.attk_channel_bufName = str(self.hostID) + "attk-channel-buffer"
        #self.attk_channel_buffer = shared_buffer(bufName=self.attk_channel_bufName, isProxy=False)

        result = self.sharedBufferArray.open(self.attk_channel_bufName,isProxy=False)
        if result == BUF_NOT_INITIALIZED or result == FAILURE:
            print "Shared Buffer open failed! Buffer not initialized for host: " + str(self.hostID)
            sys.exit(0)
        else:
            self.log.info("Attk playback buffer open suceeded !")

    def check_emulation_stage(self):
        dummy_id, recv_msg = self.sharedBufferArray.read(self.attk_channel_bufName)
        if "EMULATE:" in recv_msg:
            self.running_emulate_stage = True
            self.emulate_stage_id = recv_msg.split(":")[1]
            print "STARTING NEW EMULATION STAGE WITH ID = ", self.emulate_stage_id

    def run(self):

        pktToSend = None
        self.log.info("Started at " + str(datetime.now()))
        sys.stdout.flush()

        assert (self.NetServiceLayer != None)
        assert (self.IPCLayer != None)
        while True:

            currCmd = self.getcurrCmd()
            if currCmd != None and currCmd == CMD_QUIT:
                self.log.info("Stopping " + str(datetime.now()))
                sys.stdout.flush()
                self.stopping = True
                break

            callbackFns = []
            self.threadCallbackLock.acquire()
            if self.nPendingCallbacks == 0:
                self.threadCallbackLock.release()
            else:

                values = list(self.threadCallbackQueue.values())
                for i in xrange(0, len(values)):
                    if len(values[i]) > 0:
                        callbackFns.append(values[i].pop())
                self.nPendingCallbacks = 0
                self.threadCallbackLock.release()

                for i in xrange(0, len(callbackFns)):
                    function, args = callbackFns[i]
                    function(*args)

            self.check_emulation_stage()
            self.idle()

        # can use this to send async pkts to Net layer and IPC layer
    def idle(self):
        pass





