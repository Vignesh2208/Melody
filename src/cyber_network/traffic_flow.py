import time
import threading
import random

from timeit import default_timer as timer

TRAFFIC_FLOW_PERIODIC = 'Periodic'
TRAFFIC_FLOW_EXPONENTIAL = 'Exponential'
TRAFFIC_FLOW_ONE_SHOT = 'One Shot'


class EmulatedTrafficFlow(threading.Thread):

    def __init__(self, type, offset, inter_flow_period, run_time, src_mn_node, dst_mn_node,
                 root_user_name, root_password,
                 server_process_start_cmd,
                 client_expect_file,
                 long_running=False):
        '''
        'type', 'offset' and rate' do the following:
            - Periodic: That repeats itself after af fixed period determined by inter_flow_period seconds,
                        offset determines when it commences for the first time.
            - Exponential: That repeats itself with exponential durations with the specified inter_flow_period as mean,
                        offset determines when it commences for the first time.
            - One Shot: Does not repeat, so the rate does not matter. However, offset determines when it commences

        'run_time' determines the total time for which the traffic is generated.

        'offset' determines how long after the thread started, the traffic is generated.

        'src_mn_node' and 'dst_mn_node' define the endpoints of the flow
        '''

        super(EmulatedTrafficFlow, self).__init__()

        self.type = type
        self.offset = offset
        self.inter_flow_period = inter_flow_period
        self.run_time = run_time

        self.src_mn_node = src_mn_node
        self.dst_mn_node = dst_mn_node

        self.root_user_name = root_user_name
        self.root_password = root_password

        self.server_process_start_cmd = server_process_start_cmd
      
        self.long_running = long_running
        self.client_expect_file = client_expect_file

        self.start_time = None
        self.elasped_time = None

        self.server_popen = None
        self.client_popen = None
	self.looped = False 

    def client_loop(self):

        #print "Starting client loop..."

        while True:

            self.elasped_time = timer()

            if self.elasped_time - self.start_time > self.run_time:
                break

            cmd = "sudo " + self.client_expect_file + ' ' +\
                  self.root_user_name + ' ' +\
                  self.root_password + ' ' + self.dst_mn_node.IP() 
          
            #print "Client command:", cmd
            if self.long_running and self.looped:
		pass
	    else:
	        self.client_popen = self.src_mn_node.popen(cmd)

            #print "Client command:", cmd

            if self.type == TRAFFIC_FLOW_PERIODIC:
                sleep_for = self.inter_flow_period
                time.sleep(sleep_for)
            elif self.type == TRAFFIC_FLOW_EXPONENTIAL:
                sleep_for = random.expovariate(1.0/self.inter_flow_period)
                time.sleep(sleep_for)
            elif self.type == TRAFFIC_FLOW_ONE_SHOT and not self.long_running:
		time.sleep(1)               
		break
	    elif self.long_running:
		#time.sleep(self.elasped_time-self.run_time)
		self.looped = True
            else:
                print "Invalid traffic flow type"
                raise Exception

            #if not self.long_running:
            #    self.client_popen.terminate()

        # For long running flows, clean up after everything else.
        #if self.long_running:
       	self.client_popen.terminate()
	self.looped = False
        
    def start_server(self):

        if self.server_process_start_cmd:

            # Start the server
            self.server_popen = self.dst_mn_node.popen(self.server_process_start_cmd)

    def stop_server(self):

        # Stop the server
        if self.server_process_start_cmd:
            #print "Stopping server with cmd: ", self.server_process_start_cmd
            #pass
            self.server_popen.terminate()

    def run(self):

        print "Starting thread..."

        self.start_time = timer()

        # First wait for offset seconds
        time.sleep(self.offset)

        # Start the server process
        self.start_server()

        # Wait a second before starting the client loop
        time.sleep(1)

        self.client_loop()

        # Kill the server process
        self.stop_server()
        

