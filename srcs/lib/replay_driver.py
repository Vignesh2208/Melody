"""Replay driver

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>, Rakesh Kumar (gopchandani@gmail.com)
"""


import argparse
import json
import time
import binascii
import socket
import sys
import dpkt

from dpkt.ethernet import Ethernet
from dpkt.ip import IP
import srcs.lib.logger as logger
import srcs.lib.defines as defines

from srcs.lib.shared_buffer import *


class ReplayDriver(object):
    """Controls replaying pcaps

    """
    def __init__(self, input_params):
        """Initializes the replay driver.

        :param input_params: a dictionary containing parameters and pcaps to load
        :type input_params: dict
        """

        self.driver_id = input_params["driver_id"]
        self.run_time = input_params["run_time"]
        self.node_id = input_params["node_id"]
        self.node_ip = input_params["node_ip"]
        self.rtt = {}
        self.log = logger.Logger(
            f"/tmp/{self.node_id}-replay_log.txt", "Replay Driver")
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
        self.raw_rx_sock = socket.socket(
            socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
        self.raw_tx_sock = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

    def init_shared_buffers(self, run_time):
        """Initializes shared buffers to allow communication with the main melody process

        :param run_time: run time in seconds. If the buffer cannot be opened, the driver would simply run for
                         the specified amount and exit gracefully.
        :type run_time: int
        :return: None
        """
        result = self.shared_buf_array.open(
            bufName=f"{self.driver_id}-main-cmd-channel-buffer", isProxy=False)
        if result == defines.BUF_NOT_INITIALIZED or result == defines.FAILURE:
            self.log.info("Cmd channel buffer open failed !")
            
            if run_time == 0:
                while True:
                    time.sleep(1.0)

            time.sleep(run_time)
            sys.exit(0)

        self.log.info("Cmd channel buffer open succeeded !")
        

    def send_command_message(self, msg):
        """Sends a message over the shared buffer

        :param msg: Message to send
        :type msg: str
        :return: None
        """
        ret = 0
        while ret <= 0:
            ret = self.shared_buf_array.write(
                f"{self.driver_id}-main-cmd-channel-buffer", msg, 0)
            time.sleep(0.001)

    def recv_command_message(self):
        """Gets command from the shared buffer

        :return: string or None
        """
        dummy_id, msg = self.shared_buf_array.read_until(
            f"{self.driver_id}-main-cmd-channel-buffer")
        return msg
    
    def load_pcap(self, pcap_file_path):
        """Loads a pcap specified by the pcap_file_path

        :param pcap_file_path: Absolute path to the pcap file
        :type pcap_file_path: str
        :return: None
        """
        recv_events = {}
        send_events = []

        replay_pcap_reader = dpkt.pcap.Reader(open(pcap_file_path, 'rb'))
        l2_type = replay_pcap_reader.datalink()
        self.log.info(f"L2-Type: {l2_type}")

        curr_send_idx = 0
        curr_send_n_recv_events = 0
        prev_recv_time = 0.0
        prev_send_time = 0.0

        for ts, curr_pkt in replay_pcap_reader:

            if l2_type == dpkt.pcap.DLT_NULL:
                src_ip, dst_ip = defines.get_pkt_src_dst_IP(
                    curr_pkt, dpkt.pcap.DLT_NULL)
                raw_ip_pkt = defines.get_raw_ip_pkt(
                    curr_pkt, dpkt.pcap.DLT_NULL)
                
            elif l2_type == dpkt.pcap.DLT_LINUX_SLL:
                src_ip, dst_ip = defines.get_pkt_src_dst_IP(
                    curr_pkt, dpkt.pcap.DLT_LINUX_SLL)
                raw_ip_pkt = defines.get_raw_ip_pkt(
                    curr_pkt, dpkt.pcap.DLT_LINUX_SLL)
                
            else:
                src_ip, dst_ip = defines.get_pkt_src_dst_IP(curr_pkt)
                raw_ip_pkt = defines.get_raw_ip_pkt(curr_pkt)
            

            if src_ip == self.node_ip:
                #ip_payload = binascii.hexlify(raw_ip_pkt.__str__().encode())
                ip_payload = raw_ip_pkt.__bytes__()
                if prev_recv_time == 0.0 :
                    if prev_send_time == 0.0:
                        delta_t = self.rtt[pcap_file_path]
                    else:
                        delta_t = ts - prev_send_time + self.rtt[pcap_file_path]
                else :
                    delta_t = ts - prev_recv_time 
                    prev_recv_time = 0.0
                
                prev_send_time = ts
                send_events.append(
                    [ip_payload, dst_ip, curr_send_n_recv_events,delta_t,
                    binascii.hexlify(raw_ip_pkt.__str__().encode())])
                curr_send_n_recv_events = 0
                curr_send_idx = curr_send_idx + 1
            elif dst_ip == self.node_ip:
                curr_send_n_recv_events = curr_send_n_recv_events + 1
                ip_payload = binascii.hexlify(raw_ip_pkt.__str__().encode())
                prev_recv_time = ts
                try:
                    recv_events[ip_payload].append(curr_send_idx)
                except:
                    recv_events[ip_payload] = []
                    recv_events[ip_payload].append(curr_send_idx)

        self.log.info(
            f"LOADED PCAP: {pcap_file_path} SEND EVENTS: "
            f"{len(send_events)} RECV EVENTS: {len(recv_events.keys())}")
        
        return send_events, recv_events

    def load_pcaps(self):
        """Load all pcaps which involve this mininet host

        :return: None
        """
        self.log.info(
            f"Loading pcaps involving: {self.node_id}")
        for stage_dict in self.attack_plan:

            if stage_dict["active"] == "false":
                continue

            if stage_dict["type"] == "replay":
                try:    
                    if self.node_id in stage_dict["rtt"].keys() :
                        self.rtt[stage_dict["pcap_file_path"]] = \
                            float(stage_dict["rtt"][self.node_id])
                except KeyError:
                    self.rtt[stage_dict["pcap_file_path"]] = 0.0
                if self.node_id in stage_dict["involved_nodes"]:
                    self.loaded_pcaps[stage_dict["pcap_file_path"]] = \
                        self.load_pcap(stage_dict["pcap_file_path"])

        self.send_command_message(defines.LOADED_CMD)
        self.log.info("Loaded all pcaps and sent acknowledgement ... !")
        

    def trigger_replay(self, pcap_file_path):
        """Triggers replay of the pcap_file specified by pcap_file_path

        .. note:: The pcap file must have already been loaded before calling this.

        :param pcap_file_path: Absolute path to pcap file
        :type pcap_file_path: str
        :return: None
        """
        self.log.info(f"Replaying PCAP file {pcap_file_path}")
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
                    payload = curr_send_event[0]
                    dst_ip = curr_send_event[1]
                    n_required_recv_events = curr_send_event[2]
                    send_sleep_time = float(curr_send_event[3]) - curr_rtt
                    self.log.info(
                        f"Sending replay event: Dst-IP = "
                        f"{dst_ip} Num required recv events = {n_required_recv_events} ")
                    

            if curr_send_event is None:
                break

            if n_required_recv_events == 0:
                if send_sleep_time > 0 :
                    time.sleep(send_sleep_time)
                ret = self.raw_tx_sock.sendto(payload, (dst_ip, 0))
                curr_send_event = None
                curr_send_idx = curr_send_idx + 1

            else:
                try:
                    raw_pkt = self.raw_rx_sock.recv(defines.MAXPKTSIZE)
                except socket.error as e:
                    self.log.error(f"Socket Error: {str(e)}")
                    continue

                assert len(raw_pkt) != 0
                
                try:
                    raw_ip_pkt = Ethernet(raw_pkt).data
                    ip_payload = binascii.hexlify(raw_ip_pkt.__str__().encode())
                except Exception as e:
                    self.log.error (f"ERROR PARSING IP PACKET {str(e)}")
                    continue

                

                try:
                    if len(recv_events[ip_payload]) > 0:
                        first_send_window = recv_events[ip_payload][0]

                        assert (first_send_window >= curr_send_idx)
                        if first_send_window == curr_send_idx :
                            n_required_recv_events = n_required_recv_events - 1
                        else:
                            recv_events[ip_payload].pop(0)
                            send_events[first_send_window] = [
                                send_events[first_send_window][0],
                                send_events[first_send_window][1],
                                send_events[first_send_window][2] - 1]
                    else:
                        pass

                except KeyError as e:
                    pass

        self.log.info("Signalling End of Replay Stage ...")
        self.send_command_message(defines.SIGNAL_FINISH_CMD)
        
    def wait_for_commands(self):
        """Wait for a trigger replay command from the main melody process

        :return: None
        """
        recv_msg = ''
        
        while defines.EXIT_CMD not in recv_msg:
            recv_msg = self.recv_command_message()

            if recv_msg == '':
                continue
            
            # If the received msg is a pcap file path, then replay the pcap
            if recv_msg in self.loaded_pcaps:
                self.trigger_replay(recv_msg)
            else:
                self.log.error(
                    f"Unknown PCAP file path: {recv_msg}")
                break
        self.raw_rx_sock.close()
        self.raw_tx_sock.close()
        self.log.info(
            f"Replay driver with id: {self.driver_id} exiting...")
        


def main():
    """Creates a replay driver and calls wait_for_commands

    :return: None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_params_file_path", dest="input_params_file_path")
    
    args = parser.parse_args()

    with open(args.input_params_file_path) as f:
        input_params = json.load(f)

    d = ReplayDriver(input_params)
    d.log.info("Started Replay driver ...")
    d.wait_for_commands()


if __name__ == "__main__":
    main()


