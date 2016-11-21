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
		return basicHostAttackLayer.onRxPktFromNetworkLayer(self,pkt)		# injects pkt into IPC layer
		

	# Callback on each received pkt from IPC layer
	# By default it is injected to Network Layer
	# Arguments 
	#		pkt 	(full packet - string)
	#		dstCyberNodeID	(int)
	def onRxPktFromIPCLayer(self,pkt,dstCyberNodeID):
		# possibly modify pkt here
		return basicHostAttackLayer.onRxPktFromIPCLayer(self,pkt,dstCyberNodeID)	# injects pkt into Network layer


	# Send pkt asynchronously to the Network layer
	def txAsyncNetServiceLayer(self,pkt,dstCyberNodeID):
		return basicHostAttackLayer.txAsyncNetServiceLayer(self,pkt,dstCyberNodeID)

	# Send pkt asynchronously to the IPC layer
	def txAsyncIPCLayer(self,pkt) :
		return basicHostAttackLayer.txAsyncIPCLayer(self,pkt)

	# Returns the unique hostID (int)
	def getHostID(self) :
		return self.hostID

	#  Could be arbitrarily modified to perform specific attacks
	#  using the API described.
	#  Function called repeatedly.
	def idle(self) :
		# Put logic for specific attacks here.  Can be used to do Async sends to IPC and Network layers

		pass











