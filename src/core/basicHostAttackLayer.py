import sys
import threading
import logger
from datetime import datetime
from defines import *


class basicHostAttackLayer(threading.Thread):

    def __init__(self, host_id, log_file, ipc_layer, network_service_layer):

        threading.Thread.__init__(self)
        self.thread_cmd_lock = threading.Lock()
        self.thread_callback_lock = threading.Lock()

        self.thread_cmd_queue = []
        self.thread_callback_queue = {}
        self.n_pending_callbacks = 0
        self.host_id = host_id
        self.log = logger.Logger(log_file, "Host " + str(host_id) + " Attack Layer Thread")
        self.ipc_layer = ipc_layer
        self.net_service_layer = network_service_layer
        self.ip_mapping = self.net_service_layer.ip_map
        self.myIP = self.ip_mapping[self.host_id][0]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.stopping = False


    """ -- DO NOT OVERRIDE -- """

    def get_curr_cmd(self):
        self.thread_cmd_lock.acquire()
        curr_cmd = None
        if len(self.thread_cmd_queue) > 0:
            curr_cmd = self.thread_cmd_queue.pop()
        self.thread_cmd_lock.release()
        return curr_cmd

    """ -- DO NOT OVERRIDE -- """

    def cancel_thread(self):
        self.thread_cmd_lock.acquire()
        self.thread_cmd_queue.append(CMD_QUIT)
        self.thread_cmd_lock.release()

    """ -- DO NOT OVERRIDE -- """

    def send_udp_msg(self, pkt, ip_addr, port):
        #self.log.info("%s  SEND_TO=%s:%s  PKT=%s" % (datetime.now(), str(ip_addr), str(port), str(pkt)))
        self.sock.sendto(pkt, (ip_addr, port))

    """ -- DO NOT OVERRIDE -- """

    def tx_pkt(self, pkt, dst_cyber_entity_id):
        if dst_cyber_entity_id in self.net_service_layer.ip_map.keys():
            ip_addr, port = self.net_service_layer.ip_map[dst_cyber_entity_id]
            self.send_udp_msg(pkt, ip_addr, port)

    """ -- DO NOT OVERRIDE -- """

    def tx_async_net_service_layer(self, pkt, dst_cyber_entity_id):
        self.tx_pkt(pkt, dst_cyber_entity_id)

    """ -- DO NOT OVERRIDE -- """

    def tx_async_ipc_layer(self, pkt):
        self.ipc_layer.run_on_thread(self.ipc_layer.on_rx_pkt_from_network,
                                     extract_powersim_entity_id_from_pkt(pkt), pkt)

    """ -- DO NOT OVERRIDE -- """

    def run_on_thread(self, function, powersim_entity_id, *args):
        self.thread_callback_lock.acquire()
        if powersim_entity_id not in self.thread_callback_queue.keys():
            self.thread_callback_queue[powersim_entity_id] = []
            self.thread_callback_queue[powersim_entity_id].append((function, args))
        else:
            if len(self.thread_callback_queue[powersim_entity_id]) == 0:
                self.thread_callback_queue[powersim_entity_id].append((function, args))
            else:
                self.thread_callback_queue[powersim_entity_id][0] = (function, args)
        self.n_pending_callbacks = self.n_pending_callbacks + 1
        self.thread_callback_lock.release()


    """ -- DO NOT OVERRIDE -- """

    def run(self):

        self.log.info("Started ...")
        sys.stdout.flush()

        assert (self.net_service_layer is not None)
        assert (self.ipc_layer is not None)
        while True:

            curr_cmd = self.get_curr_cmd()
            if curr_cmd is not None and curr_cmd == CMD_QUIT:
                self.log.info("Stopping ... ")
                sys.stdout.flush()
                self.stopping = True
                break

            callback_fns = []
            self.thread_callback_lock.acquire()
            if self.n_pending_callbacks == 0:
                self.thread_callback_lock.release()
            else:

                values = list(self.thread_callback_queue.values())
                for i in xrange(0, len(values)):
                    if len(values[i]) > 0:
                        callback_fns.append(values[i].pop())
                self.n_pending_callbacks = 0
                self.thread_callback_lock.release()

                for i in xrange(0, len(callback_fns)):
                    function, args = callback_fns[i]
                    function(*args)

            self.idle()

    """ can be overriden to send async messages to network and ipc layers
        using tx_async_net_service_layer and tx_async_ipc_layer
        functions
    """

    def idle(self):
        pass

    """
        Default behaviour - do nothing and simply relay packet to ipc layer
        Can be overridden to intercept/drop/change packets before being sent to powersim entities
    """

    def on_rx_pkt_from_network_layer(self, pkt):
        self.ipc_layer.run_on_thread(self.ipc_layer.on_rx_pkt_from_network,
                                     extract_powersim_entity_id_from_pkt(pkt), pkt)

    """
        Default behaviour - do nothing and simply relay packet to network Layer
        Can be overridden to intercept/drop/change packets before transmission over the cyber network
    """

    def on_rx_pkt_from_ipc_layer(self, pkt, dst_node_id):
        self.tx_async_net_service_layer(pkt, dst_node_id)
