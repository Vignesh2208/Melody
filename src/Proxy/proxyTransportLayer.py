import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *
import socket
from datetime import datetime


class proxyTransportLayer(threading.Thread) :

	def __init__(self,logFile,IPCLayer,NetworkServiceLayer) :
		threading.Thread.__init__(self)

		self.threadCmdLock = threading.Lock()
		self.threadCmdQueue = []
		self.threadCallbackQueue = {}
		self.threadCallbackLock = threading.Lock()

		self.log = logger.Logger(logFile,"Proxy Transport Layer Thread")
		self.IPCLayer = IPCLayer
		self.NetServiceLayer = NetworkServiceLayer
		self.nPendingCallbacks = 0
		self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def sendUDPMsg(self, pkt, IPAddr, Port):
		UDP_IP = IPAddr
		UDP_PORT = Port
		MESSAGE = str(pkt)
		self.log.info("%s  SEND_TO=%s:%s  PKT=%s"%(datetime.now(), str(UDP_IP), str(UDP_PORT), str(MESSAGE)))
		self.sendSocket.sendto(MESSAGE, (UDP_IP, UDP_PORT))


	def txPowerSim(self,pkt) :
		self.sendUDPMsg(pkt, self.NetServiceLayer.powerSimIP, POWERSIM_UDP_PORT)

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


	# Needs to be modified as Appropriate. It is used by the Proxy to determine the
	# necessary shared IPC Buffer to put the packet into
	def extractSrcNodeID(self,rxPktPowerSim) :
		powerSimId = extractPowerSimIdFromPkt(rxPktPowerSim)
		try:
			srcNodeID = self.IPCLayer.powerSimIDtohostID[powerSimId]
		except Exception,e:
			print str(e)
			srcNodeID = 1
		return powerSimId,srcNodeID # For Now


	def onRxPktFromNetworkLayer(self,pkt):
		powerSimId,srcNodeID = self.extractSrcNodeID(pkt)
		self.IPCLayer.runOnThread(self.IPCLayer.onRxPktFromTransportLayer,powerSimId,srcNodeID,pkt)

	def onRxPktFromIPCLayer(self,pkt):
		self.txPowerSim(pkt)

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

	def run(self) :

		pktToSend = None
		self.log.info("Started ...")
		while True :

			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
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













