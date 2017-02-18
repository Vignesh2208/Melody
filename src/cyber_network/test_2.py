import sys
import time
from datetime import datetime

for i in xrange(0,100) :
	print "Before = ", str(datetime.now())
	sys.stdout.flush()
	time.sleep(1)
	print "After = ", str(datetime.now())
	print "################################################"
	sys.stdout.flush()
