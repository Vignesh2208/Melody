
import uuid
import json

TRAFFIC_FLOW_PERIODIC = 'Periodic'
TRAFFIC_FLOW_EXPONENTIAL = 'Exponential'
TRAFFIC_FLOW_ONE_SHOT = 'One Shot'

class EmulatedTrafficFlow(object):

    def __init__(self, type, offset, inter_flow_period, run_time, src_mn_node, dst_mn_node,
                 root_user_name, root_password,
                 server_process_start_cmd,
                 client_expect_file,
                 long_running=False):
        """
            'type', 'offset' and rate' do the following:
            - Periodic: That repeats itself after af fixed period determined by inter_flow_period seconds,
                        offset determines when it commences for the first time.
            - Exponential: That repeats itself with exponential durations with the specified inter_flow_period as mean,
                        offset determines when it commences for the first time.
            - One Shot: Does not repeat, so the rate does not matter. However, offset determines when it commences

        'run_time' determines the total time for which the traffic is generated.

        'offset' determines how long after the thread started, the traffic is generated.

        'src_mn_node' and 'dst_mn_node' define the endpoints of the flow
        """

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

    def get_emulated_driver_attributes(self, for_client=True):

        if for_client :
            driver_attributes = {
                                "type": self.type,
                                "cmd": self.client_expect_file,
                                "offset": self.offset,
                                "inter_flow_period": self.inter_flow_period,
                                "run_time": self.run_time,
                                "long_running": self.long_running,
                                "root_user_name": self.root_user_name,
                                "root_password": self.root_password,
                                "node_id": self.src_mn_node.name,
                                "driver_id":  self.src_mn_node.name + "-emulation-" + str(uuid.uuid1())}
        elif self.server_process_start_cmd != "":
            driver_attributes = {
                "type": self.type,
                "cmd": self.server_process_start_cmd,
                "offset": 0,
                "inter_flow_period": self.inter_flow_period,
                "run_time": self.run_time,
                "long_running": self.long_running,
                "root_user_name": self.root_user_name,
                "root_password": self.root_password,
                "node_id": self.dst_mn_node.name,
                "driver_id": self.dst_mn_node.name + "-emulation-" + str(uuid.uuid1())}
        else:
            return None

        return driver_attributes

class ReplayTrafficFlow(object):

    def __init__(self, involved_nodes, pcap_file_path):
        self.involved_nodes = involved_nodes
        self.pcap_file_path = pcap_file_path

    def get_attributes(self):
        attributes = {
            "type": "replay",
            "involved_nodes": self.involved_nodes,
            "pcap_file_path": self.pcap_file_path,
            "active": True,
        }
        return attributes

class ReplayFlowsContainer(object):
    def __init__(self):
        self.replay_flows = []

    def add_replay_flow(self, replay_flow_obj):
        self.replay_flows.append(replay_flow_obj)

    def get_all_involved_nodes(self):
        involved_nodes = []
        for flow in self.replay_flows:
            for node in flow.involved_nodes:
                if node not in involved_nodes:
                    involved_nodes.append(node)
        return involved_nodes

    def create_replay_plan(self):
        replay_plan = []
        for replay_flow_obj in self.replay_flows:
            replay_plan.append(replay_flow_obj.get_attributes())
        with open("/tmp/replay_plan.json", "w") as outfile:
            json.dump(replay_plan, outfile)

