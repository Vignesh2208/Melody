
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

sender = shared_buffer("test-buffer",True)
res = sender.open()

assert res > 0
msg = "Hello World!"
print "sending msg: ", msg
res = sender.write(msg,dstID=10)
assert (res == len(msg))
print "SENDER SUCCEEDED"
#while 1 :
#	time.sleep(1)