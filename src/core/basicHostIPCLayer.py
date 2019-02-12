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
    def __init__(self, host_id, log_file):
        threading.Thread.__init__(self)

        self.thread_cmd_lock = threading.Lock()
        self.thread_callback_queue = {}
        self.thread_callback_lock = threading.Lock()
        self.n_pending_callbacks = 0

        self.thread_cmd_queue = []
        self.host_id = host_id
        self.log = logger.Logger(log_file, "Host " + str(host_id) + " IPC Thread")
        self.host_id_to_powersim_id = None
        self.powersim_id_to_host_id = None
        self.attack_layer = None
        self.raw_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

    """ -- DO NOT OVERRIDE -- """

    def set_attack_layer(self, attack_layer):
        self.attack_layer = attack_layer

    """ -- DO NOT OVERRIDE -- """

    def get_attack_layer(self):
        return self.attack_layer

    """ -- DO NOT OVERRIDE -- """

    def get_curr_cmd(self):
        curr_cmd = None
        self.thread_cmd_lock.acquire()
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

    def set_powersim_id_map(self, powersim_id_map):
        self.host_id_to_powersim_id = powersim_id_map
        self.powersim_id_to_host_id = {}
        for host_id in self.host_id_to_powersim_id.keys():
            powersim_id_set = self.host_id_to_powersim_id[host_id]
            for powersim_entity_id in powersim_id_set:
                self.powersim_id_to_host_id[powersim_entity_id] = host_id

    """ -- DO NOT OVERRIDE -- """

    def get_mapped_powersim_ids_for_node(self, cyber_entity_id):
        if cyber_entity_id in self.host_id_to_powersim_id.keys():
            return self.host_id_to_powersim_id[cyber_entity_id]
        else:
            return None

    """ -- DO NOT OVERRIDE -- """

    def get_mapped_cyber_entity_for_node(self, powersim_entity_id):
        if powersim_entity_id in self.powersim_id_to_host_id.keys():
            return self.powersim_id_to_host_id[powersim_entity_id]
        else:
            return None

    """ -- DO NOT OVERRIDE -- """

    def tx_pkt_to_powersim_entity(self, pkt):
        pkt_parsed = pss_pb2.PowerSimMessage()
        pkt_parsed.ParseFromString(pkt)
        if pkt_parsed.HasField("read_request"):
            dst_powersim_entity_id = pkt_parsed.read_request.objid
        elif pkt_parsed.HasField("write_request"):
            dst_powersim_entity_id = pkt_parsed.write_request.objid
        elif pkt_parsed.HasField("response"):
            dst_powersim_entity_id = pkt_parsed.response.receiver_attributes.receiver_id
        else:
            dst_powersim_entity_id = None

        cyber_entity_id = self.get_mapped_cyber_entity_for_node(dst_powersim_entity_id)
        if cyber_entity_id is not None:
            self.attack_layer.run_on_thread(self.attack_layer.on_rx_pkt_from_ipc_layer,
                                            dst_powersim_entity_id, pkt, cyber_entity_id)

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

        self.log.info("Started underlying IPC layer ... ")
        #self.log.info("Power sim id to cyber entity id map: " + str(self.powersim_id_to_host_id))
        #self.log.info("Cyber entity id to powersim id map: " + str(self.host_id_to_powersim_id))
        sys.stdout.flush()
        assert (self.attack_layer is not None)
        self.on_start_up()
        while True:

            curr_cmd = self.get_curr_cmd()
            if curr_cmd is not None and curr_cmd == CMD_QUIT:
                self.on_shutdown()
                self.log.info("Stopping ... ")
                sys.stdout.flush()
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