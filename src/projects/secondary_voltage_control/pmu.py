from src.core.basicHostIPCLayer import basicHostIPCLayer
from src.core.defines import *
import grpc
import time
import sys
import random
import threading

from src.proto import pss_pb2
from src.proto import pss_pb2_grpc



class PMU(threading.Thread):
    def __init__(self, host_control_layer, pmu_name):
        threading.Thread.__init__(self)
        self.host_control_layer = host_control_layer
        self.stop = False
        self.pmu_name = pmu_name
        self.raw_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.obj_type = "bus"
        self.obj_id = self.pmu_name.split('_')[-1]
        self.field_type = "v"



    def tx_pkt_to_powersim_entity(self, pkt, dst_application_id):
        ip_addr = self.host_control_layer.powersim_ids_mapping[dst_application_id]["mapped_host_ip"]
        port = self.host_control_layer.powersim_ids_mapping[dst_application_id]["port"]
        
        self.raw_sock.sendto(str(pkt), (ip_addr, port))


    def run(self):
        request_no = 0
        while not self.stop:


            pkt = pss_pb2.CyberMessage()
            pkt.src_application_id = self.pmu_name
            pkt.dst_application_id = "SCADA_CONTROLLER"
            pkt.msg_type = "PERIODIC_UPDATE"
            data = pkt.content.add()
            data.key = "VOLTAGE"


            ret = rpc_read(self.obj_type, self.obj_id, self.field_type)
            assert(ret is not None)
            data.value = ret

            data = pkt.content.add()
            data.key = "TIMESTAMP"
            data.value = str(time.time())

            data = pkt.content.add()
            data.key = "COUNTER"
            data.value = str(request_no)

            data = pkt.content.add()
            data.key = "OBJ_ID"
            data.value = self.obj_id


            self.host_control_layer.log.info("Sending Reading: \n" + str(pkt))
            self.tx_pkt_to_powersim_entity(pkt.SerializeToString(), pkt.dst_application_id)
            time.sleep(1)
            request_no += 1




class hostApplicationLayer(basicHostIPCLayer):

    def __init__(self, host_id, log_file, powersim_ids_mapping, managed_application_id):
        basicHostIPCLayer.__init__(self, host_id, log_file, powersim_ids_mapping, managed_application_id)
        self.PMU = PMU(self, managed_application_id)


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

        self.log.info("Started PMU:  " + self.managed_application_id + " on " + str(self.host_id))
        self.PMU.start()

    """
       Called before initiating shutdown of IPC. It can be overridden to stop essential services.
    """

    def on_shutdown(self):
        self.PMU.stop = True
        self.PMU.join()
        self.log.info("Stopped PMU: " + self.managed_application_id + " on " + str(self.host_id))
