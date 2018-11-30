import sys
import os
import shared_buffer
from shared_buffer import  *
import logger
from logger import *
from basicNetworkServiceLayer import basicNetworkServiceLayer
import time
import getopt
import traceback
import signal
from utils.sleep_functions import sleep
import time
import datetime
from datetime import datetime

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
        (opts, args) = getopt.getopt(sys.argv[1:],"hc:l:r:n:id:",[ "help", "netcfg-file=", "log-file=", "run-time=", "project-name=","is-control","id="])
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
	

def init_shared_buffers(hostID,runTime,sharedBufferArray):

    result = sharedBufferArray.open(bufName="h" + str(hostID) + "main-cmd-channel-buffer",isProxy=False)

    if result == BUF_NOT_INITIALIZED or result == FAILURE:
        print "Cmd channel buffer open failed!. Not starting any threads !"
        sys.stdout.flush()
        if runTime == 0 :
            while True:
                sleep(1)

        start_time = time.time()
        sleep(runTime + 2)
        while time.time() < start_time + float(runTime):
            sleep(1)
        sys.exit(0)

def main(hostID,netCfgFile,logFile,runTime,projectName,isControlHost) :

    hostIPMap,powerSimIdMap = extractIPMapping(netCfgFile)
    log = logger.Logger(logFile,"Host" + str(hostID) + ": ")

    sharedBufferArray = shared_buffer_array()
	
    if isControlHost == True :
        hostIPCLayer = __import__("projects." + str(projectName) + ".hostControlLayer", globals(), locals(), ['hostControlLayer'], -1)
        hostIPCLayer = hostIPCLayer.hostControlLayer
        hostAttackLayer = __import__("projects." + str(projectName) + ".hostAttackLayer", globals(), locals(),['hostAttackLayer'], -1)
        hostAttackLayer = hostAttackLayer.hostAttackLayer
    else:
        hostIPCLayer = __import__("basicHostIPCLayer", globals(), locals(), ['basicHostIPCLayer'], -1)
        hostIPCLayer = hostIPCLayer.basicHostIPCLayer
        hostAttackLayer = __import__("projects." + str(projectName) + ".hostAttackLayer", globals(), locals(), ['hostAttackLayer'], -1)
        hostAttackLayer = hostAttackLayer.hostAttackLayer

    print "Initializing main channel buffer"
    sys.stdout.flush()
    init_shared_buffers(hostID, runTime,sharedBufferArray)

    print "Cmd channel buffer open suceeded !"
    sys.stdout.flush()

    IPCLayer = hostIPCLayer(hostID,logFile,sharedBufferArray)
    IPCLayer.setPowerSimIdMap(powerSimIdMap)
    NetLayer = basicNetworkServiceLayer(hostID,logFile,hostIPMap)
    AttackLayer = hostAttackLayer(hostID,logFile,IPCLayer,NetLayer,sharedBufferArray)
    IPCLayer.setAttackLayer(AttackLayer)
    NetLayer.setAttackLayer(AttackLayer)
    assert(IPCLayer != None and NetLayer != None and AttackLayer != None)


    print "Waiting for start command ... buf = ", "h" + str(hostID) + "main-cmd-channel-buffer"
    sys.stdout.flush()
    recv_msg = ''
    while "START" not in recv_msg:
        recv_msg = ''
        dummy_id, recv_msg = sharedBufferArray.read("h" + str(hostID) + "main-cmd-channel-buffer")
        print "Finished 1 iter ... "
        time.sleep(0.1)


    NetLayer.start()
    AttackLayer.start()
    IPCLayer.start()
    print "Signalled Start threads at ", str(datetime.now())
    sys.stdout.flush()
    recv_msg = ''

    print "Waiting for exit command ..."
    sys.stdout.flush()
    i = 1
    while "EXIT" not in recv_msg:
        recv_msg = ''
        print "Checking for EXIT for the ", i ," time at: ", str(datetime.now())
        i = i + 1
        sys.stdout.flush()
        dummy_id, recv_msg = sharedBufferArray.read("h" + str(hostID) + "main-cmd-channel-buffer")
        print "Finished 1 iter ... "
        time.sleep(0.1)


    IPCLayer.cancelThread()
    AttackLayer.cancelThread()
    NetLayer.cancelThread()


    #IPCLayer.join()
    #AttackLayer.join()
    #NetLayer.join()

    print "Shutting Down Host ", hostID
    sys.stdout.flush()

if __name__ == "__main__":

    isController,netCfgFilePath,logFile,runTime,projectName,hostID = parseOpts()
    sys.exit(main(hostID,netCfgFilePath,logFile,runTime,projectName,isController))
	

