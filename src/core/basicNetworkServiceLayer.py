import shared_buffer
from shared_buffer import *
import sys
import os
import threading
import logger
from logger import Logger
from defines import *
import socket
import Queue
from datetime import datetime


class basicNetworkServiceLayer(threading.Thread):

    def __init__(self, host_id, log_file, host_id_to_ip):
        threading.Thread.__init__(self)

        self.thread_cmd_lock = threading.Lock()
        self.thread_cmd_queue = []
        self.host_id = host_id
        self.ip_map = host_id_to_ip
        self.host_ip, self.listen_port = self.ip_map[self.host_id]
        self.log = logger.Logger(log_file, "Host " + str(self.host_id) + " Network Layer Thread")
        self.host_id_to_powersim_entity_id = None
        self.powersim_entity_id_To_host_id = None
        self.attack_layer = None

    def set_attack_layer(self, attack_layer):
        self.attack_layer = attack_layer

    def get_attack_layer(self):
        return self.attack_layer

    def get_curr_cmd(self):
        self.thread_cmd_lock.acquire()
        curr_cmd = None
        if len(self.thread_cmd_queue) > 0 :
            curr_cmd = self.thread_cmd_queue.pop()
        self.thread_cmd_lock.release()
        return curr_cmd

    def cancel_thread(self):
        self.thread_cmd_lock.acquire()
        self.thread_cmd_queue.append(CMD_QUIT)
        self.thread_cmd_lock.release()

    def on_rx_pkt_from_network(self, pkt):
        self.attack_layer.run_on_thread(self.attack_layer.on_rx_pkt_from_network_layer,
                                        extract_powersim_entity_id_from_pkt(pkt), pkt)

    def run(self):
        self.log.info("Started listening on IP: " + self.host_ip + " PORT: " + str(self.listen_port))
        sys.stdout.flush()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.settimeout(SOCKET_TIMEOUT)
        sock.bind((self.host_ip, self.listen_port))

        while True:
            curr_cmd = self.get_curr_cmd()
            if curr_cmd is not None and curr_cmd == CMD_QUIT:
                self.log.info("Stopping Network Layer Thread ...")
                sys.stdout.flush()
                sock.close()
                break
            try:
                data, addr = sock.recvfrom(MAXPKTSIZE)
            except socket.timeout:
                data = None
            if data is not None:
                #self.log.info("%s  RECV_FROM=%s:%s  PKT=%s" % (datetime.now(), str(addr[0]), str(addr[1]), str(data)))
                self.on_rx_pkt_from_network(str(data))
