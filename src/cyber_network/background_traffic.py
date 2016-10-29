
class TrafficSpec(object):
    def __init__(self, type, rate, src_node_id, dst_node_id):
        pass


class BackgroundTraffic(object):
    def __init__(self, mininet_obj, traffic_specs):
        self.mininet_obj = mininet_obj

    def generate_ssh_flows(self, rate, src_node_id, dst_node_id):

        src_mn_node = self.mininet_obj.get(src_node_id)
        dst_mn_node = self.mininet_obj.get(dst_node_id)

        # Spawn an SSHd on the server

        dst_mn_node.cmd('/usr/sbin/sshd -D&')
        src_mn_node.cmd('')
