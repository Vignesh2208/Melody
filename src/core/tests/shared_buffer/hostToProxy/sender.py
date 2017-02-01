import sys
import os
import time

scriptDir = os.path.dirname(os.path.realpath(__file__))
idx = scriptDir.index('NetPower_TestBed')
srcDir = scriptDir[0:idx] + "NetPower_TestBed/src"
proxyDir = scriptDir[0:idx] + "NetPower_TestBed/src/core"
if srcDir not in sys.path:
	sys.path.append(srcDir)

if proxyDir not in sys.path:
	sys.path.append(proxyDir)

from shared_buffer import shared_buffer
import time

sender = shared_buffer("test-buffer",False)
res = sender.open()

assert res > 0
msg = "Hello World!"
print("sending msg: ", msg)
res = 0
while res <= 0 :
	res = sender.write(msg,dstID=0)
	time.sleep(1)



assert (res == len(msg))
print("SENDER SUCCEEDED")
