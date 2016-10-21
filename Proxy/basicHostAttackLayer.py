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
		currCmd = self.threadCmdQueue.pop()
		self.threadCmdLock.release()
		return currCmd

	def cancelThread(self):
		self.threadCmdLock.acquire()
		self.threadCmdQueue.append(CMD_QUIT)
		self.threadCmdLock.release()


	def run(self) :

		pktToSend = None
		while True :

			currCmd = getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				break

			recvPkt = rxNetServiceLayer()
			if recvPkt != None :
				txIPCLayer(recvPkt)

			txPkt = rxIPCLayer()
			if txPkt != None :
				txNetServiceLayer












