import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *



class basicHostAttackLayer(threading.Thread) :

	def __init__(self,hostID,logFile,IPCLayer,NetworkServiceLayer) :

		threading.Thread.__init__(self)
		self.threadCmdLock = threading.Lock()
		self.threadCmdQueue = []
		self.hostID = hostID
		self.log = logger.Logger(logFile,"Host " + str(hostID) + " Attack Layer Thread")
		self.IPCLayer = IPCLayer
		self.NetServiceLayer = NetworkServiceLayer

	
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

	# default - benign Attack Layer
	def onRxPktFromNetworkLayer(self,pkt):
		self.IPCLayer.onRxPktFromAttackLayer(pkt)

	# default - benign Attack Layer
	def onRxPktFromIPCLayer(self,pkt,dstNodeID):
		self.NetServiceLayer.onRxPktFromAttackLayer(pkt,dstNodeID)


	def txAsyncNetServiceLayer(self,pkt,dstNodeID):
		self.NetServiceLayer.onRxPktFromAttackLayer(pkt,dstNodeID)

	def txAsyncIPCLayer(self,pkt) :
		self.IPCLayer.onRxPktFromAttackLayer(pkt)



	def run(self) :

		pktToSend = None
		self.log.info("Started ...")
		assert(self.NetServiceLayer != None)
		assert(self.IPCLayer != None)
		while True :

			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping ...")
				break

			# can use this to send async pkts to Net layer and IPC layer














