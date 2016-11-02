import sys
import os
import threading
import Proxy.shared_buffer
from Proxy.shared_buffer import *
import Proxy.logger
from Proxy.logger import Logger
from Proxy.defines import *
from Proxy.basicHostIPCLayer import basicHostIPCLayer
from datetime import datetime

class hostControlLayer(basicHostIPCLayer) :

	def __init__(self,hostID,logFile) :
		basicHostIPCLayer.__init__(self,hostID,logFile)


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

	# Returns the payload present in the pkt (string)
	def extractPayloadFromPkt(self, pkt):
		return basicHostIPCLayer.extractPayloadFromPkt(pkt)


	# transmits to power simulator 
	# Arguments:
	# 	powerSimNodeID (string)
	#   payload (string)
	def txPktToPowerSim(self,powerSimNodeID,payload) :
		cyberNodeID = self.getCyberNodeIDforNode(powerSimNodeID)
		txpkt = '%10d%s%s'% (len(powerSimNodeID),powerSimNodeID,payload)
		self.attackLayer.onRxPktFromIPCLayer(txpkt,cyberNodeID)

	# Callback on each received pkt from Attack layer.
	# Arguments:
	#   pkt - full pkt including powerSimID(string)
	def onRxPktFromAttackLayer(self,pkt):
		# process the pkt here
		self.log.info("%s  %s"%datetime.now(), pkt)
		return None

		
	
	# Could be modified to implement specific control algorithms
	def run(self) :

		# Default Control Algorithm which does nothing specific
		self.log.info("Started ...")
		self.log.info("power sim id to host id map = " + str(self.powerSimIDtohostID))
		assert(self.attackLayer != None)
		while True :

			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				self.log.info("Stopping ...")
				break

			# Put control logic here










