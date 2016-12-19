import sys
import os
import time
import threading
import Proxy.shared_buffer
from Proxy.shared_buffer import *
import Proxy.logger
from Proxy.logger import Logger
from Proxy.defines import *
from timeit import default_timer as timer
from Proxy.basicHostAttackLayer import basicHostAttackLayer


class hostAttackLayer(basicHostAttackLayer):
    def __init__(self, hostID, logFile, IPCLayer, NetworkServiceLayer, sharedBufferArray):
        basicHostAttackLayer.__init__(self, hostID, logFile, IPCLayer, NetworkServiceLayer, sharedBufferArray)

        self.init_time = None
        self.elasped_time = None

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

    #  Could be arbitrarily modified to perform specific attacks
    #  using the API described.
    #  Function called repeatedly.
    def idle(self):
        # Put logic for specific attacks here.  Can be used to do Async sends to IPC and Network layers
        if self.running_emulate_stage == True:
            if self.emulate_stage_id == "emulation-stage-nmap-from-1-to-2":
                print "Inside emulation-stage-nmap", self.getHostID()
                print self.IPMapping

                # Start keeping track of time
                if not self.init_time:
                    self.init_time = timer()

                # Measure how long has it been since the start
                self.elasped_time = timer() - self.init_time

                # If it has been longer than desired duration
                if self.elasped_time > 5:
                    self.signal_end_of_emulate_stage()
