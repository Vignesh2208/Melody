from src.core.basicHostIPCLayer import basicHostIPCLayer
from src.proto import pss_pb2
from src.utils.sleep_functions import *
from src.core.defines import *
import threading
import time


class PMU(threading.Thread):
    def __init__(self, host_control_layer):
        threading.Thread.__init__(self)
        self.host_control_layer = host_control_layer
        self.stop = False

    def run(self):
        request_no = 0
        while not self.stop:

            if request_no % 3 == 0:
                pkt = pss_pb2.PowerSimMessage()
                pkt.response.value = "1.5V"
                pkt.response.receiver_attributes.receiver_id = "PLC123"
                pkt.response.receiver_attributes.response_id = "1234"
            elif request_no % 3 == 1:
                pkt = pss_pb2.PowerSimMessage()
                pkt.read_request.timestamp = str(request_no)
                pkt.read_request.objtype = "PLC"
                pkt.read_request.objid = "PLC123"
                pkt.read_request.fieldtype = "config"
                pkt.read_request.sender_attributes.sender_id = "PMU123"
                pkt.read_request.sender_attributes.request_id = "4567"
            else:
                pkt = pss_pb2.PowerSimMessage()
                pkt.write_request.timestamp = str(request_no)
                pkt.write_request.objtype = "PLC"
                pkt.write_request.objid = "PLC123"
                pkt.write_request.fieldtype = "register"
                pkt.write_request.value = "Value_to_be_written"
                pkt.write_request.sender_attributes.sender_id = "PMU123"
                pkt.write_request.sender_attributes.request_id = "7890"

            request_no += 1
            self.host_control_layer.tx_pkt_to_powersim_entity(pkt.SerializeToString())
            time.sleep(1)


class hostControlLayer(basicHostIPCLayer):

    def __init__(self, host_id, log_file):
        basicHostIPCLayer.__init__(self, host_id, log_file)
        self.PMU123 = PMU(self)

    """
        This function gets called on reception of message from network.
        pkt will be a string of type PowerSimMessage proto defined in src/proto/pss.proto
    """

    def on_rx_pkt_from_network(self, pkt):
        # just print the proto message for now
        pkt_parsed = pss_pb2.PowerSimMessage()
        pkt_parsed.ParseFromString(pkt)

        self.log.info("Rx New packet for mapped powersim entity: " + str(extract_powersim_entity_id_from_pkt(pkt)))
        self.log.info(str(pkt_parsed))


    """
        Called after initialization of IPC layer. It can be overridden to start essential services.
    """

    def on_start_up(self):
        self.PMU123.start()
        self.log.info("Started PMU123")

    """
       Called before initiating shutdown of IPC. It can be overridden to stop essential services.
    """

    def on_shutdown(self):
        self.PMU123.stop = True
        self.PMU123.join()