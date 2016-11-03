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
import time

class hostControlLayer(basicHostIPCLayer) :

	def __init__(self,hostID,logFile) :
		basicHostIPCLayer.__init__(self,hostID,logFile)


	# Returns the set of power sim node Ids [list of strings] that
	# are mapped to the given cyber node (int). It returns None if the
	# mapping does not exist.
	def getPowerSimIDsforNode(self, cyberNodeID):
		return basicHostIPCLayer.getPowerSimIDsforNode(self,cyberNodeID)

	# Returns the cyber node id (int) when given a power sim node id (string)
	# If the mapping does not exist, it returns None
	def getCyberNodeIDforNode(self, powerSimNodeID):
		return basicHostIPCLayer.getCyberNodeIDforNode(self,powerSimNodeID)


	# Returns the power sim id present in the pkt (string)
	def extractPowerSimIdFromPkt(self, pkt):
		return basicHostIPCLayer.extractPowerSimIdFromPkt(self,pkt)

	# Returns the payload present in the pkt (string)
	def extractPayloadFromPkt(self, pkt):
		return basicHostIPCLayer.extractPayloadFromPkt(self,pkt)


	# transmits to power simulator 
	# Arguments:
	# 	powerSimNodeID (string)
	#   payload (string)
	def txPktToPowerSim(self,powerSimNodeID,payload) :
		return basicHostIPCLayer.txPktToPowerSim(self,powerSimNodeID,payload)


	# Callback on each received pkt from Attack layer.
	# Arguments:
	#   pkt - full pkt including powerSimID(string)
	def onRxPktFromAttackLayer(self,pkt):
		# process the pkt here
		self.log.info("Recv: at " + str(datetime.now())  + "Pkt = " + str(pkt))
		return None

	def run(self):
		self.log.info("Started control layer run")
		self.lastSendTime = int(round(time.time()*1000))
		return basicHostIPCLayer.run(self)

		
	
	# Could be modified to implement specific control algorithms
	# Function called repeatedly
	def idle(self) :
		# Put control logic here
		currTime = int(round(time.time()*1000))
		if currTime - self.lastSendTime >= 1000 :
			#self.txPktToPowerSim("2","HelloWorld!")
			self.lastSendTime = currTime










