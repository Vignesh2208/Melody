import time
from datetime import datetime
import sys
import ctypes
libc = ctypes.CDLL('libc.so.6')

class Timespec(ctypes.Structure):
	""" timespec struct for nanosleep, see:
      	http://linux.die.net/man/2/nanosleep """
	_fields_ = [('tv_sec', ctypes.c_long),
	('tv_nsec', ctypes.c_long)]

libc.nanosleep.argtypes = [ctypes.POINTER(Timespec),
                           ctypes.POINTER(Timespec)]
nanosleep_req = Timespec()
nanosleep_rem = Timespec()

def nsleep(us):
	#print('nsleep: {0:.9f}'.format(us)) 
	""" Delay microseconds with libc nanosleep() using ctypes. """
	if (us >= 1000000):
		sec = us/1000000
		us %= 1000000
	else: sec = 0
	nanosleep_req.tv_sec = sec
	nanosleep_req.tv_nsec = int(us * 1000)

	libc.nanosleep(nanosleep_req, nanosleep_rem)


arg_list = sys.argv
node_ip = 3
node_ip = arg_list[1]


with open("/home/vignesh/Desktop/emane-Timekeeper/experiment-data/" + str(node_ip),"w" ) as f :
	pass

with open("/home/vignesh/Desktop/emane-Timekeeper/experiment-data/" + str(node_ip),"a" ) as f :

	i = 0
	while i < 50 :
		curr_time = str(datetime.now())
		sys.stdout.write("Curr Time = " +  curr_time + "\n")
		sys.stdout.flush()
		nsleep(1000000)
		i = i + 1

	sys.stdout.write("Finished script\n")
	sys.stdout.flush()

