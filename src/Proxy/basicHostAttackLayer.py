import shared_buffer
from shared_buffer import *
import sys
import os
import binascii
import threading
import logger
from logger import Logger
from datetime import datetime

from defines import *

import socket
import time



class attackPlaybackThread(threading.Thread) :
    def __init__(self, attackLayer):
        self.attackLayer = attackLayer
        threading.Thread.__init__(self)
        self.raw_rx_sock = socket.socket(socket.PF_PACKET,socket.SOCK_RAW,socket.htons(0x0800))
        self.raw_rx_sock.settimeout(5.0)




    def run(self):
        start_time = time.time()
        print "Running Attack Playback Thread"
        while True :
            self.attackLayer.stoppingLock.acquire()
            if self.attackLayer.stopping == True:
                self.attackLayer.stoppingLock.release()
                self.raw_rx_sock.close()
                print "Stopped Attack playback thread ..."
                break
            self.attackLayer.stoppingLock.release()

            try :
                raw_pkt = self.raw_rx_sock.recv(MAXPKTSIZE)
            except socket.error as e :
                raw_pkt = None
                continue


            assert len(raw_pkt) != 0
            raw_ip_pkt = get_raw_ip_pkt(raw_pkt)
            #
            ip_payload = binascii.hexlify(raw_ip_pkt.__str__( ))
            #print "Rx raw_ip (src,dst) = ", inet_to_str(raw_ip_pkt.src), inet_to_str(raw_ip_pkt.dst)
            #print "Rx pkt len = ", len(raw_ip_pkt), " pkt check = ", self.attackLayer.rx_pkt_check," Rx payload = ", ip_payload


            self.attackLayer.accessLock.acquire()
            if self.attackLayer.rx_pkt_check_updated == False:
                recv_msg = ''
                dummy_id, recv_msg = self.attackLayer.attk_channel_buffer.read()
                if len(recv_msg) != 0 and recv_msg[0:2] == "RX" :
                    self.attackLayer.rx_pkt_check = recv_msg[3:]
                    self.attackLayer.rx_pkt_check_updated = True
                elif len(recv_msg) != 0 and recv_msg[0:2] == "TX" :
                    payload = binascii.unhexlify(recv_msg[3:])
                    src_ip, dst_ip = decode_raw_ip_payload_src_dst(payload)
                    #print "Tx (src,dst) = ", src_ip, dst_ip, " len = ", len(payload), " payload = ", recv_msg[3:]
                    self.attackLayer.raw_tx_sock.sendto(payload, (dst_ip, 0))


            if ip_payload == self.attackLayer.rx_pkt_check :
                ret = 0
                self.attackLayer.rx_pkt_check = None
                self.attackLayer.rx_pkt_check_updated = False
                while ret <= 0 :
                    ret = self.attackLayer.attk_channel_buffer.write("ACK",0)

            self.attackLayer.accessLock.release()











class basicHostAttackLayer(threading.Thread):
    def __init__(self, hostID, logFile, IPCLayer, NetworkServiceLayer):

        threading.Thread.__init__(self)
        self.threadCmdLock = threading.Lock()

        self.threadCmdQueue = []
        self.threadCallbackQueue = {}
        self.threadCallbackLock = threading.Lock()
        self.nPendingCallbacks = 0

        self.hostID = hostID
        self.log = logger.Logger(logFile, "Host " + str(hostID) + " Attack Layer Thread")
        self.IPCLayer = IPCLayer
        self.NetServiceLayer = NetworkServiceLayer
        self.attk_channel_bufName = str(hostID) + "attk-channel-buffer"
        self.attk_channel_buffer = shared_buffer(bufName=self.attk_channel_bufName,isProxy=False)
        result = self.attk_channel_buffer.open()
        if result == BUF_NOT_INITIALIZED or result == FAILURE:
            print "Shared Buffer open failed! Buffer not initialized for host: " + str(hostID)
            sys.exit(0)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.raw_tx_sock = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_RAW)
        self.rx_pkt_check = None
        self.rx_pkt_check_updated = False
        self.stopping = False

        self.stoppingLock = threading.Lock()
        self.accessLock = threading.Lock()
        self.attack_playback_thread_started = False

        self.attack_playback_thread = attackPlaybackThread(self)


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

    def attack_playback_pass(self):
        if self.attack_playback_thread_started == False:
            self.attack_playback_thread_started = True
            self.log.info("Starting Attack playback thread ...")
            self.attack_playback_thread.start()




        recv_msg = ''
        self.accessLock.acquire()
        dummy_id, recv_msg = self.attk_channel_buffer.read()
        if len(recv_msg) != 0:
            if recv_msg[0:2] == "TX":
                payload = binascii.unhexlify(recv_msg[3:])
                src_ip, dst_ip = decode_raw_ip_payload_src_dst(payload)
                #print "Tx (src,dst) = ", src_ip, dst_ip, "len = ", len(payload), " payload = ", recv_msg[3:]
                self.raw_tx_sock.sendto(payload, (dst_ip, 0))
                self.accessLock.release()
            elif recv_msg[0:2] == "RX":
                self.rx_pkt_check = recv_msg[3:]
                self.rx_pkt_check_updated = True
                self.accessLock.release()
            else:
                self.accessLock.release()
        else:
            self.accessLock.release()




    def run(self):

        pktToSend = None
        self.log.info("Started ...")
        assert (self.NetServiceLayer != None)
        assert (self.IPCLayer != None)
        while True:

            currCmd = self.getcurrCmd()
            if currCmd != None and currCmd == CMD_QUIT:
                self.stoppingLock.acquire()
                self.stopping = True
                self.stoppingLock.release()
                self.attack_playback_thread.join()
                self.log.info("Stopping ...")
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

            self.attack_playback_pass()
            self.idle()

        # can use this to send async pkts to Net layer and IPC layer

    def idle(self):
        pass





