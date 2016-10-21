import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *


class hostIPCLayer(threading.Thread) :

	def __init__(self,hostID,logFile) :
		self.attkLayerTxLock = threading.Lock()
		self.attkLayerRxLock = threading.Lock()
		self.threadCmdLock = threading.Lock()

		self.attkLayerTxBuffer = []
		self.attkLayerRxBuffer = []
		self.threadCmdQueue = []
		self.hostID = hostID
		self.log = logger.Logger(logFile,"Host " + str(hostID) + " IPC Thread")
		self.sharedBufName = str(hostID) + "buffer"
		self.sharedBuffer = shared_buffer(bufName=self.sharedBufName,isProxy=False)


		result = self.sharedBuffer.open()

		if result == BUF_NOT_INITIALIZED or result == FAILURE :
			self.log.error("Shared Buffer open failed! Buffer not initialized")


	def appendToTxBuffer(self,pkt) :
		self.attkLayerTxLock.acquire()
		self.attkLayerTxBuffer.append(pkt)
		self.attkLayerTxLock.release()

	def getReceivedMsg(self) :
		pkt = None
		self.attkLayerRxLock.acquire()
		dstID,pkt = self.attkLayerRxBuffer.pop()
		self.attkLayerRxLock.release()
		return dstID,pkt

	def appendToRxBuffer(self,pkt) :
		self.attkLayerRxLock.acquire()
		self.attkLayerRxBuffer.append(pkt)
		self.attkLayerRxLock.release()

	def getPktToSend(self) :
		pkt = None
		self.attkLayerTxLock.acquire()
		pkt = attkLayerTxBuffer.pop()
		self.attkLayerTxLock.release()
		return pkt

	def cancelThread(self):
		self.threadCmdLock.acquire()
		self.threadCmdQueue.append(CMD_QUIT)
		self.threadCmdLock.release()



	def run(self) :

		pktToSend = None
		while True :

			currCmd = None
			recvPkt = None
			self.threadCmdLock.acquire()
			currCmd = self.threadCmdQueue.pop()
			self.threadCmdLock.release()
			if currCmd != None and currCmd == CMD_QUIT :
				break

			# send any available pkt to Proxy
			if pktToSend == None :
				pktToSend = self.getPktToSend()

			if pktToSend != None :
				ret = self.sharedBuffer.write(pktToSend)
				if ret > 0 :
					pktToSend = None

			dstID,recvPkt = self.sharedBuffer.read()

			if recvPkt != None :
				self.appendToRxBuffer((dstID,recvPkt))











