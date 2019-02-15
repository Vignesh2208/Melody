from src.core.basicHostIPCLayer import basicHostIPCLayer
from src.proto import pss_pb2
from src.utils.sleep_functions import *
from src.core.defines import *
import threading
import time
import random


class PMU(threading.Thread):
    def __init__(self, host_control_layer, pmu_names):
        threading.Thread.__init__(self)
        self.host_control_layer = host_control_layer
        self.stop = False
        self.pmu_names = pmu_names
        self.raw_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    def tx_pkt_to_powersim_entity(self, pkt, dst_application_id):
        mapped_cyber_entity = self.host_control_layer.powersim_id_to_host_id[dst_application_id]
        ip_addr, port = self.host_control_layer.ip_map[mapped_cyber_entity]
        print "Sending to IP,Port: ", ip_addr, port
        self.raw_sock.sendto(str(pkt), (ip_addr, port))


    def run(self):
        request_no = 0
        while not self.stop:

            for pmu_name in self.pmu_names:

                pkt = pss_pb2.CyberMessage()
                pkt.src_application_id = pmu_name
                pkt.dst_application_id = "SCADA_CONTROLLER"
                pkt.msg_type = "PERIODIC_UPDATE"
                data = pkt.content.add()
                data.key = "VOLTAGE"
                data.value = str(random.uniform(1, 10))

                data = pkt.content.add()
                data.key = "CURRENT"
                data.value = str(random.uniform(1, 10))

                data = pkt.content.add()
                data.key = "TIMESTAMP"
                data.value = str(time.time())

                data = pkt.content.add()
                data.key = "COUNTER"
                data.value = str(request_no)
                dst_app_id = pkt.dst_application_id
                self.tx_pkt_to_powersim_entity(pkt.SerializeToString(), dst_app_id)

            request_no += 1
            time.sleep(1)


class hostApplicationLayer(basicHostIPCLayer):

    def __init__(self, host_id, log_file, host_id_powersim_id, host_id_to_ip):
        basicHostIPCLayer.__init__(self, host_id, log_file, host_id_powersim_id, host_id_to_ip)
        self.pmu_names = []

        for pmu_name in self.host_id_to_powersim_id[self.host_id]:
            self.pmu_names.append(pmu_name)

        self.PMU = PMU(self, self.pmu_names)


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

        self.PMU.start()
        self.log.info("Started PMUs on " + str(self.host_id))

    """
       Called before initiating shutdown of IPC. It can be overridden to stop essential services.
    """

    def on_shutdown(self):
        self.PMU.stop = True
        self.PMU.join()
        self.log.info("Stopped PMUs on " + str(self.host_id))
