import sys
import os
import logger
from logger import *
from basicNetworkServiceLayer import basicNetworkServiceLayer
import time

argList = sys.argv



def extractIPMapping(netCfgFile) :
	IPMapping = {}


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
	sys.exit(main())
	

