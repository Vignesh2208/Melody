"""Default co-simulation application layer.

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>
"""


import threading
import socket
import srcs.lib.logger as logger
import srcs.lib.defines as defines

from srcs.proto import css_pb2

class basicHostIPCLayer(threading.Thread):
    """Default application layer of co-simulation processes spawned inside mininet hosts
    
    A co-simulation process may implement a specific application layer by inheriting from this class.
    Co-simulation processes may interact with the power simulator through by making GRPC
    calls to the proxy.
    """
    def __init__(self, host_id, log_file, application_ids_mapping,
                 managed_application_id, params):
        """Initialization

        :param host_id: The mininet host name in which this thread is spawned
        :type host_id: str
        :param log_file: The absolute path to a file which will log stdout
        :type log_file: str
        :param application_ids_mapping: A dictionary which maps application_id to ip_address,port
        :type application_ids_mapping: dict
        :param managed_application_id: Application id assigned to this co-simulation process
        :type managed_application_id: str
        :param params: is a dictionary containing parameters of key,value strings
        :return:  None
        """
        threading.Thread.__init__(self)

        self.thread_cmd_queue = []
        self.host_id = host_id
        self.managed_application_id = managed_application_id
        self.application_ids_mapping = application_ids_mapping

        self.host_ip = self.application_ids_mapping[self.managed_application_id]["mapped_host_ip"]
        self.listen_port = self.application_ids_mapping[self.managed_application_id]["port"]

        self.log = logger.Logger(log_file, f"Host {str(host_id)} IPC Thread")
        self.raw_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.params = params

    def get_curr_cmd(self):
        """Gets the current pending command sent by the co-simulation host process

        :return: str or None -- the command sent from the process to this thread
        .. note:: Do not override
        """
        try:
            curr_cmd = self.thread_cmd_queue.pop()
        except IndexError:
            return None
        return curr_cmd

    def cancel_thread(self):
        """Send a command to terminate this thread

        :return: None
        .. note:: Do not override
        """
        self.thread_cmd_queue.append(defines.CMD_QUIT)

    def tx_pkt_to_powersim_entity(self, pkt):
        """Transmit a co-simulation packet over the mininet cyber network

        :param pkt: A packet string which is converted to CyberMessage proto and sent over the network
        :type pkt: str
        :return: None
        .. note:: Do not override
        """
        pkt_parsed = css_pb2.CyberMessage()
        pkt_parsed.ParseFromString(pkt)
        cyber_entity_ip = self.application_ids_mapping[
            pkt_parsed.dst_application_id]["mapped_host_ip"]
        cyber_entity_port = self.application_ids_mapping[
            pkt_parsed.dst_application_id]["port"]
        self.raw_sock.sendto(pkt, (cyber_entity_ip, cyber_entity_port))

    def run(self):
        """Main run function which starts the thread functionality

        Monitors the mininet network on ip,port specified for the assigned application_id. Upon
        receiving a packet intended for this application, it calls on_rx_packet_from_network

        :return: None
        .. note:: Do not override
        """
        self.log.info("Started underlying IPC layer ... ")
        self.log.info(f"Started listening on IP: {self.host_ip} "
                      f"PORT: {str(self.listen_port)}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.settimeout(defines.SOCKET_TIMEOUT)
        sock.bind((self.host_ip, self.listen_port))


        self.on_start_up()
        while True:

            curr_cmd = self.get_curr_cmd()
            if curr_cmd is not None and curr_cmd == defines.CMD_QUIT:
                self.on_shutdown()
                self.log.info("Stopping ... ")
                
                break

            try:
                data, addr = sock.recvfrom(defines.MAXPKTSIZE)
            except socket.timeout:
                data = None
            if data is not None:
                self.on_rx_pkt_from_network(data)

    def on_rx_pkt_from_network(self, pkt):
        """This function gets called on reception of message from network.

        It may be overriden in the specific application layer implementation for a variety of purposes

        :param pkt: A packet string of the CyberMessage proto format specified in srcs/proto/css.proto
        :type pkt: str
        :return: None
        """
        pass

    def on_start_up(self):
        """This function gets called on thread start up after all initilization is complete.

        It may be overridden in specific application layer implementations for starting
        user defined services.

        :return: None
        """
        pass

    def on_shutdown(self):
        """This function gets called upon shutdown of the thread.

        It may be overridden in specific application layer implementations for cleanup

        :return:  None
        """
        pass
