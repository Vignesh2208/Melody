import shared_buffer
from shared_buffer import *
import sys
import os
import socket
import threading
import logger
import datetime
from datetime import datetime
from logger import Logger
from defines import *
import time
import Queue
from utils.sleep_functions import sleep


class basicHostIPCLayer(threading.Thread):
    def __init__(self, hostID, logFile,sharedBufferArray):
        threading.Thread.__init__(self)

        self.threadCmdLock = threading.Lock()
        self.threadCallbackQueue = {}
        self.threadCallbackLock = threading.Lock()
        self.nPendingCallbacks = 0

        self.threadCmdQueue = []
        self.hostID = hostID
        self.sharedBufferArray = sharedBufferArray
        self.log = logger.Logger(logFile, "Host " + str(hostID) + " IPC Thread")
        self.hostIDtoPowerSimID = None
        self.powerSimIDtohostID = None
        self.attackLayer = None
        self.raw_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.init_shared_ipc_buffer()

    # self.raw_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    def setAttackLayer(self, attackLayer):
        self.attackLayer = attackLayer

    def getAttackLayer(self):
        return self.attackLayer

    def getcurrCmd(self):
        currCmd = None
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

    def setPowerSimIdMap(self, powerSimIdMap):
        self.hostIDtoPowerSimID = powerSimIdMap
        self.powerSimIDtohostID = {}
        for hostID in self.hostIDtoPowerSimID.keys():
            powerSimIdSet = self.hostIDtoPowerSimID[hostID]
            for powerSimId in powerSimIdSet:
                self.powerSimIDtohostID[powerSimId] = hostID

    def getPowerSimIDsforNode(self, cyberNodeID):
        if cyberNodeID in self.hostIDtoPowerSimID.keys():
            return self.hostIDtoPowerSimID[cyberNodeID]
        else:
            return None

    def getCyberNodeIDforNode(self, powerSimNodeID):
        if powerSimNodeID in self.powerSimIDtohostID.keys():
            return self.powerSimIDtohostID[powerSimNodeID]
        else:
            return None

    def onRxPktFromProxy(self, pkt, dstCyberNodeID):

        if is_pkt_from_attack_dispatcher(pkt) == True:
            payload = self.extractPayloadFromPkt(pkt)
            try:
                src_ip, dst_ip = decode_raw_ip_payload_src_dst(str(payload))
                self.log.info("Sending attack dispatcher packet : " + str(payload) + " to: " + dst_ip)
                self.raw_sock.sendto(binascii.unhexlify(payload), (dst_ip, 0))
            except Exception as e:
                pass
        else:
            self.attackLayer.runOnThread(self.attackLayer.onRxPktFromIPCLayer, extractPowerSimIdFromPkt(pkt), pkt,
                                         dstCyberNodeID)

    def onRxPktFromAttackLayer(self, pkt):
        ret = 0
        self.log.info("Relaying pkt: " + str(pkt) + " to core")
        while ret <= 0:
            ret = self.sharedBufferArray.write(self.sharedBufName,pkt, PROXY_NODE_ID)
            sleep(0.05)
        # print "Return val = ", ret

        self.log.info("Relayed pkt: " + str(pkt) + " to core")

    def txPktToPowerSim(self, powerSimNodeID, payload):
        cyberNodeID = self.getCyberNodeIDforNode(powerSimNodeID)
        powerSimNodeIDLen = str(len(powerSimNodeID))
        txpkt = powerSimNodeIDLen.zfill(POWERSIM_ID_HDR_LEN) + powerSimNodeID + payload
        self.attackLayer.runOnThread(self.attackLayer.onRxPktFromIPCLayer, powerSimNodeID, txpkt, cyberNodeID)

    def extractPayloadFromPkt(self, pkt):
        powerSimID = extractPowerSimIdFromPkt(pkt)
        return pkt[POWERSIM_ID_HDR_LEN + len(powerSimID):]

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

    def init_shared_ipc_buffer(self):
        self.sharedBufName = str(self.hostID) + "buffer"
        #self.sharedBuffer = shared_buffer(bufName=self.sharedBufName, isProxy=False)

        result = self.sharedBufferArray.open(self.sharedBufName,isProxy=False)

        if result == BUF_NOT_INITIALIZED or result == FAILURE:
            self.log.error("Shared Buffer open failed! Buffer not initialized")
            return False
        else:
            self.log.info("Shared Buffer open succeeded")
            return True

    def run(self) :
        #sleep(3)   
        self.log.info("Started at " + str(datetime.now()))
		

        #init_res = self.init_shared_ipc_buffer()
        #if init_res == False :
        #    self.log.info("Shared Buffer initialization failed. Stopping Thread.")
        #    return
        self.log.info("power sim id to host id map = " + str(self.powerSimIDtohostID))
        self.log.info("host id to powersim id map = " + str(self.hostIDtoPowerSimID))
        sys.stdout.flush()
        assert (self.attackLayer != None)
        while True:

            currCmd = self.getcurrCmd()
            if currCmd != None and currCmd == CMD_QUIT:
                self.log.info("Stopping at " + str(datetime.now()))
                sys.stdout.flush()
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

            self.idle()

    def idle(self):
        recvPkt = ""
        dstCyberNodeID, recvPkt = self.sharedBufferArray.read(self.sharedBufName)
        time.sleep(0.01)

        if len(recvPkt) != 0:
            self.log.info("Received pkt: " + str(recvPkt) + " from core for Dst Node Id =  " + str(dstCyberNodeID))
            self.onRxPktFromProxy(recvPkt, dstCyberNodeID)

        #print "Before = ", str(datetime.now())
        #sys.stdout.flush()
        #sleep(1)
        #print "After = ", str(datetime.now())
        #sys.stdout.flush()
