import dpkt
import grpc
import sys
import time
import random
import socket

from dpkt.loopback import Loopback
from dpkt.ethernet import Ethernet
from dpkt.sll import SLL
from dpkt.ip import IP
from src.proto import pss_pb2
from src.proto import pss_pb2_grpc


# Error Defines
SUCCESS = 1
FAILURE = 0
IS_SHARED = 1
BUF_NOT_INITIALIZED = -1
TEMP_ERROR = -2

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

TRAFFIC_FLOW_PERIODIC = 'Periodic'
TRAFFIC_FLOW_EXPONENTIAL = 'Exponential'
TRAFFIC_FLOW_ONE_SHOT = 'OneShot'

# Every network simulated node listens on this port by default for udp pkts from other nodes
DEFAULT_HOST_UDP_PORT = 5100

# 10 characters for holding the length of power sim id. currently only used for power world
POWERSIM_ID_HDR_LEN = 10



def getid():
    return str(hash(time.time() + random.random()))

def rpc_read(readlist):

    try:
        channel = grpc.insecure_channel(GRPC_SERVER_LOCATION)
        stub = pss_pb2_grpc.pssStub(channel)
        readRequest = pss_pb2.ReadRequest(timestamp=time.time())

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
        return [response[id] for id in xrange(0,counter)]
    except:
        print "Error in creating RPC read request ..."
        sys.stdout.flush()
        return None


def rpc_write(writelist):

    try:
        channel = grpc.insecure_channel(GRPC_SERVER_LOCATION)
        stub = pss_pb2_grpc.pssStub(channel)
        writeRequest = pss_pb2.WriteRequest(timestamp=time.time())

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
        return [status[id] for id in xrange(0, counter)]
    except:
        print "Error in creating RPC write request ..."
        sys.stdout.flush()
        return None




def inet_to_str(inet):
    """Convert inet object to a string
        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)


def str_to_inet(str):
    """Convert string object to an inet
        Args:
            str: Printable/readable IP address
        Returns:
            inet (inet struct): inet network address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_pton(socket.AF_INET, str)
    except ValueError:
        return socket.inet_pton(socket.AF_INET6, str)


def get_ip_loopback(buf):
    # Unpack the data within the Ethernet frame (the IP packet)
    # Pulling out src, dst, length, fragment info, TTL, and Protocol
    lp = Loopback(buf)
    lp.unpack(buf)
    ip = lp.data
    return ip


def get_ip_ethernet(buf):
    lp = Ethernet(buf)
    lp.unpack(buf)
    ip = lp.data
    return ip


def get_ip_sll(buf):
    lp = SLL(buf)
    lp.unpack(buf)
    ip = lp.data
    return ip


def get_pkt_src_dst_IP(buf, DL_TYPE=ETH_TYPE_FRAME):
    """
    :param buf: A string buffer containing the entire packet
    :return: A tuple with source and destination IP strings
    """

    if DL_TYPE == dpkt.pcap.DLT_NULL:
        ip = get_ip_loopback(buf)
    elif DL_TYPE == dpkt.pcap.DLT_LINUX_SLL:
        ip = get_ip_sll(buf)
    else:
        ip = get_ip_ethernet(buf)

    return inet_to_str(ip.src), inet_to_str(ip.dst)


def get_raw_ip_pkt(buf, DL_TYPE=ETH_TYPE_FRAME):
    """
    :param buf: A string buffer containing the entire packet
    :return: A string buffer with IP payload
    """

    if DL_TYPE == dpkt.pcap.DLT_NULL:
        ip = get_ip_loopback(buf)
    elif DL_TYPE == dpkt.pcap.DLT_LINUX_SLL:
        ip = get_ip_sll(buf)
    else:
        ip = get_ip_ethernet(buf)

    return ip


def decode_raw_ip_payload_src_dst(buf):
    ip = IP(buf)
    return inet_to_str(ip.src), inet_to_str(ip.dst)



def is_pkt_from_attack_dispatcher(pkt_str):
    if pkt_str[0] == "1":
        return True
    else:
        return False
