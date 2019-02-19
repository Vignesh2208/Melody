import shared_buffer
from shared_buffer import *
import sys
import threading
import logger
import datetime
from datetime import datetime
from defines import *
from src.proto import pss_pb2
import time
from src.utils.sleep_functions import sleep


class basicHostIPCLayer(threading.Thread):
    def __init__(self, host_id, log_file, powersim_ids_mapping, managed_powersim_id):
        threading.Thread.__init__(self)


        self.thread_cmd_queue = []
        self.host_id = host_id
        self.managed_powersim_id = managed_powersim_id
        self.powersim_ids_mapping = powersim_ids_mapping

        self.host_ip = self.powersim_ids_mapping[self.managed_powersim_id]["mapped_host_ip"]
        self.listen_port = self.powersim_ids_mapping[self.managed_powersim_id]["port"]

        self.log = logger.Logger(log_file, "Host " + str(host_id) + " IPC Thread")
        self.raw_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    """ -- DO NOT OVERRIDE -- """

    def get_curr_cmd(self):
        try:
            curr_cmd = self.thread_cmd_queue.pop()
        except IndexError:
            return None
        return curr_cmd

    """ -- DO NOT OVERRIDE -- """

    def cancel_thread(self):
        self.thread_cmd_queue.append(CMD_QUIT)



    """ -- DO NOT OVERRIDE -- """

    def tx_pkt_to_powersim_entity(self, pkt):
        pkt_parsed = pss_pb2.CyberMessage()
        pkt_parsed.ParseFromString(pkt)
        cyber_entity_ip = self.powersim_ids_mapping[pkt_parsed.dst_application_id]["mapped_host_ip"]
        cyber_entity_port = self.powersim_ids_mapping[pkt_parsed.dst_application_id]["port"]
        self.raw_sock.sendto(pkt, (cyber_entity_ip, cyber_entity_port))


    """ -- DO NOT OVERRIDE -- """

    def run(self):

        self.log.info("Started underlying IPC layer ... ")
        self.log.info("Started listening on IP: " + self.host_ip + " PORT: " + str(self.listen_port))
        sys.stdout.flush()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.settimeout(SOCKET_TIMEOUT)
        sock.bind((self.host_ip, self.listen_port))


        self.on_start_up()
        while True:

            curr_cmd = self.get_curr_cmd()
            if curr_cmd is not None and curr_cmd == CMD_QUIT:
                self.on_shutdown()
                self.log.info("Stopping ... ")
                sys.stdout.flush()
                break

            try:
                data, addr = sock.recvfrom(MAXPKTSIZE)
            except socket.timeout:
                data = None
            if data is not None:
                self.on_rx_pkt_from_network(str(data))



    """
        This function gets called on reception of message from network.
        It can be overriden by the IPC layer to selectively relay the pkt to proxy. The pkt needs to be
        relayed to the proxy only if it is a REQUEST. It the pkt is a RESPONSE, it simply needs to be processed
        by the IPC layer.
        
        pkt will be 
    """

    def on_rx_pkt_from_network(self, pkt):
        pass

    """
        Called after initialization of IPC layer. It can be overridden to start essential services.
    """

    def on_start_up(self):
        pass

    """
       Called before initiating shutdown of IPC. It can be overridden to stop essential services.
    """

    def on_shutdown(self):
        pass
