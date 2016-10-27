import sys
import os
import threading
import shared_buffer
from shared_buffer import *
import logger
from logger import Logger
from defines import *
from Proxy.basicHostAttackLayer import basicHostAttackLayer



class hostAttackLayer(basicHostAttackLayer) :

	def __init__(self,hostID,logFile,IPCLayer,NetworkServiceLayer) :
		basicHostAttackLayer.__init__(self,hostID,logFile,IPCLayer,NetworkServiceLayer)
		

	# Transmit to another node through the Network Simulator using UDP.
	# Network Service Layer will automatically resolve dstNodeID to an IP Address
	# Arguments:
	#	pkt 	  - <string>
	# 	dstNodeID - <int> Node ID of intended recipient
	def txNetServiceLayer(self,pkt,dstNodeID) :
		basicHostAttackLayer.txNetServiceLayer(self,pkt,dstNodeID)

	# Gets a pkt (string) received by the Network Layer if one is present.
	# Otherwise it returns None
	# Returns:
	#	pkt		 - <string>
	def rxNetServiceLayer(self) :
		return basicHostAttackLayer.rxNetServiceLayer(self)

	# Takes a pkt (string) as argument and relays it to IPC Layer of host
	# which can then optionally relay it to Proxy (If it is not a Control Host)
	# Arguments:
	#	pkt		- <string>
	def txIPCLayer(self,pkt) :
		basicHostAttackLayer.txIPCLayer(self,pkt)

	#  Returns a dstNodeID,pkt tuple if available from the IPC Layer of the Host
	#  The Attack Layer can subsequently choose to relay it to Network Layer.
	#  Returns:
	#	(dstNodeID,pkt)		-(<int>,<string>)
	def rxIPCLayer(self) :
		return basicHostAttackLayer.rxIPCLayer(self)


	#  Could be arbitrarily modified to perform specific attacks
	#  using the API described.
	def run(self) :

		# Default Benign Attack Layer
		basicHostAttackLayer.run(self)












