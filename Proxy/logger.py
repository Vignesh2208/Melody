import sys
import os


class Logger(object) :

	def __init__(self,logFile,tag) :

		if logFile != "stdout" :
			with open(logFile,"w") as f :
				pass
			self.printable = False
		else:
			self.printable = True

		self.logFile = logFile
		self.tag = tag


		assert(self.logLevel == "INFO" or self.logLevel == "DEBUG" or self.logLevel == "ERROR")

	def logMsg(self,loglevel,tag,msg) :
		if self.printable == True :
			print(str(tag) + " >> " + strl(loglevel) + " << " + str(msg))
		else :
			with open(self.logFile,"a") as f :
				f.write(str(tag) + " >> " + strl(loglevel) + " << " + str(msg) + "\n")

	def info(self,msg) :
		self.logMsg("INFO",self.tag,msg) 

	def warn(self,msg) :
		self.logMsg("WARN",self.tag,msg) 

	def error(self,msg) :
		self.logMsg("ERROR",self.tag,msg)
