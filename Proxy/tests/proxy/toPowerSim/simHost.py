from shared_buffer import shared_buffer
import time
PROXY_NODE_ID = 0


sender = shared_buffer("1buffer",False)
res = sender.open()

assert(res > 0)
msg = 'Hello World!'
res = sender.write(msg,dstID=PROXY_NODE_ID)


assert(res >  0)
sender.close()
print "SENDER TEST SUCCEEDED"