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

from shared_buffer import shared_buffer
import time
CONTROL_NODE_ID = 2


sender = shared_buffer("1buffer",True)
res = sender.open()

assert(res > 0)
msg = 'Hello World!'
res = sender.write(msg,dstID=2)


assert(res >  0)
sender.close()
print "SENDER TEST SUCCEEDED"