
from src.core.defines import *
from src.core.basicHostIPCLayer import basicHostIPCLayer
from src.proto import pss_pb2
from src.utils.sleep_functions import *
import threading
import time


class PLC(threading.Thread):
    def __init__(self, host_control_layer, plc_name):
        threading.Thread.__init__(self)
        self.host_control_layer = host_control_layer
        self.stop = False
        self.plc_name = plc_name
        self.recv_pkt_queue = []

    def run(self):
        request_no = 0
        while not self.stop:

            try:
                data = self.recv_pkt_queue.pop()
            except IndexError:
                data = None

            if data is None:
                time.sleep(0.001)
                continue

            pkt_parsed = pss_pb2.CyberMessage()
            pkt_parsed.ParseFromString(data)

            for content_type in pkt_parsed.content:
                if content_type.key == "TIMESTAMP":
                    pmu_send_tstamp = float(content_type.value)

            #possibly make an RPC call here

            recv_time = float(time.time())

            self.host_control_layer.log.info("Rx New packet for PLC: \n" + str(pkt_parsed))
            self.host_control_layer.log.info("Experienced control delay:" + str(recv_time - pmu_send_tstamp))
            self.host_control_layer.log.info("----------------------------------------")

            request_no += 1


class hostApplicationLayer(basicHostIPCLayer):

    def __init__(self, host_id, log_file, powersim_ids_mapping, managed_powersim_id):
        basicHostIPCLayer.__init__(self, host_id, log_file, powersim_ids_mapping, managed_powersim_id)
        self.cmd_lock = threading.Lock()
        self.PLC = PLC(self, self.managed_powersim_id)


    """
        This function gets called on reception of message from network.
        pkt will be a string of type CyberMessage proto defined in src/proto/pss.proto
    """

    def on_rx_pkt_from_network(self, pkt):
        # just print the proto message for now
        pkt_parsed = pss_pb2.CyberMessage()
        pkt_parsed.ParseFromString(pkt)
        self.PLC.recv_pkt_queue.append(pkt)



    """
        Called after initialization of IPC layer. It can be overridden to start essential services.
    """

    def on_start_up(self):

        self.PLC.start()
        self.log.info("Started PLC: " + self.managed_powersim_id + " on " + str(self.host_id))

    """
       Called before initiating shutdown of IPC. It can be overridden to stop essential services.
    """

    def on_shutdown(self):
        self.PLC.stop = True
        self.PLC.join()
        self.log.info("Stopping PLC: "  + self.managed_powersim_id + " on " + str(self.host_id))
