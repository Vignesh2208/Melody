import sys

print sys.path


import subprocess
import os
import time
import threading
import core
from core.shared_buffer import *
import core.logger
from core.logger import Logger
from core.defines import *
from timeit import default_timer as timer
from core.basicHostAttackLayer import basicHostAttackLayer


class hostAttackLayer(basicHostAttackLayer):
    def __init__(self, hostID, logFile, IPCLayer, NetworkServiceLayer, sharedBufferArray):
        basicHostAttackLayer.__init__(self, hostID, logFile, IPCLayer, NetworkServiceLayer, sharedBufferArray)

        self.stage_init_time = None
        self.duration = None
        self.p = None

    # Callback on each received pkt from Net layer
    # By default it is injected to IPC layer
    # Arguments
    #		pkt 	(full packet - string)
    def onRxPktFromNetworkLayer(self, pkt):
        # possibly modify pkt here
        return basicHostAttackLayer.onRxPktFromNetworkLayer(self, pkt)  # injects pkt into IPC layer

    # Callback on each received pkt from IPC layer
    # By default it is injected to Network Layer
    # Arguments
    #		pkt 	(full packet - string)
    #		dstCyberNodeID	(int)
    def onRxPktFromIPCLayer(self, pkt, dstCyberNodeID):
        # possibly modify pkt here
        return basicHostAttackLayer.onRxPktFromIPCLayer(self, pkt, dstCyberNodeID)  # injects pkt into Network layer

    # Send pkt asynchronously to the Network layer
    def txAsyncNetServiceLayer(self, pkt, dstCyberNodeID):
        return basicHostAttackLayer.txAsyncNetServiceLayer(self, pkt, dstCyberNodeID)

    # Send pkt asynchronously to the IPC layer
    def txAsyncIPCLayer(self, pkt):
        return basicHostAttackLayer.txAsyncIPCLayer(self, pkt)

    # Returns the unique hostID (int)
    def getHostID(self):
        return self.hostID

    def handle_nmap_emulation_stage(self):

        tokens = self.emulate_stage_id.split("-")
        src_id = int(tokens[4])
        dst_id = int(tokens[6])

        # Check to see this node is the source of nmap scan
        if self.getHostID() == src_id:

            # Start keeping track of time
            if not self.p:

                print src_id, dst_id, self.duration
                dst_ip = self.IPMapping[dst_id][0]
                print dst_ip
                self.p = subprocess.Popen(["nmap", "-T5", "--disable-arp-ping", "-p", "1-65535", dst_ip])

            # Measure how long has it been since the start, if it has been longer than desired duration
            if timer() - self.stage_init_time > self.duration:

                print "Killing pid:", self.p.pid
                self.p.terminate()

    def capture_start_of_emulated_stage(self):
        tokens = self.emulate_stage_id.split("-")
        self.duration = int(tokens[8])

        # Start keeping track of time
        if not self.stage_init_time:
            self.stage_init_time = timer()
            print "Inside emulation-stage-nmap", self.getHostID()

    def indicate_end_of_emulated_stage(self):

        # Measure how long has it been since the start, if it has been longer than desired duration
        if timer() - self.stage_init_time > self.duration:

            # This is crucial for the next stage to be initialized
            self.stage_init_time = None

            self.signal_end_of_emulate_stage()

    #  Could be arbitrarily modified to perform specific attacks
    #  using the API described.
    #  Function called repeatedly.
    def idle(self):
        # Put logic for specific emulated attack stages here. Can be used to do Async sends to IPC and Network layers
        if self.running_emulate_stage:

            self.capture_start_of_emulated_stage()

            if self.emulate_stage_id.startswith("emulation-stage-nmap"):
                self.handle_nmap_emulation_stage()

            self.indicate_end_of_emulated_stage()
