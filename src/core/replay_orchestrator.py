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

    def run(self):

        n_pending_requests = 0
        relevant_hosts = [host.name for host in self.net_power_obj.network_configuration.mininet_obj.hosts]
        self.log.info("Replay Orchestrator Started ...")
        with open(self.replay_plan_file, "r") as f:
            self.replay_plan = json.load(f)

        for stage_dict in self.replay_plan:

            if stage_dict["active"] == "false":
                continue

            if stage_dict["type"] == "replay":
                if n_pending_requests == 0:
                    self.log.info("Waiting for nxt command from Melody main thread ...")
                    sys.stdout.flush()
                    if self.get_curr_cmd() == "EXIT":
                        break
                else:
                    n_pending_requests -= 1

                self.log.info("Signalled Start of Next Replay Phase: Pcap = " + stage_dict["pcap_file_path"])

                is_relevant = True
                for node_id in stage_dict["involved_nodes"]:
                    if node_id not in relevant_hosts:
                        is_relevant = False

                if is_relevant:
                    self.net_power_obj.disable_TCP_RST()
                    for node_id in stage_dict["involved_nodes"]:
                        self.signal_pcap_replay_trigger(node_id, stage_dict["pcap_file_path"])
                        sys.stdout.flush()
                    self.log.info("Waiting for Replay Phase to complete ...")
                    for node_id in stage_dict["involved_nodes"]:
                        while True:
                            dummy_id, replay_status = self.net_power_obj.shared_buf_array.read(node_id
                                                                                 + "-replay-main-cmd-channel-buffer")
                            try:
                                cmd = self.thread_cmd_queue.get(block=False)
                            except Queue.Empty:
                                cmd = None
                            if cmd == "EXIT":
                                self.log.info("Emulation ended. Stopping replay orchestrator ...")
                                sys.exit(0)
                            elif cmd == "TRIGGER":
                                n_pending_requests += 1
                            if replay_status == "DONE":
                                break
                            sleep(0.1)
                    self.net_power_obj.enable_TCP_RST()
                self.log.info("Signalled End of Last Replay Phase ...")

        self.log.info("Finished executing replay plan. Stopping replay orchestrator...")
        sys.exit(0)

