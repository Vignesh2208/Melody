import sys
import os

scriptDir = os.path.dirname(os.path.realpath(__file__))
if scriptDir not in sys.path:
	sys.path.append(scriptDir)

srcDir = scriptDir + "/.."
if srcDir not in sys.path:
	sys.path.append(srcDir)

import logger
from logger import *
from basicNetworkServiceLayer import basicNetworkServiceLayer
import time
import getopt
import traceback
import signal





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
		IPMapping[hostID] = (IPAddr, Port)

		for i in xrange(3,len(splitLs)) :
			PowerSimId = str(splitLs[i])
			if hostID not in PowerSimIdMapping.keys() :
				PowerSimIdMapping[hostID] = []
			PowerSimIdMapping[hostID].append(PowerSimId)

	return IPMapping,PowerSimIdMapping


def usage() :
	print "python host.py <options>"
	print "Options:"
	print "-h or --help"
	print "-c or --netcfg-file=  Absolute path to network Cfg File <required>"
	print "-l or --log-file=     Absolute path to log File <optional>"
	print "-r or --run-time=    Run time of host in seconds before it is shut-down <optional - default forever>"
	print "-n or --project-name= Name of project folder <optional - default is test project>"
	print "-i or --is-controller If specified, this node is invoked as the control station"
	print "-d or --id= Id of the node. Required and must be > 0"
	sys.exit(0)

def parseOpts() :


	lenRequiredOpts = 2
	isController = False
	netCfgFilePath = None
	hostID = None
	logFile = "stdout"
	runTime = 0
	projectName = "test"

	try:
		(opts, args) = getopt.getopt(sys.argv[1:],
			"hc:l:r:n:id:",
			[ "help", "netcfg-file=", "log-file=", "run-time=", "project-name=",
			  "is-control","id="])
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
		if o in ("-n", "--project-name=") :
			projectName = str(v)
		if o in ("-i", "--is-controller") :
			isController = True 
		if o in ("-d","--id=") :
			hostID = int(v)

	assert(netCfgFilePath != None and hostID != None)
	return (isController,netCfgFilePath,logFile,runTime,projectName,hostID)
		


def main(hostID,netCfgFile,logFile,runTime,projectName,isControlHost) :

	hostIPMap,powerSimIdMap = extractIPMapping(netCfgFile)
	log = logger.Logger(logFile,"Host" + str(hostID) + ": ")
	
	if isControlHost == True :
		hostIPCLayer = __import__("Projects." + str(projectName) + ".hostControlLayer", globals(), locals(), ['hostControlLayer'], -1)
		hostIPCLayer = hostIPCLayer.hostControlLayer
		hostAttackLayer = __import__("basicHostAttackLayer", globals(), locals(), ['basicHostAttackLayer'], -1)
		hostAttackLayer = hostAttackLayer.basicHostAttackLayer
	else:
		hostIPCLayer = __import__("basicHostIPCLayer", globals(), locals(), ['basicHostIPCLayer'], -1)
		hostIPCLayer = hostIPCLayer.basicHostIPCLayer
		hostAttackLayer = __import__("Projects." + str(projectName) + ".hostAttackLayer", globals(), locals(), ['hostAttackLayer'], -1)
		hostAttackLayer = hostAttackLayer.hostAttackLayer

	
	IPCLayer = hostIPCLayer(hostID,logFile)
	IPCLayer.setPowerSimIdMap(powerSimIdMap)
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
		NetLayer.cancelThread()
	else :			  # run forever
		while True :
			time.sleep(1)


	IPCLayer.join()
	AttackLayer.join()
	NetLayer.join()

	print "Shutting Down Host ", hostID

if __name__ == "__main__":

	isController,netCfgFilePath,logFile,runTime,projectName,hostID = parseOpts()
	sys.exit(main(hostID,netCfgFilePath,logFile,runTime,projectName,isController))
	

