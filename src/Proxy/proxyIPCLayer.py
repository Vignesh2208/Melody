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
		

		self.threadCmdLock = threading.Lock()
		self.threadCmdQueue = []

		self.threadCallbackQueue = {}
		self.threadCallbackLock = threading.Lock()

		self.sharedBufferArray = shared_buffer_array()
		self.log = logger.Logger(logFile,"Proxy IPC Thread")
		self.hostList = hostIDList
		self.nPendingCallbacks = 0
		for hostID in hostIDList :
			result = self.sharedBufferArray.open(bufName=str(hostID) + "buffer",isProxy=True)
			if result == BUF_NOT_INITIALIZED or result == FAILURE :
				self.log.error("Shared Buffer open failed for Proxy. Buffer not initialized")
			else :
				self.log.info("Initialized shared buffer for : " + str(hostID))

		self.controlCenterID = -1
		self.hostIDtoPowerSimID = None
		self.powerSimIDtohostID = None
		self.transportLayer = None
		self.nHosts = len(self.hostList)

	def setControlCenterID(self,controlCenterID):
		self.controlCenterID = controlCenterID

	def setTransportLayer(self, transportLayer):
		self.transportLayer = transportLayer

	def getTransportLayer(self):
		return self.transportLayer


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

	def runOnThread(self, function, powerSimNodeID, *args):
		self.threadCallbackLock.acquire()
		if powerSimNodeID not in self.threadCallbackQueue.keys():
			self.threadCallbackQueue[powerSimNodeID] = []
			self.threadCallbackQueue[powerSimNodeID].append((function, args))
		else:
			if len(self.threadCallbackQueue[powerSimNodeID]) == 0:
				self.threadCallbackQueue[powerSimNodeID].append((function, args))
			else:
				self.threadCallbackQueue[powerSimNodeID][0] = (function, args)
		self.nPendingCallbacks = self.nPendingCallbacks + 1
		self.threadCallbackLock.release()

	def onRxPktFromTransportLayer(self,srcNodeID,pkt):
		injectHostBufName = str(srcNodeID) + "buffer"
		# replace dstID with NodeID of ControlNode Here
		finalDstID = self.extractFinalDstID(pkt)
		ret = 0
		while ret <= 0 :
			ret = self.sharedBufferArray.write(injectHostBufName, pkt, finalDstID)
		return

	def onRxPktFromHost(self,pkt):
		self.transportLayer.runOnThread(self.transportLayer.onRxPktFromIPCLayer,extractPowerSimIdFromPkt(pkt),pkt)

	def getcurrCmd(self):
		self.threadCmdLock.acquire()
		try:
			currCmd = self.threadCmdQueue.pop()
		except:
			currCmd = None
		self.threadCmdLock.release()
		return currCmd

	def run(self) :

		assert(self.controlCenterID > 0)
		self.log.info("Started ...")
		self.log.info("power sim id to host id map = " + str(self.powerSimIDtohostID))
		while True :

			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT:
				self.log.info("Stopping ...")
				break

			callbackFns = []
			self.threadCallbackLock.acquire()
			if self.nPendingCallbacks == 0:
				self.threadCallbackLock.release()
			else:

				values = list(self.threadCallbackQueue.values())
				for i in xrange(0, len(values)):
					if len(values[i]) > 0:
						callbackFns.append(values[i].pop())
				self.nPendingCallbacks = 0
				self.threadCallbackLock.release()

				for i in xrange(0, len(callbackFns)):
					function, args = callbackFns[i]
					function(*args)

			self.idle()

	def idle(self):
		for i in xrange(0, self.nHosts):
			recvPkt = ''
			tmpID, recvPkt = self.sharedBufferArray.read(str(self.hostList[i]) + "buffer")

			if len(recvPkt) > 0:
				self.log.info("Received pkt: " + str(recvPkt) + " from a Host Node")
				self.onRxPktFromHost(recvPkt)










