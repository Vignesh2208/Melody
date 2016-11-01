import time
import threading

from timeit import default_timer as timer


class TrafficFlow(threading.Thread):

    def __init__(self, type, offset, rate, run_time, protocol, src_node_id, dst_node_id, root_user_name, root_password, base_dir, mininet_obj):
        '''
        'type', 'offset' and rate' do the following:
            - Periodic: That repeats itself after af fixed period determined by 1/rate seconds,
                        offset determines when it commences for the first time.
            - Poisson: That repeats itself with poisson arrivals with the specified rate,
                        offset determines when it commences for the first time.
            - One shot: Does not repeat, so the rate does not matter. However, offset determines when it commences

        'run_time' determines the total time for which the traffic is generated.

        'protocol' determines the nature of traffic that is sent/received, currently supported protocols are:
            - ssh: Start an sshd at dst_node, connect to it from src and send a small file via scp

        'src_node_id' and 'dst_node_id' define the endpoints of the flow
        '''

        self.type = type
        self.offset = offset
        self.rate = rate
        self.run_time = run_time
        self.protocol = protocol
        self.src_node_id = src_node_id
        self.dst_node_id = dst_node_id
        self.mininet_obj = mininet_obj

        self.src_mn_node = self.mininet_obj.get(self.src_node_id)
        self.dst_mn_node = self.mininet_obj.get(self.dst_node_id)

        self.root_user_name = root_user_name
        self.root_password = root_password
        self.base_dir = base_dir

        self.src_process_pid = None
        self.dst_process_pid = None

        self.start_time = None
        self.elasped_time = None

    def client_loop(self):

        while True:

            self.elasped_time = timer()

            time.sleep(1)

            if self.elasped_time - self.start_time > self.run_time:
                break

            result = self.src_mn_node.cmd(self.base_dir + '/src/cyber_network/ssh_session_connect_disconnect.expect ' +
                                          self.root_user_name + ' ' +
                                          self.root_password + ' ' +
                                          self.dst_mn_node.IP())

            print result

    def setup_server(self):

        # Start the server
        result = self.dst_mn_node.cmd('/usr/sbin/sshd -D&')
        print result

    def run(self):

        self.start_time = timer()

        # First wait for offset seconds
        time.sleep(self.offset)

        # Start the server process
        self.setup_server()

        # Wait a second before starting the client
        time.sleep(1)

        self.client_loop()
