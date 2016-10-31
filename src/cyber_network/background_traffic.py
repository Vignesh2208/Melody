import time
from mininet.cli import CLI


class TrafficFlow(object):

    def __init__(self, type, offset, rate, protocol, src_node_id, dst_node_id):
        '''
        'type', 'offset' and rate' do the following:
            - Periodic: That repeats itself after af fixed period determined by 1/rate seconds,
                        offset determines when it commences for the first time.
            - Poisson: That repeats itself with poisson arrivals with the specified rate,
                        offset determines when it commences for the first time.
            - One shot: Does not repeat, so the rate does not matter. However, offset determines when it commences

        'protocol' determines the nature of traffic that is sent/received, currently supported protocols are:
            - ssh: Start an sshd at dst_node, connect to it from src and send a small file via scp

        'src_node_id' and 'dst_node_id' define the endpoints of the flow
        '''

        self.type = type
        self.offset = offset
        self.rate = rate
        self.protocol = protocol
        self.src_node_id = src_node_id
        self.dst_node_id = dst_node_id

        self.src_process_pid = None
        self.dst_process_pid = None

        self.src_mn_node = None
        self.dst_mn_node = None

    def start(self, mininet_obj, root_user_name, root_password, base_dir):

        self.src_mn_node = mininet_obj.get(self.src_node_id)
        self.dst_mn_node = mininet_obj.get(self.dst_node_id)

        # First wait for offset seconds
        time.sleep(self.offset)

        # Start the server
        result = self.dst_mn_node.cmd('/usr/sbin/sshd -D&')
        print result

        # Wait a second before starting the client
        time.sleep(1)

        result = self.src_mn_node.cmd(base_dir + '/src/cyber_network/ssh_session_connect_disconnect.expect ' +
                                      root_user_name + ' ' +
                                      root_password + ' ' +
                                      self.dst_mn_node.IP())

        print result

    def stop(self):
        pass


class BackgroundTraffic(object):
    def __init__(self, mininet_obj, traffic_flows, root_user_name, root_password, base_dir):
        self.mininet_obj = mininet_obj
        self.traffic_flows = traffic_flows
        self.root_user_name = root_user_name
        self.root_password = root_password
        self.base_dir = base_dir

    def start(self):
        for tf in self.traffic_flows:
            tf.start(self.mininet_obj, self.root_user_name, self.root_password, self.base_dir)

    def stop(self):
        for tf in self.traffic_flows:
            tf.stop()
