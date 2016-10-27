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
		threading.Thread.__init__(self)

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

	def extractPowerSimIdFromPkt(self,pkt):
		return "test"

	# Needs to be modified as Appropriate. It is used by the Proxy to determine the
	# necessary shhared IPC Buffer to put the packet into
	def extractSrcNodeID(self,rxPktPowerSim) :
		powerSimId = self.extractPowerSimIdFromPkt(rxPktPowerSim)
		try:
			srcNodeID = self.IPCLayer.powerSimIDtohostID[powerSimId]
		except:
			srcNodeID = 1
		return srcNodeID # For Now

	def run(self) :

		pktToSend = None
		self.log.info("Started ...")
		while True :

			currCmd = self.getcurrCmd()
			txPkt = None
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping ...")
				break

			recvPkt = self.rxPowerSim()
			if recvPkt != None :
				srcHostID = self.extractSrcNodeID(recvPkt)
				self.txIPCLayer((srcHostID,recvPkt))

			srcId,txPkt = self.rxIPCLayer()
			if txPkt != None :
				self.txPowerSim(txPkt)












