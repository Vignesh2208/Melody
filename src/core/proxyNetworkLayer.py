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


class proxyNetworkServiceLayer(threading.Thread) :

	def __init__(self,logFile,powerSimIP) :
		threading.Thread.__init__(self)

		self.threadCmdLock = threading.Lock()
		self.NetLayerRxLock = threading.Lock()
		self.NetLayerRxBuffer = []
		self.threadCmdQueue = []
		self.powerSimIP = powerSimIP 
		self.log = logger.Logger(logFile,"core Network Layer Thread")
		self.transportLayer = None

	def setTransportLayer(self, transportLayer):
		self.transportLayer = transportLayer

	def getTransportLayer(self):
		return self.transportLayer


	def setPowerSimIdMap(self, powerSimIdMap):
		self.hostIDtoPowerSimID = powerSimIdMap
		self.powerSimIDtohostID = {}
		for hostID in self.hostIDtoPowerSimID.keys():
			powerSimIdSet = self.hostIDtoPowerSimID[hostID]
			for powerSimId in powerSimIdSet:
				self.powerSimIDtohostID[powerSimId] = hostID



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

	def onRxPktFromNetwork(self, pkt):
		self.transportLayer.runOnThread(self.transportLayer.onRxPktFromNetworkLayer, extractPowerSimIdFromPkt(pkt), pkt)

	def run(self) :

		self.log.info("Started listening on Port: " + str(PROXY_UDP_PORT))
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
		sock.settimeout(SOCKET_TIMEOUT)
		sock.bind(('0.0.0.0', PROXY_UDP_PORT))
		while True :
			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping ...")
				sock.close()
				break

			if POWERSIM_TYPE == "POWER_WORLD" :

				try:
					data, addr = sock.recvfrom(MAXPKTSIZE)
				except socket.timeout:
					data = None

				if data != None :
					self.log.info("%s  RECV_FROM=%s:%s  PKT=%s"%(datetime.now(), str(addr[0]), str(addr[1]), str(data)))
					self.onRxPktFromNetwork(str(data))













