import shared_buf
import sys
import os
from definitions import *


class shared_buffer(object) :
	def __init__(bufName,isProxy) :
		self.bufName = bufName
		self.isProxy = isProxy

		shared_buf.init()
	
	def open(self) :

		result = shared_buf.open(self.sharedBufName, self.isProxy)
		return result

	def close(self) :
		shared_buf.close()

	def read(self) :
		return shared_buf.read(self.sharedBufName,self.isProxy)

	def write(self,msg,dstID=PROXY_NODE_ID) :
		return shared_buf.write(self.sharedBufName,str(msg),len(str(msg)),dstID)

