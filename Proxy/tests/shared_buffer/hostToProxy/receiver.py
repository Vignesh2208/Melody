from shared_buffer import shared_buffer
import time


receiver = shared_buffer("test-buffer",True)
res = receiver.open()

assert(res > 0)
msg = ''

while len(msg) == 0 :
	Id,msg = receiver.read()
	time.sleep(1)

assert(Id==0)
assert(msg == "Hello World!")
print "msg received: msg = ",msg
receiver.close()
print "RECEIVER TEST SUCCEEDED"