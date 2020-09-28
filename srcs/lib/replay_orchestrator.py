"""Replay Orchestrator

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>, Rakesh Kumar (gopchandani@gmail.com)
"""


import json
import threading
import logging
import queue
import time
import sys

import srcs.lib.logger as logger
import srcs.lib.defines as defines

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)


class ReplayOrchestrator(threading.Thread):
    """This thread orchestrates pcap replay by communicating with all replay drivers.

    """

    def __init__(self, net_power_obj, replay_plan_file):
        """Initialization of replay orchestrator

        :param net_power_obj: defined in srcs/core/netpower.py
        :param replay_plan_file: Absolute path to file containing the replay plan which specifies which replay driver
                                 is incharge of each pcap to be replayed
        """
        threading.Thread.__init__(self)

        self.thread_cmd_queue = queue.Queue()
        self.replay_plan_file = replay_plan_file
        self.shared_bufs = {}
        self.log = logger.Logger(
            "/tmp/replay_orchestrator_log.txt", "Replay Orchestrator")
        self.replay_plan = None
        self.start_time = None
        self.net_power_obj = net_power_obj

    def get_curr_cmd(self):
        curr_cmd = self.thread_cmd_queue.get(block=True)
        return curr_cmd

    def signal_pcap_replay_trigger(self, node_id, pcap_file_path):
        """Signals the pcap driver on "node_id" to run the pcap

        :param node_id: mininet host name
        :type node_id: str
        :param pcap_file_path: Absolute path to the pcap to be replayed
        :type pcap_file_path: str
        :return: None
        """
        ret = 0
        while ret <= 0:
            ret = self.net_power_obj.shared_buf_array.write(
                f"{node_id}-replay-main-cmd-channel-buffer", pcap_file_path, 0)
        self.log.info(f"Signalled start of replay phase to node: {node_id}")

    def send_command(self, cmd):
        self.thread_cmd_queue.put(cmd)

    def cancel_thread(self):
        self.thread_cmd_queue.put(defines.EXIT_CMD)

    def are_two_pcap_stages_conflicting(self, stage_1_nodes, stage_2_nodes):
        """Checks if two sets have nodes have any intersections

        :param stage_1_nodes: list of host names
        :param stage_2_nodes:  list of host names
        :return: True if the intersection is not NULL, else False
        """
        for node_id in stage_1_nodes:
            if node_id in stage_2_nodes:
                return True
        return False

    def is_pcap_stage_relevant(self, involved_hosts):
        """Checks if any node involved in the pcap doesn't even exist in the emulation

        :param involved_hosts: list of mininet host names
        :return: True if all nodes involved are valid, else False
        """
        relevant_hosts = [host.name for host in self.net_power_obj.network_configuration.mininet_obj.hosts]
        is_relevant = True
        for node_id in involved_hosts["involved_nodes"]:
            if node_id not in relevant_hosts:
                is_relevant = False
        return is_relevant

    def trigger_replay(self, node_ids, pcap_file):
        """Sends a trigger command to all nodes specified in node_ids

        :param node_ids: list of mininet host names
        :param pcap_file: pcap file to replay among those hosts
        :return: None
        """
        for node_id in node_ids:
            self.signal_pcap_replay_trigger(node_id, pcap_file)

    def run(self):
        """Listens for queued commands from the main melody process and sends triggers to the appropriate replay drivers

        """
        n_pending_requests = 0

        self.log.info("Replay Orchestrator Started ...")
        with open(self.replay_plan_file, "r") as f:
            self.replay_plan = json.load(f)

        cumulative_involved_replay_hosts = []
        nxt_replay_pcap_no = 0

        while True:
            try:
                cmd = self.thread_cmd_queue.get(block=False)
            except queue.Empty:
                cmd = None
            if cmd == defines.EXIT_CMD:
                self.net_power_obj.enable_TCP_RST()
                self.log.info(
                    "Emulation ended. Stopping replay orchestrator ...")
                sys.exit(defines.EXIT_SUCCESS)
            elif cmd == defines.TRIGGER_CMD:
                if nxt_replay_pcap_no >= len(self.replay_plan):
                    self.log.info("All pcaps replayed!. Ignoring TRIGGER ...")
                    time.sleep(1.0)
                    continue

                if not self.is_pcap_stage_relevant(self.replay_plan[nxt_replay_pcap_no]):
                    nxt_replay_pcap_no += 1
                    time.sleep(1.0)
                    continue

                if not self.are_two_pcap_stages_conflicting(
                            cumulative_involved_replay_hosts, self.replay_plan[nxt_replay_pcap_no]["involved_nodes"])\
                        and n_pending_requests == 0:
                    self.log.info(
                        "Signalled Start of Next Replay Pcap: " + \
                        self.replay_plan[nxt_replay_pcap_no]["pcap_file_path"])
                    self.net_power_obj.disable_TCP_RST()
                    self.trigger_replay(
                        self.replay_plan[nxt_replay_pcap_no]["involved_nodes"],
                        self.replay_plan[nxt_replay_pcap_no]["pcap_file_path"])
                    for node_id in self.replay_plan[nxt_replay_pcap_no][
                        "involved_nodes"]:
                        cumulative_involved_replay_hosts.append(node_id)
                    nxt_replay_pcap_no += 1
                else:
                    n_pending_requests += 1
            if (len(cumulative_involved_replay_hosts) == 0 and
                n_pending_requests > 0):
                self.log.info("End of Last Replay batch. Begin processing next "
                    "batch of pending requests ...")
                while n_pending_requests > 0:
                    if not self.are_two_pcap_stages_conflicting(
                            cumulative_involved_replay_hosts,
                            self.replay_plan[nxt_replay_pcap_no]["involved_nodes"]):
                        for node_id in self.replay_plan[nxt_replay_pcap_no][
                            "involved_nodes"]:
                            cumulative_involved_replay_hosts.append(node_id)
                        self.log.info(
                            "Signalled Start of Next Replay Pcap: " + \
                            self.replay_plan[nxt_replay_pcap_no]["pcap_file_path"])
                        self.trigger_replay(
                            self.replay_plan[nxt_replay_pcap_no]["involved_nodes"],
                            self.replay_plan[nxt_replay_pcap_no]["pcap_file_path"])
                        nxt_replay_pcap_no += 1
                        n_pending_requests -= 1
                    else:
                        break

            i = 0
            while i < len(cumulative_involved_replay_hosts):
                dummy_id, replay_status = \
                    self.net_power_obj.shared_buf_array.read(
                        f"{cumulative_involved_replay_hosts[i]}-replay-main-cmd-channel-buffer")
                if replay_status == defines.SIGNAL_FINISH_CMD:
                    cumulative_involved_replay_hosts.pop(i)
                else:
                    i += 1

            time.sleep(0.1)



