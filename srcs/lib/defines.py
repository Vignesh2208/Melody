"""Helper functions.

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>
"""

import dpkt
import grpc
import sys
import time
import random
import socket
import logging

from dpkt.loopback import Loopback
from dpkt.ethernet import Ethernet
from dpkt.sll import SLL
from dpkt.ip import IP
from srcs.proto import pss_pb2
from srcs.proto import pss_pb2_grpc


# Error Defines
SUCCESS = 1
FAILURE = 0
EXIT_FAILURE = -1
EXIT_SUCCESS = 0
BUF_NOT_INITIALIZED = -1

# Other Defines
PROXY_NODE_ID = 0
CMD_QUIT = 1
MAXPKTSIZE = 10000
SOCKET_TIMEOUT = 1
ETH_TYPE_FRAME = 1


NS = 1
USEC = 1000*NS
MS = 1000*USEC
SEC = 1000*MS
NS_PER_MS = 1000000
NS_PER_SEC = 1000000000
GRPC_SERVER_LOCATION = "11.0.0.255:50051"

TRAFFIC_FLOW_ONE_SHOT = 'OneShot'

# Defines strings
EXIT_CMD = "EXIT"
START_CMD = "START"
NONE = "NONE"
LOADED_CMD = "LOADED"
SIGNAL_FINISH_CMD = "DONE"
TRIGGER_CMD = "TRIGGER"


def getid():
    """Returns a random unique string ID

    :return: str
    """
    return str(hash(time.time() + random.random()))


def rpc_read(readlist):
    """Makes a GRPC read request call to the proxy. It may be used to read some values from the power simulation.

    It takes in as input a list of read requests and composes and sends a single GRPC read request to the proxy.
    It waits until the proxy sends a response and returns the values contained in the response or None if there
    was an error.

    :param readlist: A list of tuples (objtype (str), objid (str), fieldtype (str)). Refer srcs/proto/pss.proto
    :type readlist: list of tuples
    :return: list of str or None
    """

    try:
        channel = grpc.insecure_channel(GRPC_SERVER_LOCATION)
        stub = pss_pb2_grpc.pssStub(channel)
        readRequest = pss_pb2.ReadRequest(timestamp=str(time.time()))

        counter = 0
        for objtype, objid, fieldtype in readlist:
            req = readRequest.request.add()
            req.id = str(counter)
            req.objtype = objtype
            req.objid = objid
            req.fieldtype = fieldtype
            req.value = ""
            counter += 1

        readResponse = stub.read(readRequest)
        response = {int(res.id):res.value for res in readResponse.response}
        return [response[id] for id in range(0,counter)]
    except:
        logging.info("Error in creating RPC read request ! Check /tmp/proxy_log.txt")
        return None


def rpc_write(writelist):
    """Makes a GRPC write request call to the proxy. It may be used to write some values to the power simulation

    It takes in as input a list of write requests and composes and sends a single GRPC write request to the proxy.
    It waits until the proxy sends a response and returns the status response or None if there was an error.

    :param writelist: A list of tuples (objtype (str), objid (str), fieldtype (str), value(str)).
                      Refer srcs/proto/pss.proto
    :type writelist: list of tuples
    :return: list of int (Refer srcs/proto/pss.proto: WriteStatus)  or None
    """

    try:
        channel = grpc.insecure_channel(GRPC_SERVER_LOCATION)
        stub = pss_pb2_grpc.pssStub(channel)
        writeRequest = pss_pb2.WriteRequest(timestamp=str(time.time()))

        counter = 0
        for objtype, objid, fieldtype, value in writelist:
            req = writeRequest.request.add()
            req.id = str(counter)
            req.objtype = objtype
            req.objid = objid
            req.fieldtype = fieldtype
            req.value = value
            counter += 1

        writeStatus = stub.write(writeRequest)
        status = {int(res.id): res.status for res in writeStatus.status}
        return [status[id] for id in range(0, counter)]
    except:
        logging.info("Error in creating RPC write request !. "
                     "Check /tmp/proxy_log.txt")
        
        return None


