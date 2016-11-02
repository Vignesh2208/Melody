import sys
import os
import threading
import shared_buffer
from shared_buffer import *
import logger
from logger import Logger
from defines import *
from basicHostAttackLayer import basicHostAttackLayer



class hostAttackLayer(basicHostAttackLayer) :

	def __init__(self,hostID,logFile,IPCLayer,NetworkServiceLayer) :
		basicHostAttackLayer.__init__(self,hostID,logFile,IPCLayer,NetworkServiceLayer)
		

	# Callback on each received pkt from Net layer
	# By default it is injected to IPC layer
	# Arguments 
	#		pkt 	(full packet - string)
	def onRxPktFromNetworkLayer(self,pkt):

		# possibly modify pkt here
		return basicHostAttackLayer.onRxPktFromNetworkLayer(pkt)		# injects pkt into IPC layer
		

	# Callback on each received pkt from IPC layer
	# By default it is injected to Network Layer
	# Arguments 
	#		pkt 	(full packet - string)
	#		dstCyberNodeID	(int)
	def onRxPktFromIPCLayer(self,pkt,dstCyberNodeID):

		# possibly modify pkt here
		return basicHostAttackLayer.onRxPktFromIPCLayer(pkt,dstCyberNodeID)	# injects pkt into Network layer


	# Send pkt asynchronously to the Network layer
	def txAsyncNetServiceLayer(self,pkt,dstCyberNodeID):
		return basicHostAttackLayer.txAsyncNetServiceLayer(pkt,dstCyberNodeID)

	# Send pkt asynchronously to the IPC layer
	def txAsyncIPCLayer(self,pkt) :
		return basicHostAttackLayer.txAsyncIPCLayer(pkt)

	# Returns the unique hostID (int)
	def getHostID(self) :
		return self.hostID

	#  Could be arbitrarily modified to perform specific attacks
	#  using the API described.
	def run(self) :

		# Default Benign Attack Layer
		pktToSend = None
		self.log.info("Started ...")
		assert(self.NetServiceLayer != None)
		assert(self.IPCLayer != None)
		while True :

			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping ...")
				break

			# Put logic for specific attacks here.  Can be used to do Async sends to IPC and Network layers












