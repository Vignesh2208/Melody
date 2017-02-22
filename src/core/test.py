from utils.sleep_functions import sleep
import sys
from datetime import datetime
import time

for i in xrange(0,10) :
	print "Before = ", str(datetime.now())
	sys.stdout.flush()
	time.sleep(1)
	print "After = ", str(datetime.now())
	print "################################################"
	sys.stdout.flush()
