import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger

from defines import *
import Queue
import socket




class basicHostAttackLayer(threading.Thread) :

	def __init__(self,hostID,logFile,IPCLayer,NetworkServiceLayer) :

		threading.Thread.__init__(self)
		self.threadCmdLock = threading.Lock()

		self.threadCmdQueue = []
		self.threadCallbackQueue = {}
		self.threadCallbackLock = threading.Lock()
		self.nPendingCallbacks = 0

		self.hostID = hostID
		self.log = logger.Logger(logFile,"Host " + str(hostID) + " Attack Layer Thread")
		self.IPCLayer = IPCLayer
		self.NetServiceLayer = NetworkServiceLayer

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
	
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

	def sendUDPMsg(self, pkt, IPAddr, Port):
		UDP_IP = IPAddr
		UDP_PORT = Port
		MESSAGE = str(pkt)
		self.log.info(
			"<SEND PKT> TO: " + str(UDP_IP) + ":" + str(UDP_PORT) + " FROM: " + str(self.hostID) + " PKT= " + str(MESSAGE))

		self.sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

	def txPkt(self, pkt, dstNodeID):
		if dstNodeID in self.NetServiceLayer.IPMap.keys():
			IPAddr, Port = self.NetServiceLayer.IPMap[dstNodeID]
			self.sendUDPMsg(pkt, IPAddr, Port)

	def txAsyncNetServiceLayer(self,pkt,dstNodeID):
		self.txPkt(pkt,dstNodeID)

	def txAsyncIPCLayer(self,pkt) :
		self.IPCLayer.runOnThread(self.IPCLayer.onRxPktFromAttackLayer,extractPowerSimIdFromPkt(pkt),pkt)

	# default - benign Attack Layer
	def onRxPktFromNetworkLayer(self, pkt):
		self.IPCLayer.runOnThread(self.IPCLayer.onRxPktFromAttackLayer,extractPowerSimIdFromPkt(pkt),pkt)

	# default - benign Attack Layer
	def onRxPktFromIPCLayer(self, pkt, dstNodeID):
		self.txAsyncNetServiceLayer(pkt, dstNodeID)

	def runOnThread(self, function, powerSimNodeID, *args):
		self.threadCallbackLock.acquire()
		if powerSimNodeID not in self.threadCallbackQueue.keys():
			self.threadCallbackQueue[powerSimNodeID] = []
			self.threadCallbackQueue[powerSimNodeID].append((function, args))
		else:
			if len(self.threadCallbackQueue[powerSimNodeID]) == 0:
				self.threadCallbackQueue[powerSimNodeID].append((function, args))
			else :
				self.threadCallbackQueue[powerSimNodeID][0] = (function, args)
		self.nPendingCallbacks = self.nPendingCallbacks + 1
		self.threadCallbackLock.release()




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

			callbackFns = []
			self.threadCallbackLock.acquire()
			if self.nPendingCallbacks == 0:
				self.threadCallbackLock.release()
			else:

				values = list(self.threadCallbackQueue.values())
				for i in xrange(0,len(values)) :
					if len(values[i]) > 0 :
						callbackFns.append(values[i].pop())
				self.nPendingCallbacks = 0
				self.threadCallbackLock.release()

				for i in xrange(0,len(callbackFns)) :
					function,args = callbackFns[i]
					function(*args)

			self.idle()

			# can use this to send async pkts to Net layer and IPC layer


	def idle(self):
		pass











