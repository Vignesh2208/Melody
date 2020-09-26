import time
import sys
import os
import subprocess

def set_cpu_affinity(pid) :
    taskset_cmd = "sudo taskset -cp 0,1 " + str(pid) + " > /dev/null"
    subprocess.Popen(taskset_cmd, shell=True)

def set_def_cpu_affinity(pid,cpu_subset_str) :
    taskset_cmd = "sudo taskset -cp " + cpu_subset_str + " " + str(pid) + " > /dev/null"
    #os.system("sudo taskset -cp " + cpu_subset_str + " " + str(pid) + " > /dev/null")
    subprocess.Popen(taskset_cmd, shell=True)
def set_cpu_affinity_pid_list(pid_list) :
    for pid in pid_list :
        set_cpu_affinity(pid)

def procStatus(pid):
    for line in open("/proc/%d/status" % pid).readlines():
        if line.startswith("State:"):
            return line.split(":",1)[1].strip().split(' ')[0]
    return None

def get_pids_with_cmd(cmd, expected_no_of_pids=1) :
    pid_list = []

    while  len(pid_list) < expected_no_of_pids :
        time.sleep(0.5)
        pid_list = []
        try:
	        ps_output = subprocess.check_output(
                "ps -e -o command:200,pid | grep '^" + cmd + "'", shell=True)
        except subprocess.CalledProcessError:
	        ps_output = ""

        if len(ps_output) > 0 :
            for p in ps_output.decode("ascii").split('\n'):
                p_tokens = p.split()
                if not p_tokens:
	                continue
                pid = int(p_tokens[len(p_tokens)-1])
                if procStatus(pid) != 'D' :
                    pid_list.append(pid)



    return pid_list

def representsInt(s) :
    try:
        int(s)
        return True
    except ValueError:
        return False

def get_thread_ids(pid):
    cmd = "ps -e -T | grep " + str(pid)
    output = subprocess.check_output(cmd, shell=True)
    output = output.decode("ascii").split("\n")
    threads = []
    for line in output:
        line = line.split(" ")
        if len(line) > 0:
            i = 0
            for i in range(0,len(line)) :
                if len(line[i]) > 0 and representsInt(line[i]) and int(line[i]) == pid:
                    for j in range(i+1,len(line)) :
                        if len(line[j]) > 0 :
                            if representsInt(line[j]) and int(line[j]) != pid :
                                threads.append(int(line[j]))
                            break
                    break
    return threads

