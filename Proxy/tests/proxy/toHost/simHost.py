from shared_buffer import shared_buffer
import time


receiver = shared_buffer("1buffer",False)
res = receiver.open()

assert(res > 0)
msg = ''

while len(msg) == 0 :
	Id,msg = receiver.read()
	time.sleep(1)

assert(Id == 1)
assert(msg == "Hello World!")
print "msg received: msg = ",msg
receiver.close()
print "RECEIVER TEST SUCCEEDED"