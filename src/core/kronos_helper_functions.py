"""Kronos Python API

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>
"""

import os
import time
from src.core.libs.gettimepid import gettimepid

kronos_file_name = "/proc/status"


def is_root():
	"""Checks if calling process has sudo permission
	
	:return: 1 - SUCCESS, 0 - FAILURE
	"""
	if os.geteuid() == 0 :
		return 1
	print "Needs to be run as root"
	return 0


def is_module_loaded():
	"""Checks if Kronos is loaded
	
	:return: 1 - SUCCESS, 0 - FAILURE
	"""
	if os.path.isfile(kronos_file_name):
		return 1
	else :
		print "Kronos module is not loaded"
		return 0


def get_current_virtual_time_pid(specified_pid):
	"""Get current virtual time of process with pid = specified_pid
	
	:param specified_pid: pid of process to check
	:type specified_pid: int
	:return: Virtual time secs (float) or Current real time secs (float) iff process is not controlled by Kronos
	"""
	
	return float(gettimepid(specified_pid))


def get_current_virtual_time():
	"""Return current virtual time during a live Kronos experiment
	
	:return: Virtual time secs (float) or Current real time secs (float) iff there is no live Kronos experiment running
			 at the time of the call.
	"""
	curr_time = get_current_virtual_time_pid(0)
	if curr_time == 0.0:
		return time.time()     
	return curr_time

