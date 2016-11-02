import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *


class basicHostIPCLayer(threading.Thread) :

	def __init__(self,hostID,logFile) :
		threading.Thread.__init__(self)
		
		self.threadCmdLock = threading.Lock()
		self.threadCmdQueue = []
		self.hostID = hostID
		self.log = logger.Logger(logFile,"Host " + str(hostID) + " IPC Thread")
		self.sharedBufName = str(hostID) + "buffer"
		self.sharedBuffer = shared_buffer(bufName=self.sharedBufName,isProxy=False)


		result = self.sharedBuffer.open()

		if result == BUF_NOT_INITIALIZED or result == FAILURE :
			self.log.error("Shared Buffer open failed! Buffer not initialized")

		self.hostIDtoPowerSimID = None
		self.powerSimIDtohostID = None
		self.attackLayer = None

	def setAttackLayer(self,attackLayer):
		self.attackLayer = attackLayer

	def getAttackLayer(self):
		return self.attackLayer

	
	def getcurrCmd(self):
		currCmd = None
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

	def setPowerSimIdMap(self, powerSimIdMap):
		self.hostIDtoPowerSimID = powerSimIdMap
		self.powerSimIDtohostID = {}
		for hostID in self.hostIDtoPowerSimID.keys():
			powerSimIdSet = self.hostIDtoPowerSimID[hostID]
			for powerSimId in powerSimIdSet:
				self.powerSimIDtohostID[powerSimId] = hostID

	def getPowerSimIDsforNode(self, cyberNodeID):
		if cyberNodeID in self.hostIDtoPowerSimID.keys() :
			return self.hostIDtoPowerSimID[cyberNodeID]
		else:
			return None

	def getCyberNodeIDforNode(self, powerSimNodeID):
		if powerSimNodeID in self.powerSimIDtohostID.keys():
			return self.powerSimIDtohostID[powerSimNodeID]
		else:
			return None

	def onRxPktFromProxy(self,pkt,dstCyberNodeID) :
		self.attackLayer.onRxPktFromIPCLayer(pkt,dstCyberNodeID)


	def onRxPktFromAttackLayer(self,pkt):
		ret = 0
		while ret <= 0 :
			ret = self.sharedBuffer.write(pkt,PROXY_NODE_ID)
			self.log.info("Relaying pkt: " + str(pkt) + " to Proxy")



	def extractPowerSimIdFromPkt(self, pkt):

		powerSimID = "test"
		if POWERSIM_TYPE == "POWER_WORLD":
			powerSimIDLen = int(pkt[0:POWERSIM_ID_HDR_LEN])
			powerSimID = str(pkt[POWERSIM_ID_HDR_LEN:POWERSIM_ID_HDR_LEN + powerSimIDLen])

		return powerSimID

	def extractPayloadFromPkt(self,pkt) :
		powerSimID = self.extractPowerSimIdFromPkt(pkt) 
		return pkt[POWERSIM_ID_HDR_LEN + len(powerSimID):]



	def run(self) :

		self.log.info("Started ...")
		self.log.info("power sim id to host id map = " + str(self.powerSimIDtohostID))
		assert(self.attackLayer != None)
		pktToSend = None
		while True :

			
			recvPkt = None
			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping ...")
				break


			dstCyberNodeID,recvPkt = self.sharedBuffer.read()

			if len(recvPkt) != 0 :
				self.log.info("Received pkt: " + str(recvPkt) + " from Proxy for Dst: " + str(dstCyberNodeID))
				self.onRxPktFromProxy(recvPkt,dstCyberNodeID)

				










