
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


receiver = shared_buffer("test-buffer",False)
res = receiver.open()

assert(res > 0)
msg = ''

while len(msg) == 0 :
	Id,msg = receiver.read()
	time.sleep(1)

assert(Id==10)
assert(msg == "Hello World!")
print "msg received: msg = ",msg
receiver.close()
print "RECEIVER TEST SUCCEEDED"