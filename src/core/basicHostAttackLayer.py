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



    def post_playback(self):
        pass

    def signal_end_of_replay_stage(self):

        self.attackLayer.accessLock.acquire()
        ret = 0
        while ret <= 0:
            ret = self.attackLayer.sharedBufferArray.write(self.attackLayer.attk_channel_bufName, "DONE", 0)
        self.attackLayer.running_replay_stage = False
        self.attackLayer.accessLock.release()

        print "Signalling End of Replay Stage ..."


    def run(self):
        start_time = time.time()
        self.raw_rx_sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
        #self.raw_rx_sock.settimeout(5.0)
        print "Running Attack Playback Thread at ", str(datetime.now())
        sys.stdout.flush()
        curr_send_idx = 0
        curr_send_event = None

        while True :
            self.attackLayer.stoppingLock.acquire()
            if self.attackLayer.stopping == True:
                self.attackLayer.running_replay_stage = False
                self.attackLayer.running_emulate_stage = False
                self.attackLayer.emulate_stage_id = "None"
                self.attackLayer.stoppingLock.release()
                self.raw_rx_sock.close()
                print "Stopped Attack playback thread at ", str(datetime.now())
                sys.stdout.flush()
                break
            self.attackLayer.stoppingLock.release()

            self.attackLayer.accessLock.acquire()
            if self.attackLayer.running_replay_stage == False :
                curr_send_idx = 0
                curr_send_event = None
                self.attackLayer.accessLock.release()
                continue


            if curr_send_event == None :


                if curr_send_idx < len(self.attackLayer.send_events) :
                    curr_send_event = self.attackLayer.send_events[curr_send_idx]
                    payload = binascii.unhexlify(str(curr_send_event[0]))
                    dst_ip = curr_send_event[1]
                    n_required_recv_events = curr_send_event[2]

                    print "Sending Replay Event: Dst = ", dst_ip, " N Req Recv events = ", n_required_recv_events
                    sys.stdout.flush()

            self.attackLayer.accessLock.release()

            if curr_send_event == None :
                self.signal_end_of_replay_stage()
                continue



            if n_required_recv_events == 0 :
                self.attackLayer.raw_tx_sock.sendto(payload, (dst_ip, 0))
                curr_send_event = None
                curr_send_idx = curr_send_idx + 1

            else:
                try :
                    raw_pkt = self.raw_rx_sock.recv(MAXPKTSIZE)
                except socket.error as e :
                    raw_pkt = None
                    continue


                assert len(raw_pkt) != 0
                raw_ip_pkt = get_raw_ip_pkt(raw_pkt)
                ip_payload = binascii.hexlify(raw_ip_pkt.__str__( ))

                self.attackLayer.accessLock.acquire()
                try :
                    if len(self.attackLayer.recv_events[ip_payload]) > 0 :
                        first_send_window = self.attackLayer.recv_events[ip_payload][0]
                        print "Received Replay Event ..."
                        sys.stdout.flush()

                        assert (first_send_window >= curr_send_idx)
                        if first_send_window == curr_send_idx :
                            n_required_recv_events = n_required_recv_events - 1
                        else :
                            self.attackLayer.recv_events[ip_payload].pop(0)
                            self.attackLayer.send_events[first_send_window] = [self.attackLayer.send_events[first_send_window][0],self.attackLayer.send_events[first_send_window][1],self.attackLayer.send_events[first_send_window][2] - 1]
                    else:
                        pass

                except KeyError as e:
                    pass

                self.attackLayer.accessLock.release()

        self.post_playback()

