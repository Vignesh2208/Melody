import argparse
import json
import datetime
import logger
from src.utils.sleep_functions import sleep
from datetime import datetime
from shared_buffer import *
import time


class ReplayDriver(object):
    def __init__(self, input_params):

        self.driver_id = input_params["driver_id"]
        self.run_time = input_params["run_time"]
        self.node_id = input_params["node_id"]
        self.node_ip = input_params["node_ip"]
        self.rtt = {}
        self.log = logger.Logger("/tmp/" + self.node_id + "_replay_log.txt", "Replay Driver")
        # Load up the attack plan
        self.attack_plan_file_path = input_params["replay_plan_file_path"]
        with open(self.attack_plan_file_path, "r") as f:
            self.attack_plan = json.load(f)

        # Setup the channel with the orchestrator
        self.shared_buf_array = shared_buffer_array()
        self.init_shared_buffers(self.run_time)

        # Load the relevant pcap files and load them up in a dict keyed by the name of pcap file.
        self.loaded_pcaps = dict()
        self.load_pcaps()

        # Prepare sockets for replay later
        self.raw_rx_sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
        self.raw_tx_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

    def init_shared_buffers(self, run_time):

        result = self.shared_buf_array.open(bufName=str(self.driver_id) + "-main-cmd-channel-buffer", isProxy=False)
        if result == BUF_NOT_INITIALIZED or result == FAILURE:
            self.log.info("Cmd channel buffer open failed !")
            sys.stdout.flush()
            if run_time == 0:
                while True:
                    time.sleep(1.0)

            start_time = time.time()
            sleep(run_time + 2)
            while time.time() < start_time + float(run_time):
                time.sleep(1.0)
            sys.exit(0)

        self.log.info("Cmd channel buffer open succeeded !")
        sys.stdout.flush()

    def send_command_message(self, msg):
        ret = 0
        while ret <= 0:
            ret = self.shared_buf_array.write(self.driver_id + "-main-cmd-channel-buffer", msg, 0)
            time.sleep(0.001)

    def recv_command_message(self):
        dummy_id, msg = self.shared_buf_array.read_until(str(self.driver_id) + "-main-cmd-channel-buffer")
        return msg
    
    def load_pcap(self, pcap_file_path):
        recv_events = {}
        send_events = []

        replay_pcap_reader = dpkt.pcap.Reader(open(pcap_file_path, 'rb'))
        l2_type = replay_pcap_reader.datalink()

        curr_send_idx = 0
        curr_send_n_recv_events = 0
        prev_recv_time = 0.0
        prev_send_time = 0.0

        for ts, curr_pkt in replay_pcap_reader:

            if l2_type == dpkt.pcap.DLT_NULL:
                src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt, dpkt.pcap.DLT_NULL)
                raw_ip_pkt = get_raw_ip_pkt(curr_pkt, dpkt.pcap.DLT_NULL)
            elif l2_type == dpkt.pcap.DLT_LINUX_SLL:
                src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt, dpkt.pcap.DLT_LINUX_SLL)
                raw_ip_pkt = get_raw_ip_pkt(curr_pkt, dpkt.pcap.DLT_LINUX_SLL)
            else:
                src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt)
                raw_ip_pkt = get_raw_ip_pkt(curr_pkt)

            if src_ip == self.node_ip:
                ip_payload = binascii.hexlify(raw_ip_pkt.__str__())
                if prev_recv_time == 0.0 :
                    if prev_send_time == 0.0:
                        delta_t = self.rtt[pcap_file_path]
                    else:
                        delta_t = ts - prev_send_time + self.rtt[pcap_file_path]
                else :
                    delta_t = ts - prev_recv_time 
                    prev_recv_time = 0.0
                
                prev_send_time = ts
                send_events.append([ip_payload, dst_ip, curr_send_n_recv_events,delta_t])
                curr_send_n_recv_events = 0
                curr_send_idx = curr_send_idx + 1
            elif dst_ip == self.node_ip:
                curr_send_n_recv_events = curr_send_n_recv_events + 1
                ip_payload = binascii.hexlify(raw_ip_pkt.__str__())
                prev_recv_time = ts
                try:
                    recv_events[ip_payload].append(curr_send_idx)
                except:
                    recv_events[ip_payload] = []
                    recv_events[ip_payload].append(curr_send_idx)

        self.log.info("LOADED PCAP:" + pcap_file_path + "SEND EVENTS:" + str(len(send_events)) + "RECV EVENTS:" +
                      str(len(recv_events.keys())))
        sys.stdout.flush()
        return send_events, recv_events

    def load_pcaps(self):

        self.log.info("Loading pcaps involving: " + str(self.node_id))
        for stage_dict in self.attack_plan:

            if stage_dict["active"] == "false":
                continue

            if stage_dict["type"] == "replay":
            
                try:    
                    if self.node_id in stage_dict["rtt"].keys() :
                        self.rtt[stage_dict["pcap_file_path"]] = float(stage_dict["rtt"][self.node_id])
                except KeyError:
                    self.rtt[stage_dict["pcap_file_path"]] = 0.0
                if self.node_id in stage_dict["involved_nodes"]:
                    self.loaded_pcaps[stage_dict["pcap_file_path"]] = self.load_pcap(stage_dict["pcap_file_path"])

        self.send_command_message("LOADED")
        self.log.info("Loaded all pcaps and sent acknowledgement ... !")
        sys.stdout.flush()

    def trigger_replay(self, pcap_file_path):

        self.log.info("Replaying PCAP file " + pcap_file_path)
        sys.stdout.flush()
        
        send_events, recv_events = self.loaded_pcaps[pcap_file_path]

        curr_send_idx = 0
        curr_send_event = None
        payload = None
        dst_ip = None
        send_sleep_time = 0.0
        curr_rtt = self.rtt[pcap_file_path]

        while True:
            if curr_send_event is None:
                if curr_send_idx < len(send_events):
                    curr_send_event = send_events[curr_send_idx]
                    payload = binascii.unhexlify(str(curr_send_event[0]))
                    dst_ip = curr_send_event[1]
                    n_required_recv_events = curr_send_event[2]
                    send_sleep_time = float(curr_send_event[3]) - curr_rtt
                    self.log.info("Sending Replay Event: Dst = "
                                  + dst_ip + " N Req Recv events = " + str(n_required_recv_events))
                    sys.stdout.flush()

            if curr_send_event is None:
                break

            if n_required_recv_events == 0:
                if send_sleep_time > 0 :
                    time.sleep(send_sleep_time)
                self.raw_tx_sock.sendto(payload, (dst_ip, 0))
                curr_send_event = None
                curr_send_idx = curr_send_idx + 1

            else:
                try:
                    raw_pkt = self.raw_rx_sock.recv(MAXPKTSIZE)
                except socket.error as e:
                    self.log.error("Socket Error: " + str(e))
                    continue

                assert len(raw_pkt) != 0
                raw_ip_pkt = get_raw_ip_pkt(raw_pkt)
                ip_payload = binascii.hexlify(raw_ip_pkt.__str__( ))

                try:
                    if len(recv_events[ip_payload]) > 0:
                        first_send_window = recv_events[ip_payload][0]

                        assert (first_send_window >= curr_send_idx)
                        if first_send_window == curr_send_idx :
                            n_required_recv_events = n_required_recv_events - 1
                        else:
                            recv_events[ip_payload].pop(0)
                            send_events[first_send_window] = [send_events[first_send_window][0],
                                                              send_events[first_send_window][1],
                                                              send_events[first_send_window][2] - 1]
                    else:
                        pass

                except KeyError as e:
                    pass


        self.log.info("Signalling End of Replay Stage ...")
        sys.stdout.flush()
        self.send_command_message("DONE")
        
    def wait_for_commands(self):
        recv_msg = ''
        
        while "EXIT" not in recv_msg:
            recv_msg = self.recv_command_message()

            if recv_msg == '':
                continue
            
            # If the received msg is a pcap file path, then replay the pcap
            if recv_msg in self.loaded_pcaps:
                self.trigger_replay(recv_msg)
            else:
                self.log.error("Unknown PCAP file path:" + recv_msg)
                break
        self.raw_rx_sock.close()
        self.raw_tx_sock.close()
        self.log.info("Replay driver with id:" + self.driver_id + " exiting...")
        sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_params_file_path", dest="input_params_file_path")
    sys.stdout.flush()
    args = parser.parse_args()

    with open(args.input_params_file_path) as f:
        input_params = json.load(f)

    d = ReplayDriver(input_params)
    d.log.info("Started Replay driver ...")
    d.wait_for_commands()


if __name__ == "__main__":
    main()


