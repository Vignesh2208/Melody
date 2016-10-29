import socket
import sys
import os

scriptDir = os.path.dirname(os.path.realpath(__file__))
idx = scriptDir.index('NetPower_TestBed')
srcDir = scriptDir[0:idx] + "NetPower_TestBed/src"
proxyDir = scriptDir[0:idx] + "NetPower_TestBed/src/Proxy"
if srcDir not in sys.path:
	sys.path.append(srcDir)

if proxyDir not in sys.path:
	sys.path.append(proxyDir)

from defines import *

HOST_IP = "127.0.0.1"
HOST_PORT = PROXY_UDP_PORT
MESSAGE = "0000000011powerworld1Hello World!"

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (HOST_IP, HOST_PORT))

print "Power Sim Msg Sent"