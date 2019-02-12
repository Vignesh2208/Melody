#
# File  : kronos_helper_functions.py
# 
# Brief : Exposes A few kronos helper functions API in python
#
# authors : Vignesh Babu
#


import os
import time
from src.core.libs.gettimepid import gettimepid

KRONOS_FILE_NAME = "/proc/status"

def is_root() :

	if os.geteuid() == 0 :
		return 1
	print "Needs to be run as root"
	return 0


def is_module_loaded() :

	if os.path.isfile(KRONOS_FILE_NAME) == True:
		return 1
	else :
		print "Kronos module is not loaded"
		return 0



		
def get_current_virtual_time_pid(specified_pid) :
    return float(gettimepid(specified_pid))



def get_current_virtual_time() :
    
    curr_time = get_current_virtual_time_pid(0)
    if curr_time == 0.0 :
        return time.time()     
    return curr_time

