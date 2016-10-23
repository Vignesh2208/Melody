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

		self.threadCmdLock = threading.Lock()
		self.NetLayerRxLock = threading.Lock()
		self.NetLayerRxBuffer = []
		self.threadCmdQueue = []
		self.powerSimIP = powerSimIP 
		self.log = logger.Logger(logFile,"Proxy Network Layer Thread")

		
	def sendUDPMsg(self,pkt,IPAddr,port) :
		UDP_IP = IPAddr
		UDP_PORT = port
		MESSAGE = str(pkt)
		self.log.info("<SEND> TO: " + str(UDP_IP) + " FROM: " + str(self.hostID) + " PKT: " + str(MESSAGE))
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

	def txPktPowerSim(self,pkt) :
		self.sendUDPMsg(pkt,self.powerSimIP,POWERSIM_UDP_PORT)

	def rxPktPowerSim(self) :
		pkt = None
		self.NetLayerRxLock.acquire()
		pkt = NetLayerRxBuffer.pop()
		self.NetLayerRxLock.release()
		return pkt


	def getcurrCmd(self) :
		self.threadCmdLock.acquire()
		currCmd = self.threadCmdQueue.pop()
		self.threadCmdLock.release()
		return currCmd

	def cancelThread(self):
		self.threadCmdLock.acquire()
		self.threadCmdQueue.append(CMD_QUIT)
		self.threadCmdLock.release()


	def run(self) :

		while True :
			currCmd = getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				break
			sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
			sock.settimeout(SOCKET_TIMEOUT)
			sock.bind(('0.0.0.0', PROXY_UDP_PORT))
			data, addr = sock.recvfrom(MAXPKTSIZE)

			if data != None :
				self.log.info("<RECV> TO: " + str(self.hostID) + " FROM: " + str(addr) + " PKT: " + str(data))
				self.NetLayerRxLock.acquire()
				NetLayerRxBuffer.append(str(data))
				self.NetLayerRxLock.release()