def rpc_process():
    """Sends a batch processing GRPC request request.

    Called by Melody to initiate processing of all read/write requests received in the last batch.

    :return: None
    """
    try:
        with grpc.insecure_channel(GRPC_SERVER_LOCATION) as channel:
            stub = pss_pb2_grpc.pssStub(channel)
            request = pss_pb2.ProcessRequest(id=getid())
            stub.process(request)
    except:
        logging.info("Error creating RPC process request ! "
                     "This could be due to some error in proxy. Check /tmp/proxy_log.txt")


def inet_to_str(inet):
    """Convert inet object to a string

    :param inet: inet network address
    :type inet: inet struct
    :return:  str of printable/readable IP address
    """
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)


def str_to_inet(str):
    """Convert string object to an inet

    :param str: printable/readable IP address
    :type str: str
    :return: inet (inet struct) - an inet network address
    """
    try:
        return socket.inet_pton(socket.AF_INET, str)
    except ValueError:
        return socket.inet_pton(socket.AF_INET6, str)


def get_ip_loopback(buf):
    """Unpack the data within the Ethernet frame (the IP packet)

    Pulling out src, dst, length, fragment info, TTL, and Protocol

    :param buf: A string buffer containing the entire packet
    :type buf: str
    :return: ip of type (dpkt.IP)
    """
    lp = Loopback(buf)
    lp.unpack(buf)
    ip = lp.data
    return ip


def get_ip_ethernet(buf):
    """Unpack the data within the Ethernet frame (the IP packet)

    Pulling out src, dst, length, fragment info, TTL, and Protocol

    :param buf: A string buffer containing the entire packet
    :type buf: str
    :return: ip of type (dpkt.IP)
    """
    lp = Ethernet(buf)
    lp.unpack(buf)
    ip = lp.data
    return ip


def get_ip_sll(buf):
    """Unpack the data within the SLL frame (the IP packet)

    Pulling out src, dst, length, fragment info, TTL, and Protocol

    :param buf: A string buffer containing the entire packet
    :type buf: str
    :return: ip of type (dpkt.IP)
    """
    lp = SLL(buf)
    lp.unpack(buf)
    ip = lp.data
    return ip


def get_pkt_src_dst_IP(buf, dl_type=ETH_TYPE_FRAME):
    """Get src and dst IP from raw packet string

    :param buf: A string buffer containing the entire packet
    :type buf: str
    :param dl_type: Link Layer type defined in dpkt.pcap. (Default ETH_TYPE_FRAME)
    :type dl_type: int
    :return: A tuple with source and destination IP strings
    """

    if dl_type == dpkt.pcap.DLT_NULL:
        ip = get_ip_loopback(buf)
    elif dl_type == dpkt.pcap.DLT_LINUX_SLL:
        ip = get_ip_sll(buf)
    else:
        ip = get_ip_ethernet(buf)

    return inet_to_str(ip.src), inet_to_str(ip.dst)


def get_raw_ip_pkt(buf, dl_type=ETH_TYPE_FRAME):
    """Get IP payload from raw packet string

    :param buf: A string buffer containing the entire packet
    :type buf: str
    :param dl_type: Link Layer type defined in dpkt.pcap. (Default ETH_TYPE_FRAME)
    :type dl_type: int
    :return: A string buffer with IP payload
    """

    if dl_type == dpkt.pcap.DLT_NULL:
        ip = get_ip_loopback(buf)
    elif dl_type == dpkt.pcap.DLT_LINUX_SLL:
        ip = get_ip_sll(buf)
    else:
        ip = get_ip_ethernet(buf)

    return ip


def decode_raw_ip_payload_src_dst(buf):
    """Get src,dst ip address from raw ip payload string

    :param buf: A string buffer containing raw ip payload
    :return: A typle with source and destination IP strings
    """
    ip = IP(buf)
    return inet_to_str(ip.src), inet_to_str(ip.dst)
