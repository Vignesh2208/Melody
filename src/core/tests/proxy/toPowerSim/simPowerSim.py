import socket
import sys
import os

scriptDir = os.path.dirname(os.path.realpath(__file__))
idx = scriptDir.index('NetPower_TestBed')
srcDir = scriptDir[0:idx] + "NetPower_TestBed/src"
proxyDir = scriptDir[0:idx] + "NetPower_TestBed/src/core"
if srcDir not in sys.path:
	sys.path.append(srcDir)

if proxyDir not in sys.path:
	sys.path.append(proxyDir)

from defines import *

HOST_IP = "127.0.0.1"
HOST_PORT = POWERSIM_UDP_PORT 


sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.bind((HOST_IP, HOST_PORT))

print "Waiting for data from core ..."
data, addr = sock.recvfrom(MAXPKTSIZE)

if len(data) > 0 :
	assert(data == "Hello World!")
	print "POWER SIM TEST SUCCEEDED"