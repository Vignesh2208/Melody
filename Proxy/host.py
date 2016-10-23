import sys
import os
import logger
from logger import *
from basicNetworkServiceLayer import basicNetworkServiceLayer
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
	print "python host.py <options>"
	print "Options:"
	print "-h or --help"
	print "-c or --netcfg-file=  Absolute path to network Cfg File <required>"
	print "-l or --log-file=     Absolute path to log File <optional>"
	print "-r or --runt-time=    Run time of host in seconds before it is shut-down <optional - default forever>"
	print "-n or --project-name= Name of project folder <optional - default is test project>"
	print "-i or --is-controller If specified, this node is invoked as the control station"
	sys.exit(0)

def parseOpts() :


	lenRequiredOpts = 2
	isController = False
	logFile = "stdout"
	runTime = 0
	projectName = "test"

	try:
		(opts, args) = getopt.getopt(sys.argv[1:],
			"hc:l:r:n:id:",
			[ "help", "netcfg-file=", "log-file=", "run-time=", "project-name=",
			  "is-control","id="])
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
		if o in ("-n", "--project-name=") :
			projectName = str(v)
		if o in ("-i", "--is-controller") :
			isController = True 
		if o in ("-d","--id=") :
			hostID = int(v)

	assert(netCfgFilePath != None and hostID != None)
	return (isController,netCfgFilePath,logFile,runTime,projectName,hostID)
		


def main(hostID,netCfgFile,logFile,runTime,projectName,isControlHost) :

	hostIPMap = extractIPMapping(netCfgFile)
	log = logger.Logger(logFile,"Host" + str(hostID) + ": ")
	
	if isControlHost == True :
		hostIPCLayer = __import__("Proxy.Projects." + str(projectName) + ".controlLayer", globals(), locals(), ['hostControlLayer'], -1)
		hostAttackLayer = __import__("Proxy.basicHostAttackLayer", globals(), locals(), ['basicHostAttackLayer'], -1)
	else:
		hostIPCLayer = __import__("Proxy.basicHostIPCLayer", globals(), locals(), ['basicHostIPCLayer'], -1)
		hostAttackLayer = __import__("Proxy.Projects." + str(projectName) + ".hostAttackLayer", globals(), locals(), ['hostAttackLayer'], -1)


	
	IPCLayer = hostIPCLayer(hostID,logFile)
	NetLayer = basicNetworkServiceLayer(hostID,logFile,hostIPMap)
	AttackLayer = hostAttackLayer(hostID,logFile,IPCLayer,NetLayer)

	assert(IPCLayer != None and NetLayer != None and AttackLayer != None)

	
	NetLayer.start()
	AttackLayer.start()
	IPCLayer.start()

	if runTime != 0 : # dont run forever
		time.sleep(runTime)
		IPCLayer.cancelThread()
		AttackLayer.cancelThread()
		IPCLayer.cancelThread()
	else :			  # run forever
		while True :
			time.sleep(1)

	IPCLayer.join()
	AttackLayer.join()
	NetLayer.join()

if __name__ == "__main__":

	isController,netCfgFilePath,logFile,runTime,projectName,hostID = parseOpts()
	sys.exit(main(hostID,netCfgFilePath,logFile,runTime,projectName,isController))
	

