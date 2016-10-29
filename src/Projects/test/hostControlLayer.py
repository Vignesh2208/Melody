import sys
import os
import threading
import Proxy.shared_buffer
from Proxy.shared_buffer import *
import Proxy.logger
from Proxy.logger import Logger
from Proxy.defines import *
from Proxy.basicHostIPCLayer import basicHostIPCLayer


class hostControlLayer(basicHostIPCLayer) :

	def __init__(self,hostID,logFile) :
		basicHostIPCLayer.__init__(self,hostID,logFile)


	# Appends data that needs to be set to power simulator to a Rx Buffer
	# from which it is later picked up by the Attack Layer
	# and subsequently transmitted over the network to power sim via dstCyberNode-Proxy
	# Arguments:
	#	tuple - (dstCyberNodeID (int), pkt (string) )
	def appendToRxBuffer(self,dataTuple) :
		basicHostIPCLayer.appendToRxBuffer(self,dataTuple)


	# Returns a pkt (string) received from Attack Layer (if any)
	# Otherwise it returns None
	def getPktFromAttackLayer(self):
		return basicHostIPCLayer.getPktToSend(self)

	# Returns the set of power sim node Ids [list of strings] that
	# are mapped to the given cyber node (int). It returns None if the
	# mapping does not exist.
	def getPowerSimIDsforNode(self, cyberNodeID):
		return basicHostIPCLayer.getPowerSimIDsforNode(cyberNodeID)

	# Returns the cyber node id (int) when given a power sim node id (string)
	# If the mapping does not exist, it returns None
	def getCyberNodeIDforNode(self, powerSimNodeID):
		return basicHostIPCLayer.getCyberNodeIDforNode(powerSimNodeID)


	# Returns the power sim id present in the pkt (string)
	def extractPowerSimIdFromPkt(self, pkt):
		return basicHostIPCLayer.extractPowerSimIdFromPkt(pkt)
		
	
	# Could be modified to implement specific control algorithms
	def run(self) :

		# Default Control Algorithm which does nothing specific
		basicHostIPCLayer.run(self)











