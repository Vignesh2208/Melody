
from src.core.defines import *
from src.core.basicHostIPCLayer import basicHostIPCLayer
from src.proto import pss_pb2
from src.utils.sleep_functions import *


class hostControlLayer(basicHostIPCLayer):

    def __init__(self, host_id, log_file):
        basicHostIPCLayer.__init__(self, host_id, log_file)

    """
        This function gets called on reception of message from network.
        pkt will be a string of type CyberMessage proto defined in src/proto/pss.proto
    """

    def on_rx_pkt_from_network(self, pkt):
        # just print the proto message for now
        pkt_parsed = pss_pb2.CyberMessage()
        pkt_parsed.ParseFromString(pkt)

        self.log.info("Rx New packet for mapped powersim entity: " + str(extract_powersim_entity_id_from_pkt(pkt)))
        self.log.info("\n" + str(pkt_parsed))


    """
        Called after initialization of IPC layer. It can be overridden to start essential services.
    """

    def on_start_up(self):
        self.log.info("Started PLC123")

    """
       Called before initiating shutdown of IPC. It can be overridden to stop essential services.
    """

    def on_shutdown(self):
        pass
