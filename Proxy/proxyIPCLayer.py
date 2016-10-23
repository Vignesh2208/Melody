import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *


class proxyIPCLayer(threading.Thread) :

	def __init__(self,logFile,hostIDList) :
		self.attkLayerTxLock = threading.Lock()
		self.attkLayerRxLock = threading.Lock()
		self.threadCmdLock = threading.Lock()

		self.attkLayerTxBuffer = []
		self.attkLayerRxBuffer = []
		self.threadCmdQueue = []
		self.sharedBufName = []
		self.sharedBuffer = []
		self.log = logger.Logger(logFile,"Proxy " + str(hostID) + " IPC Thread")
		for hostID in hostIDList :
			self.sharedBufName.append(str(hostID) + "buffer")
			self.sharedBuffer.append(shared_buffer(bufName=str(hostID) + "buffer",isProxy=True))
			result = self.sharedBuffer[len(sharedBuffer) - 1].open()
			if result == BUF_NOT_INITIALIZED or result == FAILURE :
				self.log.error("Shared Buffer open failed for host: " + str(hostID) + ". Buffer not initialized")


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
		dstID = None
		self.attkLayerTxLock.acquire()
		dstID,pkt = attkLayerTxBuffer.pop()
		self.attkLayerTxLock.release()
		return dstID,pkt

	def cancelThread(self):
		self.threadCmdLock.acquire()
		self.threadCmdQueue.append(CMD_QUIT)
		self.threadCmdLock.release()



	def run(self) :

		pktToSend = None
		dstID = None
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
				dstID,pktToSend = self.getPktToSend()

			if pktToSend != None :
				dstHostBufName = str(dstID) + "buffer"
				dstHostBufIdx = self.sharedBufName.index(dstHostBufName)
				assert(dstHostBufIdx >= 0 and dstHostBufIdx < len(self.sharedBufName))

				ret = self.sharedBuffer[dstHostBufIdx].write(pktToSend,dstID)
				if ret > 0 :
					pktToSend = None
					dstID = None

			dstID,recvPkt = self.sharedBuffer.read()

			if recvPkt != None :
				self.appendToRxBuffer(recvPkt)











