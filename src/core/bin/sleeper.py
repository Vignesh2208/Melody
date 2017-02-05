import datetime
import time
import sys
import ctypes
from ctypes import CDLL

libc = CDLL("libc.so.6")

while 1 :

	print "Before = ", datetime.datetime.now()
	sys.stdout.flush()
	#time.sleep(1)
	libc.sleep(1)
	print "After = ", datetime.datetime.now()
	sys.stdout.flush()
