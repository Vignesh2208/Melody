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
		threading.Thread.__init__(self)
		
		self.attkLayerTxLock = threading.Lock()
		self.attkLayerRxLock = threading.Lock()
		self.threadCmdLock = threading.Lock()

		self.attkLayerTxBuffer = []
		self.attkLayerRxBuffer = []
		self.threadCmdQueue = []
		self.sharedBufferArray = shared_buffer_array()
		self.log = logger.Logger(logFile,"Proxy IPC Thread")
		self.hostList = hostIDList
		for hostID in hostIDList :
			result = self.sharedBufferArray.open(bufName=str(hostID) + "buffer",isProxy=True)
			if result == BUF_NOT_INITIALIZED or result == FAILURE :
				self.log.error("Shared Buffer open failed for Proxy. Buffer not initialized")
			else :
				self.log.info("Initialized shared buffer for : " + str(hostID))

		self.controlCenterID = -1
		self.hostIDtoPowerSimID = None
		self.powerSimIDtohostID = None

	def setControlCenterID(self,controlCenterID):
		self.controlCenterID = controlCenterID

	def appendToTxBuffer(self,pkt) :
		self.attkLayerTxLock.acquire()
		self.attkLayerTxBuffer.append(pkt)
		self.attkLayerTxLock.release()

	def getReceivedMsg(self) :
		pkt = None
		self.attkLayerRxLock.acquire()
		try :
			dstID,pkt = self.attkLayerRxBuffer.pop()
		except:
			dstID = -1
			pkt = None
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
		try:
			dstID,pkt = self.attkLayerTxBuffer.pop()
		except:
			dstID = -1
			pkt = None
		self.attkLayerTxLock.release()
		return dstID,pkt

	def cancelThread(self):
		self.threadCmdLock.acquire()
		self.threadCmdQueue.append(CMD_QUIT)
		self.threadCmdLock.release()

	def setPowerSimIdMap(self, powerSimIdMap):
		self.hostIDtoPowerSimID = powerSimIdMap
		self.powerSimIDtohostID = {}
		for hostID in self.hostIDtoPowerSimID.keys():
			powerSimIdSet = self.hostIDtoPowerSimID[hostID]
			for powerSimId in powerSimIdSet:
				self.powerSimIDtohostID[powerSimId] = hostID

	# Needs to be modified ass appropriate
	# It is used by the proxy to determine
	# the final receipient of the pkt received from the proxy.
	# It is usually the control Center
	def extractFinalDstID(self,pktFromPowerSim) :
		return self.controlCenterID


	def run(self) :

		pktToSend = None
		dstID = None
		nHosts = len(self.hostList)
		assert(self.controlCenterID > 0)
		self.log.info("Started ...")
		while True :

			currCmd = None
			recvPkt = ''
			self.threadCmdLock.acquire()
			try:
				currCmd = self.threadCmdQueue.pop()
			except:
				currCmd = None
			self.threadCmdLock.release()
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping ...")
				break

			# send any available pkt to Host
			if pktToSend == None :
				dstID,pktToSend = self.getPktToSend()

			if pktToSend != None :
				dstHostBufName = str(dstID) + "buffer"
				
				# replace dstID with NodeID of ControlNode Here
				finalDstID = self.extractFinalDstID(pktToSend)
				ret = self.sharedBufferArray.write(dstHostBufName,pktToSend,finalDstID)
				if ret > 0 :
					self.log.info("Relaying pkt: " + str(pktToSend) + " To: " + str(finalDstID) + " via Host: " + str(dstID))
					pktToSend = None
					dstID = None
				

			for i in xrange(0,nHosts) :
				recvPkt = ''
				tmpID,recvPkt = self.sharedBufferArray.read(str(self.hostList[i])+ "buffer")

				if len(recvPkt) > 0 :
					self.log.info("Received pkt: " + str(recvPkt) + " from a Host Node")
					self.appendToRxBuffer((tmpID,recvPkt))











