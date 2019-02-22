import json
import getopt
import threading
from src.utils.sleep_functions import *
from kronos_helper_functions import *
from shared_buffer import *
import logger
import Queue
from defines import *


class ReplayOrchestrator(threading.Thread):

    def __init__(self, net_power_obj, replay_plan_file, run_time):

        threading.Thread.__init__(self)

        self.thread_cmd_queue = Queue.Queue()
        self.replay_plan_file = replay_plan_file
        self.run_time = run_time
        self.shared_bufs = {}
        self.log = logger.Logger("/tmp/replay_orchestrator_log.txt", "Replay Orchestrator")
        self.replay_plan = None
        self.start_time = None
        self.net_power_obj = net_power_obj

    def get_curr_cmd(self):
        curr_cmd = self.thread_cmd_queue.get(block=True)
        return curr_cmd



    def signal_pcap_replay_trigger(self, node_id, pcap_file_path):
        ret = 0
        while ret <= 0:
            ret = self.net_power_obj.shared_buf_array.write(str(node_id)\
                                                            + "-replay-main-cmd-channel-buffer", pcap_file_path, 0)
        self.log.info("Signalled start of replay phase to node:" + str(node_id))


    def send_command(self, cmd):
        self.thread_cmd_queue.put(cmd)

    def cancel_thread(self):
        self.thread_cmd_queue.put("EXIT")

    def are_two_pcap_stages_conflicting(self, stage_1_nodes, stage_2_nodes):
        for node_id in stage_1_nodes:
            if node_id in stage_2_nodes:
                return True
        return False

    def is_pcap_stage_relevant(self, involved_hosts):

        relevant_hosts = [host.name for host in self.net_power_obj.network_configuration.mininet_obj.hosts]
        is_relevant = True
        for node_id in involved_hosts["involved_nodes"]:
            if node_id not in relevant_hosts:
                is_relevant = False
        return is_relevant


    def trigger_replay(self, node_ids, pcap_file):
        for node_id in node_ids:
            self.signal_pcap_replay_trigger(node_id, pcap_file)

    def run(self):

        n_pending_requests = 0

        self.log.info("Replay Orchestrator Started ...")
        with open(self.replay_plan_file, "r") as f:
            self.replay_plan = json.load(f)

        cumulative_involved_replay_hosts = []
        nxt_replay_pcap_no = 0

        while True:
            try:
                cmd = self.thread_cmd_queue.get(block=False)
            except Queue.Empty:
                cmd = None
            if cmd == "EXIT":
                self.net_power_obj.enable_TCP_RST()
                self.log.info("Emulation ended. Stopping replay orchestrator ...")
                sys.exit(0)
            elif cmd == "TRIGGER":
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
                    self.log.info("Signalled Start of Next Replay Pcap: " + self.replay_plan[nxt_replay_pcap_no]["pcap_file_path"])
                    self.net_power_obj.disable_TCP_RST()
                    self.trigger_replay(self.replay_plan[nxt_replay_pcap_no]["involved_nodes"],
                                        self.replay_plan[nxt_replay_pcap_no]["pcap_file_path"])
                    for node_id in self.replay_plan[nxt_replay_pcap_no]["involved_nodes"]:
                        cumulative_involved_replay_hosts.append(node_id)
                    nxt_replay_pcap_no += 1
                else:
                    n_pending_requests += 1
            if len(cumulative_involved_replay_hosts) == 0 and n_pending_requests > 0:
                self.log.info("End of Last Replay batch. Begin processing next batch of pending requests ...")
                while n_pending_requests > 0:
                    if not self.are_two_pcap_stages_conflicting(
                            cumulative_involved_replay_hosts, self.replay_plan[nxt_replay_pcap_no]["involved_nodes"]):
                        for node_id in self.replay_plan[nxt_replay_pcap_no]["involved_nodes"]:
                            cumulative_involved_replay_hosts.append(node_id)
                        self.log.info(
                            "Signalled Start of Next Replay Pcap: " + self.replay_plan[nxt_replay_pcap_no][
                                "pcap_file_path"])
                        self.trigger_replay(self.replay_plan[nxt_replay_pcap_no]["involved_nodes"],
                                            self.replay_plan[nxt_replay_pcap_no]["pcap_file_path"])
                        nxt_replay_pcap_no += 1
                        n_pending_requests -= 1
                    else:
                        break

            i = 0
            while i < len(cumulative_involved_replay_hosts):
                dummy_id, replay_status = self.net_power_obj.shared_buf_array.read(
                    cumulative_involved_replay_hosts[i] + "-replay-main-cmd-channel-buffer")
                if replay_status == "DONE":
                    cumulative_involved_replay_hosts.pop(i)
                else:
                    i += 1


            #if n_pending_requests == 0:
            #    self.net_power_obj.enable_TCP_RST()

            sleep(0.1)



