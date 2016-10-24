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