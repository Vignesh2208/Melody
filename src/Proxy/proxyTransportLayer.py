import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *
import socket



class proxyTransportLayer(threading.Thread) :

	def __init__(self,logFile,IPCLayer,NetworkServiceLayer) :
		threading.Thread.__init__(self)

		self.threadCmdLock = threading.Lock()
		self.threadCmdQueue = []
		self.log = logger.Logger(logFile,"Proxy Transport Layer Thread")
		self.IPCLayer = IPCLayer
		self.NetServiceLayer = NetworkServiceLayer
		self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def sendUDPMsg(self, pkt, IPAddr, Port):
		UDP_IP = IPAddr
		UDP_PORT = Port
		MESSAGE = str(pkt)
		self.log.info(
			"<SEND PKT> TO POWERSIM: " + str(UDP_IP) + ":" + str(UDP_PORT)  + " PKT= " + str(
				MESSAGE))

		self.sendSocket.sendto(MESSAGE, (UDP_IP, UDP_PORT))


	def txPowerSim(self,pkt) :
		self.sendUDPMsg(pkt, self.NetServiceLayer.powerSimIP, POWERSIM_UDP_PORT)

	def rxPowerSim(self) :
		pkt = None
		self.NetServiceLayer.NetLayerRxLock.acquire()
		try:
			pkt = self.NetServiceLayer.NetLayerRxBuffer.pop()
		except:
			pkt = None
		self.NetServiceLayer.NetLayerRxLock.release()
		return pkt

	def txIPCLayer(self,data) :
		self.IPCLayer.attkLayerTxLock.acquire()
		self.IPCLayer.attkLayerTxBuffer.append(data)
		self.IPCLayer.attkLayerTxLock.release()


	def rxIPCLayer(self) :
		pkt = None
		self.IPCLayer.attkLayerRxLock.acquire()
		try:
			dstID, pkt = self.IPCLayer.attkLayerRxBuffer.pop()
		except:
			dstID = -1
			pkt = None
		self.IPCLayer.attkLayerRxLock.release()
		return dstID, pkt


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
	# necessary shhared IPC Buffer to put the packet into
	def extractSrcNodeID(self,rxPktPowerSim) :
		powerSimId = extractPowerSimIdFromPkt(rxPktPowerSim)
		try:
			srcNodeID = self.IPCLayer.powerSimIDtohostID[powerSimId]
		except Exception,e:
			print str(e)
			srcNodeID = 1
		return srcNodeID # For Now

	def run(self) :

		pktToSend = None
		self.log.info("Started ...")
		while True :

			currCmd = self.getcurrCmd()
			txPkt = None
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping ...")
				break

			recvPkt = self.rxPowerSim()
			if recvPkt != None :
				srcHostID = self.extractSrcNodeID(recvPkt)
				self.txIPCLayer((srcHostID,recvPkt))

			srcId,txPkt = self.rxIPCLayer()
			if txPkt != None :
				self.txPowerSim(txPkt)












