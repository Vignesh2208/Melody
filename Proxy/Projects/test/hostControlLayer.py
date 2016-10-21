import sys
import os
import threading
import shared_buffer
from shared_buffer import *
import Proxy.logger
from Proxy.logger import Logger
from Proxy.defines import *
from Proxy.basicHostIPCLayer import basicHostIPCLayer


class hostControlLayer(basicHostIPCLayer) :

	def __init__(self,hostID,logFile) :
		basicHostIPCLayer.__init__(hostID,logFile)


	def appendToTxBuffer(self,pkt) :
		basicHostIPCLayer.appendToTxBuffer(pkt)

	def getReceivedMsg(self) :
		return basicHostIPCLayer.getReceivedMsg()

	def appendToRxBuffer(self,pkt) :
		basicHostIPCLayer.appendToRxBuffer(pkt)

	def getPktToSend(self) :
		return basicHostIPCLayer.getPktToSend()

	def cancelThread(self):
		basicHostIPCLayer.cancelThread()

	def run(self) :
		basicHostIPCLayer.run()











