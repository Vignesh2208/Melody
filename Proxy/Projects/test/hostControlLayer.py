import sys
import os
import threading
import shared_buffer
from shared_buffer import *
import logger
from logger import Logger
from defines import *
from basicHostIPCLayer import basicHostIPCLayer


class hostControlLayer(basicHostIPCLayer) :

	def __init__(self,hostID,logFile) :
		basicHostIPCLayer.__init__(self,hostID,logFile)


	def appendToTxBuffer(self,pkt) :
		basicHostIPCLayer.appendToTxBuffer(self,pkt)

	def getReceivedMsg(self) :
		return basicHostIPCLayer.getReceivedMsg(self)

	def appendToRxBuffer(self,pkt) :
		basicHostIPCLayer.appendToRxBuffer(self,pkt)

	def getPktToSend(self) :
		return basicHostIPCLayer.getPktToSend(self)

	def cancelThread(self):
		basicHostIPCLayer.cancelThread(self)

	def run(self) :
		basicHostIPCLayer.run(self)