class basicHostAttackLayer(threading.Thread):
    def __init__(self, hostID, logFile, IPCLayer, NetworkServiceLayer,sharedBufferArray):

        threading.Thread.__init__(self)
        self.threadCmdLock = threading.Lock()

        self.threadCmdQueue = []
        self.threadCallbackQueue = {}
        self.threadCallbackLock = threading.Lock()
        self.nPendingCallbacks = 0
        self.sharedBufferArray = sharedBufferArray
        self.hostID = hostID
        self.log = logger.Logger(logFile, "Host " + str(hostID) + " Attack Layer Thread")
        self.IPCLayer = IPCLayer
        self.NetServiceLayer = NetworkServiceLayer
        self.IPMapping = self.NetServiceLayer.IPMap
        self.myIP = self.IPMapping[self.hostID][0]


        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.raw_tx_sock = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_RAW)
        self.rx_pkt_check = None
        self.rx_pkt_check_updated = False
        self.stopping = False

        self.stoppingLock = threading.Lock()
        self.accessLock = threading.Lock()
        self.attack_playback_thread_started = False
        self.running_emulate_stage = False
        self.running_replay_stage = False
        self.emulate_stage_id = "None"
        self.send_events = []
        self.recv_events = {}


        self.attack_playback_thread = attackPlaybackThread(self)

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

    def attack_playback_pass(self):
        if self.attack_playback_thread_started == False:
            self.attack_playback_thread_started = True
            self.log.info("Starting Attack playback thread " + str(datetime.now()))
            self.attack_playback_thread.start()

        recv_msg = ''
        self.accessLock.acquire()
        dummy_id, recv_msg = self.sharedBufferArray.read(self.attk_channel_bufName)
        if len(recv_msg) != 0:
            if "REPLAY:" in recv_msg:


                replay_pcap_file = recv_msg.split(":")[1]
                print "Replay PCAP FILE = ", replay_pcap_file
                print "MY IP = ", self.myIP
                self.recv_events = {}
                self.send_events = []
                self.accessLock.release()


                replay_pcap_reader = dpkt.pcap.Reader(open(replay_pcap_file, 'rb'))
                l2_type = replay_pcap_reader.datalink()

                curr_send_idx = 0
                curr_send_n_recv_events = 0


                for ts, curr_pkt in replay_pcap_reader:

                    if l2_type == dpkt.pcap.DLT_NULL:
                        src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt, dpkt.pcap.DLT_NULL)
                        raw_ip_pkt = get_raw_ip_pkt(curr_pkt,dpkt.pcap.DLT_NULL)
                    elif l2_type == dpkt.pcap.DLT_LINUX_SLL:
                        src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt, dpkt.pcap.DLT_LINUX_SLL)
                        raw_ip_pkt = get_raw_ip_pkt(curr_pkt, dpkt.pcap.DLT_LINUX_SLL)
                    else:
                        src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt)
                        raw_ip_pkt = get_raw_ip_pkt(curr_pkt)

                    if src_ip == self.myIP :
                        ip_payload = binascii.hexlify(raw_ip_pkt.__str__())
                        self.send_events.append([ip_payload,dst_ip,curr_send_n_recv_events])
                        curr_send_n_recv_events = 0
                        curr_send_idx = curr_send_idx + 1
                    else :
                        curr_send_n_recv_events = curr_send_n_recv_events + 1
                        ip_payload = binascii.hexlify(raw_ip_pkt.__str__())
                        try:
                            self.recv_events[ip_payload].append(curr_send_idx)
                        except:
                            self.recv_events[ip_payload] = []
                            self.recv_events[ip_payload].append(curr_send_idx)

                ret = 0
                while ret <= 0 :
                    ret = self.sharedBufferArray.write(self.attk_channel_bufName,"LOADED",0)

                print "LOADED PCAP LOCALLY ..."
                print "N SEND EVENTS = ", len(self.send_events)
                print "N RECV EVENTS = ", len(self.recv_events.keys())


            elif "START" in recv_msg :
                assert(self.running_emulate_stage == False and self.emulate_stage_id == "None")
                self.running_replay_stage = True

                print "SIGNALLED START REPLAY ..."
                self.accessLock.release()

            elif "EMULATE:" in recv_msg :

                assert(self.running_replay_stage == False)
                self.running_emulate_stage = True
                self.emulate_stage_id = recv_msg.split(":")[1]
                print "STARTING NEW EMULATION STAGE WITH ID = ", self.emulate_stage_id
                self.accessLock.release()




            else:
                print "Recv unknown cmd type. Msg = ", recv_msg
                self.accessLock.release()
        else:
            self.accessLock.release()


    def signal_end_of_emulate_stage(self):
        self.accessLock.acquire()
        self.running_emulate_stage = False

        print "ENDING EMULATION STAGE: ", self.emulate_stage_id
        self.emulate_stage_id = "None"
        ret = 0
        while ret <= 0:
            ret = self.sharedBufferArray.write(self.attk_channel_bufName, "DONE", 0)
        self.accessLock.release()

    def init_shared_attk_playback_buffer(self):
        self.attk_channel_bufName = str(self.hostID) + "attk-channel-buffer"
        #self.attk_channel_buffer = shared_buffer(bufName=self.attk_channel_bufName, isProxy=False)

        result = self.sharedBufferArray.open(self.attk_channel_bufName,isProxy=False)
        if result == BUF_NOT_INITIALIZED or result == FAILURE:
            print "Shared Buffer open failed! Buffer not initialized for host: " + str(self.hostID)
            sys.exit(0)
        else:
            self.log.info("Attk playback buffer open suceeded !")


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
                self.stoppingLock.acquire()
                self.stopping = True
                self.stoppingLock.release()
                self.attack_playback_thread.join()

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





