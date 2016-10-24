import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *
#from hostIPCLayer import *
#from networkServiceLayer import *


class basicHostAttackLayer(threading.Thread) :

	def __init__(self,hostID,logFile,IPCLayer,NetworkServiceLayer) :

		threading.Thread.__init__(self)
		self.threadCmdLock = threading.Lock()
		self.threadCmdQueue = []
		self.hostID = hostID
		self.log = logger.Logger(logFile,"Host " + str(hostID) + " Attack Layer Thread")
		self.IPCLayer = IPCLayer
		self.NetServiceLayer = NetworkServiceLayer

	def txNetServiceLayer(self,pkt,dstNodeID) :
		self.NetServiceLayer.txPkt(pkt,dstNodeID)

	def rxNetServiceLayer(self) :
		return self.NetServiceLayer.rxPkt()	

	def txIPCLayer(self,pkt) :
		self.IPCLayer.appendToTxBuffer(pkt)

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


	def run(self) :

		pktToSend = None
		self.log.info("Started ...")
		while True :

			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping ...")
				break

			recvPkt = self.rxNetServiceLayer()
			if recvPkt != None :
				self.txIPCLayer(recvPkt)

			dstNodeID,txPkt = self.rxIPCLayer()
			if txPkt != None :
				self.txNetServiceLayer(txPkt,dstNodeID)












