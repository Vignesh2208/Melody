import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *
import socket
import Queue
from datetime import datetime


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


	def onRxPktFromNetwork(self,pkt):
		self.attackLayer.runOnThread(self.attackLayer.onRxPktFromNetworkLayer,extractPowerSimIdFromPkt(pkt),pkt)

	def run(self):
		self.log.info("Started listening on IP: " + self.hostIP + " PORT: " + str(self.listenPort) + " at " + str(datetime.now()))
		#os.system("taskset -cp " + str(os.getpid()))
		sys.stdout.flush()
		#assert(self.attackLayer != None)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
		sock.settimeout(SOCKET_TIMEOUT)
		sock.bind((self.hostIP, self.listenPort))

		while True :
			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping at " + str(datetime.now()) )
				sys.stdout.flush()
				sock.close()
				break
			try:
				data, addr = sock.recvfrom(MAXPKTSIZE)
			except socket.timeout:
				data = None
			if data != None :
				self.log.info("%s  RECV_FROM=%s:%s  PKT=%s"%(datetime.now(), str(addr[0]), str(addr[1]), str(data)))
				# self.log.info("<RECV> TO: " + str(self.hostID) + " FROM: " + str(addr) + " PKT: " + str(data))
				self.onRxPktFromNetwork(str(data))

