from pcapfile.protocols.linklayer import ethernet
from pcapfile.protocols.network import ip
import binascii
import dpkt

import socket
from dpkt.loopback import Loopback
from dpkt.ethernet import Ethernet
from dpkt.sll import SLL
from dpkt.ip import IP
from src.proto import pss_pb2

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
SOCKET_TIMEOUT = 5
ETH_TYPE_FRAME = 1


NS = 1
USEC = 1000*NS
MS = 1000*USEC
SEC = 1000*MS
NS_PER_MS = 1000000
NS_PER_SEC = 1000000000

TRAFFIC_FLOW_PERIODIC = 'Periodic'
TRAFFIC_FLOW_EXPONENTIAL = 'Exponential'
TRAFFIC_FLOW_ONE_SHOT = 'OneShot'

# Every network simulated node listens on this port by default for udp pkts from other nodes
DEFAULT_HOST_UDP_PORT = 5100

# 10 characters for holding the length of power sim id. currently only used for power world
POWERSIM_ID_HDR_LEN = 10


 



def extract_powersim_entity_id_from_pkt(pkt):
    pkt_parsed = pss_pb2.PowerSimMessage()
    pkt_parsed.ParseFromString(pkt)
    if pkt_parsed.HasField("read_request"):
        dst_powersim_entity_id = pkt_parsed.read_request.objid
    elif pkt_parsed.HasField("write_request"):
        dst_powersim_entity_id = pkt_parsed.write_request.objid
    elif pkt_parsed.HasField("response"):
        dst_powersim_entity_id = pkt_parsed.response.receiver_attributes.receiver_id
    else:
        assert(False)
    return dst_powersim_entity_id


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
