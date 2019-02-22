
import threading
from src.core.defines import *
from src.core.basicHostIPCLayer import basicHostIPCLayer
from src.proto import css_pb2


class PLC(threading.Thread):
    def __init__(self, host_control_layer, plc_name):
        threading.Thread.__init__(self)
        self.host_control_layer = host_control_layer
        self.stop = False
        self.plc_name = plc_name
        self.recv_pkt_queue = []
        self.obj_id = self.plc_name.split('_')[-1]
        self.field_type = "Vg"
        self.obj_type = "gen"


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

            pkt_parsed = css_pb2.CyberMessage()
            pkt_parsed.ParseFromString(data)

            self.host_control_layer.log.info("Rx New packet for PLC: \n" + str(pkt_parsed))
            voltage_setpoint = None
            for data_content in pkt_parsed.content:
                if data_content.key == "VOLTAGE_SETPOINT":
                    voltage_setpoint = data_content.value
            assert(voltage_setpoint is not None)
            self.host_control_layer.log.info("Sending RPC Write Request ...")
            rpc_write([(self.obj_type, self.obj_id, self.field_type, voltage_setpoint)])
            self.host_control_layer.log.info("----------------------------------------")

            request_no += 1


class hostApplicationLayer(basicHostIPCLayer):

    def __init__(self, host_id, log_file, powersim_ids_mapping, managed_application_id):
        basicHostIPCLayer.__init__(self, host_id, log_file, powersim_ids_mapping, managed_application_id)
        self.cmd_lock = threading.Lock()
        self.PLC = PLC(self, self.managed_application_id)


    """
        This function gets called on reception of message from network.
        pkt will be a string of type CyberMessage proto defined in src/proto/pss.proto
    """

    def on_rx_pkt_from_network(self, pkt):
        pkt_parsed = css_pb2.CyberMessage()
        pkt_parsed.ParseFromString(pkt)
        self.PLC.recv_pkt_queue.append(pkt)



    """
        Called after initialization of IPC layer. It can be overridden to start essential services.
    """

    def on_start_up(self):

        self.PLC.start()
        self.log.info("Started PLC: " + self.managed_application_id + " on " + str(self.host_id))

    """
       Called before initiating shutdown of IPC. It can be overridden to stop essential services.
    """

    def on_shutdown(self):
        self.PLC.stop = True
        self.PLC.join()
        self.log.info("Stopping PLC: "  + self.managed_application_id + " on " + str(self.host_id))
