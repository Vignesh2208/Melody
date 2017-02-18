import time
import sys
import os
import subprocess

def set_cpu_affinity(pid) :
    taskset_cmd = "sudo taskset -cp 0,1 " + str(pid) + " > /dev/null"
    subprocess.Popen(taskset_cmd, shell=True)

def set_cpu_affinity_pid_list(pid_list) :
    for pid in pid_list :
        set_cpu_affinity(pid)


def get_pids_with_cmd(cmd) :
    pid_list = []
    try:
	    ps_output = subprocess.check_output("ps -e -o command:200,pid | grep '^" + cmd + "'", shell=True)
    except subprocess.CalledProcessError:
	    print ps_output

    for p in ps_output.split('\n'):
        p_tokens = p.split()
        if not p_tokens:
	        continue
        pid = int(p_tokens[len(p_tokens)-1])
        pid_list.append(pid)

    return pid_list
