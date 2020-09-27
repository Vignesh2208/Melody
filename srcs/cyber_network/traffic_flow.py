"""Holders for managing Emulated and Replay traffic flows

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>
"""
import uuid
import json
import os
import sys

import srcs.lib.defines as defines



class EmulatedTrafficFlow(object):

    def __init__(self, offset, run_time, src_mn_node, dst_mn_node,
                 server_process_start_cmd,
                 client_process_start_cmd,
                 long_running=False):
        """Initialization of Emulated Traffic Flow

        :param offset: time to wait in secs before starting the emulation cmd at client.
        :type offset: int
        :param run_time: the total time for which the traffic is generated.
        :type run_time: int
        :param client_process_start_cmd: command to start at client
        :type client_process_start_cmd: str
        :param server_process_start_cmd: command to start at server
        :type server_process_start_cmd: str
        :param src_mn_node: mininet node object for client
        :type src_mn_node: mininet_host obj
        :param dst_mn_node: mininet node object for server
        :type dst_mn_node: mininet host obj
        """

        self.type = defines.TRAFFIC_FLOW_ONE_SHOT
        self.offset = offset
        self.run_time = run_time

        self.src_mn_node = src_mn_node
        self.dst_mn_node = dst_mn_node
        self.server_process_start_cmd = server_process_start_cmd
      
        self.long_running = long_running
        self.client_process_start_cmd = client_process_start_cmd

    def get_emulated_driver_attributes(self, for_client=True):

        if for_client :
            driver_attributes = {
                                "type": self.type,
                                "cmd": self.client_process_start_cmd,
                                "offset": self.offset,
                                "run_time": self.run_time,
                                "node_id": self.src_mn_node.name,
                                "driver_id":  self.src_mn_node.name + "-emulation-" + str(uuid.uuid1())}
        elif self.server_process_start_cmd != "":
            driver_attributes = {
                "type": self.type,
                "cmd": self.server_process_start_cmd,
                "offset": 0,
                "run_time": self.run_time,
                "node_id": self.dst_mn_node.name,
                "driver_id": self.dst_mn_node.name + "-emulation-" + str(uuid.uuid1())}
        else:
            return None

        return driver_attributes

class ReplayTrafficFlow(object):
    """Holds replay traffic flow information for a specific pcap
    """

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
    """Holds replay traffic information for all pcaps
    """
    def __init__(self):
        self.replay_flows = []

    def add_replay_flow(self, replay_flow_obj):
        if not os.path.isfile(replay_flow_obj.pcap_file_path):
            sys.stdout.write("Melody >> WARNING: Ignoring replay pcap: %s because pcap file path is incorrect!\n"%replay_flow_obj.pcap_file_path)
            
        else:
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
            attributes = replay_flow_obj.get_attributes()
            if os.path.isfile(attributes["pcap_file_path"]):
                replay_plan.append(replay_flow_obj.get_attributes())
            else:
                sys.stdout.write("Ignoring replay pcap: %s because pcap file path is incorrect !\n"%attributes["pcap_file_path"])
                
        with open("/tmp/replay_plan.json", "w") as outfile:
            json.dump(replay_plan, outfile)

