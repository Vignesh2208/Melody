
import threading
import time
import srcs.lib.defines as defines
from srcs.lib.basicHostIPCLayer import basicHostIPCLayer
from srcs.proto import css_pb2


class PLC(threading.Thread):
    """A simple PLC implementation. It receives commands from SCADA controller and controls generator bus voltages.

    """
    def __init__(self, host_control_layer, plc_name, params):
        """

        :param host_control_layer: hostApplicationLayer object
        :param plc_name: application_id
        :type plc_name: str
        """
        threading.Thread.__init__(self)
        self.host_control_layer = host_control_layer
        self.stop = False
        self.plc_name = plc_name
        self.recv_pkt_queue = []
        self.params = params


    def run(self):
        request_no = 0

        obj_type_to_write = self.params["objtype"]
        field_type_to_write = self.params["fieldtype"]
        obj_id_to_write = self.params["objid"]

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

            self.host_control_layer.log.info(
                f"Received new control message from SCADA controller: {str(pkt_parsed)}")
            voltage_setpoint = None
            for data_content in pkt_parsed.content:
                if data_content.key == "VOLTAGE_SETPOINT":
                    voltage_setpoint = data_content.value
            assert(voltage_setpoint is not None)

            # Sends a write request to the proxy based on the received command from SCADA controller
            self.host_control_layer.log.info(
                "Sending RPC Write Request ...")
            defines.rpc_write([(obj_type_to_write, obj_id_to_write, field_type_to_write, voltage_setpoint)])
            self.host_control_layer.log.info(
                "----------------------------------------")

            request_no += 1


class hostApplicationLayer(basicHostIPCLayer):

    def __init__(self, host_id, log_file, application_ids_mapping, managed_application_id, params):
        basicHostIPCLayer.__init__(self, host_id, log_file, application_ids_mapping, managed_application_id, params)
        self.cmd_lock = threading.Lock()
        self.PLC = PLC(self, self.managed_application_id, params)


    def on_rx_pkt_from_network(self, pkt):
        """
            This function gets called on reception of message from network.
            pkt will be a string of type CyberMessage proto defined in srcs/proto/css.proto
            A packet sent by the SCADA controller will be caught here.
        """
        pkt_parsed = css_pb2.CyberMessage()
        pkt_parsed.ParseFromString(pkt)
        self.PLC.recv_pkt_queue.append(pkt)


    def on_start_up(self):
        """
            Called after initialization of application layer. Here we start the PLC thread.
        """
        
        self.log.info(f"Started PLC: {self.managed_application_id}")
        self.PLC.start()
        

    def on_shutdown(self):
        """
            Called before shutdown of application layer. Here we shutdown the PLC thread
        """
        self.PLC.stop = True
        self.PLC.join()
        self.log.info(f"Stopping PLC: {self.managed_application_id}")
