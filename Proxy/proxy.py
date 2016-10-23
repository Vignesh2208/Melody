import sys
import os
import logger
from logger import *
from proxyNetworkLayer import proxyNetworkServiceLayer
from proxyTransportLayer import proxyTransportLayer
from proxyIPCLayer import proxyIPCLayer
import time
import getopt
import traceback
import signal
import datetime
from datetime import *




def extractIPMapping(netCfgFile) :
	IPMapping = {}
	assert(os.path.isfile(netCfgFile) == True)
	lines = [line.rstrip('\n') for line in open(netCfgFile)]

	for line in lines:
		line = ' '.join(line.split())
		line = line.replace(" ","")
		splitLs = line.split(':')
		assert(len(splitLs) == 2)
		hostID = int(splitLs[0])
		IPAddr = splitLs[1]

		IPMapping[hostID] = IPAddr

	return IPMapping


def usage() :
	print "python proxy.py <options>"
	print "Options:"
	print "-h or --help"
	print "-c or --netcfg-file=  Absolute path to network Cfg File <required>"
	print "-l or --log-file=     Absolute path to log File <optional>"
	print "-r or --runt-time=    Run time of host in seconds before it is shut-down <optional - default forever>"
	print "-p or --power-sim-ip= IP Address of power simulator <optional - default 127.0.0.1>"
	sys.exit(0)

def parseOpts() :


	logFile = "stdout"
	runTime = 0
	powerSimIP="127.0.0.1"

	try:
		(opts, args) = getopt.getopt(sys.argv[1:],
			"hc:l:r:p:",
			[ "help", "netcfg-file=", "log-file=", "run-time=","power-sim-ip="])
	except getopt.GetoptError as e:
		printError(str(e))
		usage()
		return 1
	for (o, v) in opts:
		if o in ("-h", "--help"):
			usage()

		if o in ("-c", "--netcfg-file=") :
			netCfgFilePath = str(v)
		if o in ("-l", "--log-file=") :
			logFile = str(v)
		if o in ("-r", "--run-time=") :
			runTime = int(v)

		if o in ("-p", "--power-sim-ip=") :
			powerSimIP = str(v)
		

	assert(netCfgFilePath != None)
	return (netCfgFilePath,logFile,runTime,powerSimIP)
		


def main(netCfgFile,logFile,runTime,powerSimIP) :

	hostIPMap = extractIPMapping(netCfgFile)
	hostIDList = hostIPMap.keys()
	log = logger.Logger(logFile,"Host" + str(hostID) + ": ")
	
	IPCLayer = proxyIPCLayer(logFile,hostIDList)
	NetLayer = proxyNetworkServiceLayer(logFile,powerSimIP)
	TransportLayer = proxyTransportLayer(logFile,IPCLayer,NetLayer)

	assert(IPCLayer != None and NetLayer != None and TransportLayer != None)

	
	NetLayer.start()
	TransportLayer.start()
	IPCLayer.start()

	if runTime != 0 : # dont run forever
		time.sleep(runTime)
		IPCLayer.cancelThread()
		TransportLayer.cancelThread()
		IPCLayer.cancelThread()
	else :			  # run forever
		while True :
			time.sleep(1)

	IPCLayer.join()
	TransportLayer.join()
	NetLayer.join()

if __name__ == "__main__":

	netCfgFilePath,logFile,runTime,powerSimIP = parseOpts()
	sys.exit(main(netCfgFilePath,logFile,runTime,powerSimIP))
	



