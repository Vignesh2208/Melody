import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *
import socket


class proxyNetworkServiceLayer(threading.Thread) :

	def __init__(self,logFile,powerSimIP) :
		threading.Thread.__init__(self)

		self.threadCmdLock = threading.Lock()
		self.NetLayerRxLock = threading.Lock()
		self.NetLayerRxBuffer = []
		self.threadCmdQueue = []
		self.powerSimIP = powerSimIP 
		self.log = logger.Logger(logFile,"Proxy Network Layer Thread")


	def setPowerSimIdMap(self, powerSimIdMap):
		self.hostIDtoPowerSimID = powerSimIdMap
		self.powerSimIDtohostID = {}
		for hostID in self.hostIDtoPowerSimID.keys():
			powerSimIdSet = self.hostIDtoPowerSimID[hostID]
			for powerSimId in powerSimIdSet:
				self.powerSimIDtohostID[powerSimId] = hostID

	def sendUDPMsg(self,pkt,IPAddr,Port) :
		UDP_IP = IPAddr
		UDP_PORT = Port
		MESSAGE = str(pkt)
		self.log.info("<SEND> TO: " + str(UDP_IP) + ":" + str(UDP_PORT) + " FROM: " + str(self.powerSimIP) + " PKT: " + str(MESSAGE))
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

	def txPktPowerSim(self,pkt) :
		self.sendUDPMsg(pkt,self.powerSimIP,POWERSIM_UDP_PORT)

	def rxPktPowerSim(self) :
		pkt = None
		self.NetLayerRxLock.acquire()
		try:
			pkt = self.NetLayerRxBuffer.pop()
		except:
			pkt = None
		self.NetLayerRxLock.release()
		return pkt


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


	def run(self) :

		self.log.info("Started listening on Port: " + str(PROXY_UDP_PORT))
		while True :
			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping ...")
				break

			if POWERSIM_TYPE == "POWER_WORLD" :
				sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
				sock.settimeout(SOCKET_TIMEOUT)
				sock.bind(('0.0.0.0', PROXY_UDP_PORT))
				try:
					data, addr = sock.recvfrom(MAXPKTSIZE)
				except socket.timeout:
					data = None

				if data != None :
					self.log.info("<RECV> TO: A HOST" + " FROM: " + str(addr) + " PKT: " + str(data))
					self.NetLayerRxLock.acquire()
					self.NetLayerRxBuffer.append(str(data))
					self.NetLayerRxLock.release()












