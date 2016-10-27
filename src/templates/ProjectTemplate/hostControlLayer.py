import sys
import os
import threading
import shared_buffer
from shared_buffer import *
import logger
from logger import Logger
from defines import *
from Proxy.basicHostIPCLayer import basicHostIPCLayer


class hostControlLayer(basicHostIPCLayer) :

	def __init__(self,hostID,logFile) :
		basicHostIPCLayer.__init__(self,hostID,logFile)


	# Appends data received from Proxy to a Rx Buffer
	# from which it is later picked up by the Attack Layer
	# and subsequently transmitted over the network to dstNode
	# Arguments:
	#	tuple - (dstNodeID (int), pkt (string) )
	def appendToRxBuffer(self,dataTuple) :
		basicHostIPCLayer.appendToRxBuffer(self,dataTuple)


	# Returns a pkt (string) received from Attack Layer (if any)
	# Otherwise it returns None
	def getPktFromAttackLayer(self):
		return basicHostIPCLayer.getPktToSend(self)
		
	
	# Could be modified to implement specific control algorithms
	def run(self) :

		# Default Control Algorithm which does nothing specific
		basicHostIPCLayer.run(self)











