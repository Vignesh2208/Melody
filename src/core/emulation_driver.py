import argparse
import os
import json
from utils.sleep_functions import sleep
from defines import *
import sys
import datetime
from datetime import datetime
import shared_buffer
from shared_buffer import  *
import time


class EmulationDriver(object):

    def __init__(self, input_params):

        self.type = input_params["type"]
        self.cmd = input_params["cmd"]
        self.offset = input_params["offset"]
        self.inter_flow_period = input_params["inter_flow_period"]
        self.run_time = input_params["run_time"]
        self.long_running = input_params["long_running"]
        self.root_user_name = input_params["root_user_name"]
        self.root_password = input_params["root_password"]
        self.driver_id = input_params["driver_id"]

        self.init_shared_buffers(self.driver_id, self.run_time)
        
    def init_shared_buffers(self,driver_id,run_time):
       
        self.sharedBufferArray = shared_buffer_array()
        result = self.sharedBufferArray.open(bufName=str(driver_id) + "main-cmd-channel-buffer",isProxy=False)

        if result == BUF_NOT_INITIALIZED or result == FAILURE:
            print "Cmd channel buffer open failed!. Not starting any processe !"
            if run_time == 0 :
                while True:
                    sleep(1)
                    
            start_time = time.time()
            sleep(run_time + 2)
            while time.time() < start_time + float(run_time):
			    sleep(1)
            sys.exit(0)	
            
        print "Cmd channel buffer open succeeded !"
        sys.stdout.flush()

    def trigger(self):

        if self.type == TRAFFIC_FLOW_ONE_SHOT:
            sleep(self.offset)
            print "Started command at ", str(datetime.now())
            sys.stdout.flush()
            os.system(self.cmd)

        elif self.type == TRAFFIC_FLOW_EXPONENTIAL:
            pass
        elif self.type == TRAFFIC_FLOW_PERIODIC:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_params_file_path", dest="input_params_file_path")

    print "Started emulation driver ..."
    sys.stdout.flush()
    args = parser.parse_args()

    with open(args.input_params_file_path) as f:
        input_params = json.load(f)

    d = EmulationDriver(input_params)

    print "Waiting for START command ... buf = ", str(d.driver_id) + "main-cmd-channel-buffer"
    sys.stdout.flush()
    recv_msg = ''
    while "START" not in recv_msg:
        recv_msg = ''
        dummy_id, recv_msg = d.sharedBufferArray.read(str(d.driver_id) + "main-cmd-channel-buffer")


    print "Triggered emulation driver at ", str(datetime.now())
    sys.stdout.flush()
    d.trigger()

    print "Waiting for exit command ..."
    sys.stdout.flush()
    recv_msg = ''
    while "EXIT" not in recv_msg:
        recv_msg = ''
        sleep(1)
        dummy_id, recv_msg = d.sharedBufferArray.read(str(d.driver_id) + "main-cmd-channel-buffer")

    print "Shutting down driver ..."
    sys.stdout.flush()





if __name__ == "__main__":
    main()


