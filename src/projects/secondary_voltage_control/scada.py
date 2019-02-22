from src.core.basicHostIPCLayer import basicHostIPCLayer
from src.core.defines import *
from src.proto import css_pb2
import threading
import time
import numpy as np
import config as cfg
import cPickle as pickle

def loadObjectBinary(filename):
    with open(filename, "rb") as input:
        obj = pickle.load(input)
    print "# " + filename + " loaded"
    return obj

class SCADA(threading.Thread):
    def __init__(self, host_control_layer, scada_controller_name):
        threading.Thread.__init__(self)
        self.host_control_layer = host_control_layer
        self.stop = False
        self.scada_controller_name = scada_controller_name

    def run(self, debug=False):

        _vp_nom = np.array([cfg.BUS_VM[bus] for bus in cfg.PILOT_BUS])
        _vg = np.array([cfg.BUS_VM[gen] for gen in cfg.GEN])
        C = loadObjectBinary("C.bin")
        Cp = np.matrix([C[i] for i in range(cfg.LOAD_NO) if cfg.LOAD[i] in cfg.PILOT_BUS])
        Cpi = Cp.I
        alpha = 0.9

        while not self.stop:
            _vp = np.array([self.host_control_layer.vp[bus] for bus in cfg.PILOT_BUS])
            u = np.dot(Cpi, alpha * (_vp - _vp_nom)).A1  # 1-d base array
            _vg = np.array(_vg + u)


            for i in range(cfg.GEN_NO):
                pkt_new = css_pb2.CyberMessage()
                pkt_new.src_application_id = self.scada_controller_name
                pkt_new.dst_application_id = "PLC_Gen_Bus_%d"%cfg.GEN[i]
                data = pkt_new.content.add()
                data.key = "VOLTAGE_SETPOINT"
                data.value = str(_vg[i])

                data = pkt_new.content.add()
                data.key = "TIMESTAMP"
                data.value = str(time.time())

                self.host_control_layer.log.info("Tx New Control Pkt: " + str(pkt_new))
                self.host_control_layer.tx_pkt_to_powersim_entity(pkt_new.SerializeToString())

            time.sleep(1.5)

class hostApplicationLayer(basicHostIPCLayer):

    def __init__(self, host_id, log_file, powersim_ids_mapping, managed_application_id):
        basicHostIPCLayer.__init__(self, host_id, log_file, powersim_ids_mapping, managed_application_id)
        self.SCADA = SCADA(self, managed_application_id)
        self.vp = {bus:cfg.BUS_VM[bus] for bus in cfg.PILOT_BUS}

    """
        This function gets called on reception of message from network.
        pkt will be a string of type CyberMessage proto defined in src/proto/pss.proto
    """

    def on_rx_pkt_from_network(self, pkt):
        pkt_parsed = css_pb2.CyberMessage()
        pkt_parsed.ParseFromString(pkt)

        recv_obj_id = None
        recv_obj_value = None
        for data_content in pkt_parsed.content:
            if data_content.key == "OBJ_ID":
                recv_obj_id = int(data_content.value)
            if data_content.key == "VOLTAGE":
                recv_obj_value = float(data_content.value)
        assert(recv_obj_id is not None and recv_obj_value is not None)
        assert(recv_obj_id in self.vp)

        self.vp[recv_obj_id] = recv_obj_value
        self.log.info("Rx pkt from: %d = %s"%(recv_obj_id,str(pkt_parsed)))

    """
        Called after initialization of IPC layer. It can be overridden to start essential services.
    """

    def on_start_up(self):
        self.SCADA.start()

    """
       Called before initiating shutdown of IPC. It can be overridden to stop essential services.
    """

    def on_shutdown(self):
        self.SCADA.stop = True
        self.SCADA.join()
