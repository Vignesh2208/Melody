import datetime
import json
import os
import uuid
from datetime import datetime
from shared_buffer import *
from utils.sleep_functions import sleep
from utils.util_functions import *
from defines import *
from timekeeper_functions import *
import subprocess
import sys
import os
from fractions import gcd
import threading

NS_PER_MS = 1000000

import ctypes
libc = ctypes.cdll.LoadLibrary('libc.so.6')




class progressTimelineThread(threading.Thread):
    def __init__(self, timeline_id, netpower_obj,sharedBufferArray):
        threading.Thread.__init__(self)
        self.timeline_id = timeline_id
        self.netpower_obj = netpower_obj
        self.control_pids = self.netpower_obj.timeline_to_pids[self.timeline_id]
        self.progress_interval = self.netpower_obj.timeslice
        self.sharedBufferArray = sharedBufferArray


    def init_shared_buf_array(self):
        self.cmd_channel_bufName = "Timeline-" + str(self.timeline_id) + "-cmd-channel-buffer"
        result = self.sharedBufferArray.open(self.cmd_channel_bufName,isProxy=False)

    def recv_from_main_process(self):
        recv_msg = ''
        dummy_id, recv_msg = self.sharedBufferArray.read("cmd-channel-buffer")
        return recv_msg

    def send_finished_msg(self):
        ret = 0
        while ret <= 0:
            ret = self.sharedBufferArray.write(self.cmd_channel_bufName,"FYN", 0)

    def wait_for_progress_cmd(self):
        while True:
            recv_msg = self.sharedBufferArray.read(self.cmd_channel_bufName)
            if recv_msg == "PROGRESS":
                return 0
            if recv_msg == "STOP":
                return -1

    def getThreadId(self):
        """Returns OS thread id - Specific to Linux"""
        return libc.syscall(186)

    def run(self):

        print "Progress Thread for Timeline: ", self.timeline_id, " ThreadID = ", self.getThreadId()
        reset_timeline(self.timeline_id)
        while True:
            res = self.wait_for_progress_cmd()
            if res == -1:
                break
            for pid in self.control_pids :
                set_interval(pid, self.progress_interval, self.timeline_id)
            progress(self.timeline_id,self.getThreadId(),1)
            reset_timeline(self.timeline_id)
            self.send_finished_msg()


class progress_helper:
    def __init__(self,netpower_obj):

        self.netpower_obj = netpower_obj
        self.sharedBufferArray  = self.netpower_obj.sharedBufferArray
        for i in xrange(0,N_TIMEKEEPER_CPUS):
            result = self.netpower_obj.sharedBufferArray.open(bufName="Timeline-" + str(i) + "-cmd-channel-buffer",isProxy=True)
            if result == BUF_NOT_INITIALIZED or result == FAILURE:
                print "Shared Buffer open failed! Buffer not initialized for timeline: " + str(i)
                sys.exit(0)

        self.progress_threads = []
        self.n_timelines = N_TIMEKEEPER_CPUS
        for i in xrange(0,self.n_timelines):
            self.progress_threads.append(progressTimelineThread(i,self.netpower_obj,self.sharedBufferArray))

        print "STARTING PROGRESS THREADS ..."
        for i in xrange(0,self.n_timelines) :
            curr_thread = self.progress_threads[i]
            curr_thread.start()

    def send_progress_cmd(self):
        for i in xrange(0,self.n_timelines) :
            ret = 0
            while ret <= 0:
                ret = self.sharedBufferArray.write("Timeline-" + str(i) + "-cmd-channel-buffer", "PROGRESS", 0)

    def send_stop_cmd(self):
        for i in xrange(0,self.n_timelines) :
            ret = 0
            while ret <= 0:
                ret = self.sharedBufferArray.write("Timeline-" + str(i) + "-cmd-channel-buffer", "STOP", 0)


    def recv_msg_from_timeline(self,timeline_id):
        recv_msg = ''
        dummy_id, recv_msg = self.sharedBufferArray.read("Timeline-" + str(timeline_id) + "-cmd-channel-buffer")
        return recv_msg

    def wait_for_all_fyns(self):
        curr_timeline = 0
        while True :
            recv_msg = self.recv_msg_from_timeline(curr_timeline)
            if recv_msg == "FYN":
                curr_timeline = curr_timeline + 1

            if curr_timeline >= self.n_timelines :
                break

    def progress_all_timelines(self):
        self.send_progress_cmd()
        self.wait_for_all_fyns()

    def stop_all_progress_threads(self):

        print "STOPPING PROGRESS THREADS ..."
        for i in xrange(0,self.n_timelines) :
            self.send_stop_cmd()

        for i in xrange(0,self.n_timelines) :
            curr_thread = self.progress_threads[i]
            curr_thread.join()

        print "PROGRESS THREADS STOPPED ..."















