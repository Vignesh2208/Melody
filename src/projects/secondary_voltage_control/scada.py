from src.core.basicHostIPCLayer import basicHostIPCLayer
from src.proto import pss_pb2
from src.utils.sleep_functions import *
from src.core.defines import *
import threading
import time
import random

class hostApplicationLayer(basicHostIPCLayer):

    def __init__(self, host_id, log_file, host_id_to_powersim_id, host_id_to_ip):
        basicHostIPCLayer.__init__(self, host_id, log_file, host_id_to_powersim_id, host_id_to_ip)

        self.mapped_PLCs = {
                                "PMU_Pilot_Bus_2": "PLC_GenBus_30",
                                "PMU_Pilot_Bus_6": "PLC_GenBus_31",
                                "PMU_Pilot_Bus_9": "PLC_GenBus_32",
                                "PMU_Pilot_Bus_10": "PLC_GenBus_33",
                                "PMU_Pilot_Bus_19": "PLC_GenBus_34",
                                "PMU_Pilot_Bus_20": "PLC_GenBus_35",
                                "PMU_Pilot_Bus_22": "PLC_GenBus_36",
                                "PMU_Pilot_Bus_23": "PLC_GenBus_37",
                                "PMU_Pilot_Bus_25": "PLC_GenBus_38",
                                "PMU_Pilot_Bus_29": "PLC_GenBus_39",
                            }

    """
        This function gets called on reception of message from network.
        pkt will be a string of type CyberMessage proto defined in src/proto/pss.proto
    """

    def on_rx_pkt_from_network(self, pkt):
        pkt_parsed = pss_pb2.CyberMessage()
        pkt_parsed.ParseFromString(pkt)

        if pkt_parsed.src_application_id in self.mapped_PLCs:
            pkt_new = pss_pb2.CyberMessage()
            pkt_new.src_application_id = "SCADA_CONTROLLER"
            pkt_new.dst_application_id = self.mapped_PLCs[pkt_parsed.src_application_id]
            data = pkt_new.content.add()
            data.key = "VOLTAGE_SETPOINT"
            data.value = str(random.uniform(1, 10))

            for content_ in pkt_parsed.content:
                if str(content_.key) == "TIMESTAMP":
                    pmu_send_timestamp = content_.value
                    break

            data = pkt_new.content.add()
            data.key = "TIMESTAMP"
            data.value = str(pmu_send_timestamp)

            self.log.info("Tx New Pkt: " + str(pkt_new))
            self.tx_pkt_to_powersim_entity(pkt_new.SerializeToString())



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
