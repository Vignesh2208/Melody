import sys
import os

from logger import *
from proxyNetworkLayer import proxyNetworkServiceLayer
from proxyTransportLayer import proxyTransportLayer
from proxyIPCLayer import proxyIPCLayer
import time
import getopt
import socket
print sys.path
#sys.path.insert(0, '/home/user/Desktop/NetPower_TestBed/src')
#print sys.path
from utils.sleep_functions import sleep



def extractIPMapping(netCfgFile) :
	IPMapping = {}
	PowerSimIdMapping = {}
	assert(os.path.isfile(netCfgFile) == True)
	lines = [line.rstrip('\n') for line in open(netCfgFile)]

	for line in lines:
		line = ' '.join(line.split())
		line = line.replace(" ","")
		splitLs = line.split(',')
		assert(len(splitLs) >= 3)
		hostID = int(splitLs[0][1:])
		IPAddr = splitLs[1]
		Port = int(splitLs[2])

		IPMapping[hostID] = (IPAddr,Port)
		for i in xrange(3, len(splitLs)):
			PowerSimId = str(splitLs[i])
			if hostID not in PowerSimIdMapping.keys():
				PowerSimIdMapping[hostID] = []
			PowerSimIdMapping[hostID].append(PowerSimId)

	return IPMapping,PowerSimIdMapping


def usage() :
	print "python proxy.py <options>"
	print "Options:"
	print "-h or --help"
	print "-c or --netcfg-file=  Absolute path to network Cfg File <required>"
	print "-l or --log-file=     Absolute path to log File <optional>"
	print "-r or --runt-time=    Run time of host in seconds before it is shut-down <optional - default forever>"
	print "-p or --power-sim-ip= IP Address of power simulator <optional - default 127.0.0.1>"
	print "-d or --id= 			 ID of control center node. <optional - default taken as max of all host IDs>"
	sys.exit(0)

def parseOpts() :


	logFile = "stdout"
	runTime = 0
	powerSimIP="127.0.0.1"
	netCfgFilePath = None
	controlCenterID = None

	try:
		(opts, args) = getopt.getopt(sys.argv[1:],
			"hc:l:r:p:d:",
			[ "help", "netcfg-file=", "log-file=", "run-time=","power-sim-ip=","id="])
	except getopt.GetoptError as e:
		print (str(e))
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

		if o in ("-d", "--id="):
			controlCenterID = int(v)

	assert(netCfgFilePath != None)
	return (netCfgFilePath,logFile,runTime,powerSimIP,controlCenterID)
		


def main(netCfgFile,logFile,runTime,powerSimIP,controlCenterID) :

	hostIPMap,powerSimIdMap = extractIPMapping(netCfgFile)
	hostIDList = hostIPMap.keys()

	#print "HostID List = ", hostIDList

	if controlCenterID == None :
		controlCenterID = max(hostIDList)
	
	IPCLayer = proxyIPCLayer(logFile,hostIDList)
	IPCLayer.setControlCenterID(controlCenterID)
	IPCLayer.setPowerSimIdMap(powerSimIdMap)
	NetLayer = proxyNetworkServiceLayer(logFile,powerSimIP)
	TransportLayer = proxyTransportLayer(logFile,IPCLayer,NetLayer)

	assert(IPCLayer != None and NetLayer != None and TransportLayer != None)

	IPCLayer.setTransportLayer(TransportLayer)
	NetLayer.setTransportLayer(TransportLayer)
	
	NetLayer.start()
	TransportLayer.start()
	IPCLayer.start()

	if runTime != 0 : # dont run forever
		sleep(runTime)
		IPCLayer.cancelThread()
		TransportLayer.cancelThread()
		NetLayer.cancelThread()
	else :			  # run forever
		while True :
			sleep(1)

	IPCLayer.join()
	TransportLayer.join()
	NetLayer.join()

	#print "Proxy Shut Down Successfully"

if __name__ == "__main__":

	netCfgFilePath,logFile,runTime,powerSimIP,controlCenterID = parseOpts()
	sys.exit(main(netCfgFilePath,logFile,runTime,powerSimIP,controlCenterID))
	



