import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *



class proxyTransportLayer(threading.Thread) :

	def __init__(self,logFile,IPCLayer,NetworkServiceLayer) :

		self.threadCmdLock = threading.Lock()
		self.threadCmdQueue = []
		self.log = logger.Logger(logFile,"Proxy Attack Layer Thread")
		self.IPCLayer = IPCLayer
		self.NetServiceLayer = NetworkServiceLayer

	def txPowerSim(self,pkt) :
		self.NetServiceLayer.txPktPowerSim(pkt)

	def rxPowerSim(self) :
		return self.NetServiceLayer.rxPktPowerSim()	

	def txIPCLayer(self,data) :
		self.IPCLayer.appendToTxBuffer(data)

	def rxIPCLayer(self) :
		return self.IPCLayer.getReceivedMsg()

	def getcurrCmd(self) :
		self.threadCmdLock.acquire()
		currCmd = self.threadCmdQueue.pop()
		self.threadCmdLock.release()
		return currCmd

	def extractSrcNodeID(self,rxPktPowerSim) :
		return 1 # For Now

	def cancelThread(self):
		self.threadCmdLock.acquire()
		self.threadCmdQueue.append(CMD_QUIT)
		self.threadCmdLock.release()


	def run(self) :

		pktToSend = None
		while True :

			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				break

			recvPkt = self.rxPowerSim()
			if recvPkt != None :
				srcHostID = self.extractSrcNodeID(recvPkt)
				self.txIPCLayer((srcHostID,recvPkt))

			txPkt = self.rxIPCLayer()
			if txPkt != None :
				self.txPowerSim(txPkt)












