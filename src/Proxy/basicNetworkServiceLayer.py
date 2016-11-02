import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *
import socket


class basicNetworkServiceLayer(threading.Thread) :

	def __init__(self,hostID,logFile,hostID_To_IP) :

		threading.Thread.__init__(self)

		self.threadCmdLock = threading.Lock()
		self.threadCmdQueue = []
		self.hostID = hostID
		self.IPMap = hostID_To_IP
		self.hostIP,self.listenPort = self.IPMap[self.hostID]
		self.log = logger.Logger(logFile,"Host " + str(hostID) + " Network Layer Thread")
		self.hostIDtoPowerSimID = None
		self.powerSimIDtohostID = None
		self.attackLayer = None



	def setAttackLayer(self,attackLayer):
		self.attackLayer = attackLayer

	def getAttackLayer(self):
		return self.attackLayer


	def sendUDPMsg(self,pkt,IPAddr,Port) :
		UDP_IP = IPAddr
		UDP_PORT = Port
		MESSAGE = str(pkt)
		self.log.info("<SEND> TO: " + str(UDP_IP)  + ":" + str(UDP_PORT) + " FROM: " + str(self.hostID) + " PKT: " + str(MESSAGE))
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

	def txPkt(self,pkt,dstNodeID) :
		if dstNodeID in self.IPMap.keys() :
			IPAddr,Port = self.IPMap[dstNodeID]
			self.sendUDPMsg(pkt,IPAddr,Port)

	def getcurrCmd(self) :
		self.threadCmdLock.acquire()
		try :
			currCmd = self.threadCmdQueue.pop()
		except:
			currCmd = None
		self.threadCmdLock.release()
		return currCmd

	def cancelThread(self):
		self.threadCmdLock.acquire()
		self.threadCmdQueue.append(CMD_QUIT)
		self.threadCmdLock.release()


	def onRxPktFromAttackLayer(self,pkt,dstNodeID):
		self.txPkt(pkt,dstNodeID)

	def onRxPktFromNetwork(self,pkt):
		self.attackLayer.onRxPktFromNetworkLayer(pkt)


	def run(self) :


		self.log.info("Started listening on IP: " + self.hostIP + " PORT: " + str(self.listenPort))
		assert(self.attackLayer != None)

		while True :
			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping ...")
				break
			sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
			sock.settimeout(SOCKET_TIMEOUT)
			sock.bind((self.hostIP, self.listenPort))

			try:
				data, addr = sock.recvfrom(MAXPKTSIZE)
			except socket.timeout:
				data = None
				sock.close()
				 

			if data != None :
				self.log.info("<RECV> TO: " + str(self.hostID) + " FROM: " + str(addr) + " PKT: " + str(data))
				self.onRxPktFromNetwork(str(data))











