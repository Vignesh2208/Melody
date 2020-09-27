import threading
import srcs.lib.defines as defines

from srcs.lib.basicHostIPCLayer import basicHostIPCLayer
from srcs.lib.defines import *
from srcs.proto import css_pb2



class PMU(threading.Thread):
    """Simple PMU implementation. It reads pilot buses ans sends the reading to a SCADA controller.
    """
    def __init__(self, host_control_layer, pmu_name, params):
        """

        :param host_control_layer: hostApplicationLayer object
        :param pmu_name: application_id
        :type pmu_name: str
        :param params: is a dictionary containing parameters of key,value strings
        """
        threading.Thread.__init__(self)
        self.host_control_layer = host_control_layer
        self.stop = False
        self.pmu_name = pmu_name
        self.raw_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.params = params




    def run(self):

        obj_type_to_read = self.params["objtype"]
        field_type_to_read = self.params["fieldtype"]
        obj_id_to_read = self.params["objid"]
        polling_time = float(self.params["polling_time_secs"])

        request_no = 0
        while not self.stop:
            pkt = css_pb2.CyberMessage()
            pkt.src_application_id = self.pmu_name
            pkt.dst_application_id = "SCADA_CONTROLLER"
            pkt.msg_type = "PERIODIC_UPDATE"

            #Sends an RPC read request to get pilot bus reading.
            pilot_busses_to_read = [
                (obj_type_to_read, obj_id_to_read, field_type_to_read)]
            ret = defines.rpc_read(pilot_busses_to_read)
            assert(ret is not None)

            assert (len(ret) == 1)


            data = pkt.content.add()
            data.key = "VOLTAGE"
            data.value = ret[0]

            data = pkt.content.add()
            data.key = "TIMESTAMP"
            data.value = str(time.time())

            data = pkt.content.add()
            data.key = "COUNTER"
            data.value = str(request_no)

            data = pkt.content.add()
            data.key = "OBJ_ID"
            data.value = obj_id_to_read

            #Sends pilot bus reading to SCADA controller.
            self.host_control_layer.log.info(f"Sending reading: {pkt}")
            self.host_control_layer.tx_pkt_to_powersim_entity(
                pkt.SerializeToString())
            time.sleep(polling_time)
            request_no += 1




class hostApplicationLayer(basicHostIPCLayer):

    def __init__(self, host_id, log_file,
        application_ids_mapping, managed_application_id, params):
        basicHostIPCLayer.__init__(self, host_id, log_file,
            application_ids_mapping, managed_application_id, params)
        self.PMU = PMU(self, managed_application_id, params)




    def on_rx_pkt_from_network(self, pkt):
        """
            This function gets called on reception of message from network.
            pkt will be a string of type CyberMessage proto defined in srcs/proto/css.proto
        """
        # just print the proto message for now
        pkt_parsed = css_pb2.CyberMessage()
        pkt_parsed.ParseFromString(pkt)

        self.log.info(f"Rx new packet from: {pkt_parsed.src_application_id}")
        self.log.info(f"\n{pkt_parsed}")


    def on_start_up(self):
        """
            Called after initialization of application layer. Here we start the PMU thread.
        """

        self.log.info(
            f"Started PMU: {self.managed_application_id}")
        self.PMU.start()


    def on_shutdown(self):
        """
            Called before shutdown of application layer. Here we shutdown the PMU thread
        """
        self.PMU.stop = True
        self.PMU.join()
        self.log.info(f"Stopped PMU: {self.managed_application_id}")
