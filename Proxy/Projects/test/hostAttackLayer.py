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
		

	def txNetServiceLayer(self,pkt,dstNodeID) :
		basicHostAttackLayer.txNetServiceLayer(self,pkt,dstNodeID)

	def rxNetServiceLayer(self) :
		return basicHostAttackLayer.rxNetServiceLayer(self)

	def txIPCLayer(self,pkt) :
		basicHostAttackLayer.txIPCLayer(self,pkt)

	def rxIPCLayer(self) :
		return basicHostAttackLayer.rxIPCLayer(self)

	def getcurrCmd(self) :
		return basicHostAttackLayer.getcurrCmd(self)

	def cancelThread(self):
		basicHostAttackLayer.cancelThread(self)


	def run(self) :
		basicHostAttackLayer.run(self)












