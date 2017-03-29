import time
import sys
import os
import ctypes
from ctypes import *

#script_dir = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(script_dir + "/../core")

#import core
from core.timekeeper_functions import *
libc = CDLL("libc.so.6")

class Timespec(ctypes.Structure):
	""" timespec struct for nanosleep, see:
      	http://linux.die.net/man/2/nanosleep """
	_fields_ = [('tv_sec', ctypes.c_long),
	('tv_nsec', ctypes.c_long)]

libc.nanosleep.argtypes = [ctypes.POINTER(Timespec),
                           ctypes.POINTER(Timespec)]


def usleep(us):

    nanosleep_req = Timespec()
    nanosleep_rem = Timespec()
	#print('nsleep: {0:.9f}'.format(us)) 
    """ Delay microseconds with libc nanosleep() using ctypes. """
    if (us >= 1000000):
        sec = us/1000000
        us %= 1000000
    else: 
        sec = 0
    nanosleep_req.tv_sec = int(sec)
    nanosleep_req.tv_nsec = int(us * 1000)

    libc.nanosleep(nanosleep_req, nanosleep_rem)


def sleep(duration):

    # Check if the provided input value is integer by using float().is_integer()
    
    #usleep(int(duration*1000000))   
    time.sleep(float(duration))

    #if float(duration).is_integer():
        #libc.sleep(int(duration))
		#usleep(int(duration)*1000000)
    #else:
        #start_time = time.time()
        #while time.time() - start_time < duration:
            #usleep(500000)


def sleep_vt(duration):
    #TODO: Replace with get_virtual_time and sleep in virtual time
    #time.sleep(duration)
    curr_time = get_current_virtual_time()
    expire_time = curr_time + duration
    while curr_time < expire_time :
        time.sleep(0.5)
        curr_time = get_current_virtual_time()

def get_current_vt() :
    return get_current_virtual_time()

def get_current_vt_specified_pid(specified_pid):
    return get_current_virtual_time_specified_pid(specified_pid)

def main():
    print "sleeping for 5.2"
    sleep(5.2)
    print "sleeping for 5.0"
    sleep(5.0)


if __name__ == "__main__":
    main()

