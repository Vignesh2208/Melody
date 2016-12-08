import time
import threading
import random

from timeit import default_timer as timer

TRAFFIC_FLOW_PERIODIC = 'Periodic'
TRAFFIC_FLOW_EXPONENTIAL = 'Exponential'
TRAFFIC_FLOW_ONE_SHOT = 'One Shot'


class TrafficFlow(threading.Thread):

    def __init__(self, type, offset, inter_flow_period, run_time, src_mn_node, dst_mn_node,
                 root_user_name, root_password,
                 server_process_start_cmd,
                 #server_process_stop_cmd,
                 client_expect_file):
        '''
        'type', 'offset' and rate' do the following:
            - Periodic: That repeats itself after af fixed period determined by inter_flow_period seconds,
                        offset determines when it commences for the first time.
            - Exponential: That repeats itself with exponential durations with the specified inter_flow_period as mean,
                        offset determines when it commences for the first time.
            - One Shot: Does not repeat, so the rate does not matter. However, offset determines when it commences

        'run_time' determines the total time for which the traffic is generated.


        'src_node_id' and 'dst_node_id' define the endpoints of the flow
        '''

        super(TrafficFlow, self).__init__()

        self.type = type
        self.offset = offset
        self.inter_flow_period = inter_flow_period
        self.run_time = run_time

        self.src_mn_node = src_mn_node
        self.dst_mn_node = dst_mn_node

        self.root_user_name = root_user_name
        self.root_password = root_password

        self.server_process_start_cmd = server_process_start_cmd
        self.server_pid = None
        self.client_expect_file = client_expect_file

        self.start_time = None
        self.elasped_time = None

    def client_loop(self):

        print "Starting client loop..."

        while True:

            self.elasped_time = timer()

            if self.elasped_time - self.start_time > self.run_time:
                break

            cmd = self.client_expect_file + ' ' +\
                  self.root_user_name + ' ' +\
                  self.root_password + ' ' + self.dst_mn_node.IP()

            result = self.src_mn_node.pexec(cmd)

            if self.type == TRAFFIC_FLOW_PERIODIC:
                sleep_for = self.inter_flow_period
                time.sleep(sleep_for)
            elif self.type == TRAFFIC_FLOW_EXPONENTIAL:
                sleep_for = random.expovariate(1.0/self.inter_flow_period)
                time.sleep(sleep_for)
            elif self.type == TRAFFIC_FLOW_ONE_SHOT:
                break
            else:
                print "Invalid traffic flow type"
                raise Exception

    def start_server(self):

        if self.server_process_start_cmd:

            # Start the server
            result = self.dst_mn_node.cmd(self.server_process_start_cmd)
            print result

            for line in result.split("\r"):
                print line
                if line[0] == "[" and line[2] == "]":
                    self.server_pid = int(line.split()[1])
                    print self.server_pid

    def stop_server(self):

        # Stop the server
        result = self.dst_mn_node.cmd("sudo kill " + str(self.server_pid))

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
