from shared_buffer import shared_buffer
import time

sender = shared_buffer("test-buffer",False)
res = sender.open()

assert res > 0
msg = "Hello World!"
print "sending msg: ", msg
res = sender.write(msg,dstID=0)
assert (res == len(msg))
print "SENDER SUCCEEDED"
