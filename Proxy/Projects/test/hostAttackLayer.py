import sys
import os
import threading
import shared_buffer
from shared_buffer import *
import Proxy.logger
from Proxy.logger import Logger
from Proxy.defines import *
from Proxy.basicHostAttackLayer import basicHostAttackLayer



class hostAttackLayer(basicHostAttackLayer) :

	def __init__(self,hostID,logFile,IPCLayer,NetworkServiceLayer) :
		basicHostAttackLayer.__init__(hostID,logFile,IPCLayer,NetworkServiceLayer)
		

	def txNetServiceLayer(self,pkt,dstNodeID) :
		basicHostAttackLayer.txNetServiceLayer(pkt,dstNodeID)

	def rxNetServiceLayer(self) :
		return basicHostAttackLayer.rxNetServiceLayer()

	def txIPCLayer(self,pkt) :
		basicHostAttackLayer.txIPCLayer(pkt)

	def rxIPCLayer(self) :
		return basicHostAttackLayer.rxIPCLayer()

	def getcurrCmd(self) :
		return basicHostAttackLayer.getcurrCmd()

	def cancelThread(self):
		basicHostAttackLayer.cancelThread()


	def run(self) :
		basicHostAttackLayer.run()












