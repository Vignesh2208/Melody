from pcapfile.protocols.linklayer import ethernet
from pcapfile.protocols.network import ip
import binascii

# Error Defines
SUCCESS  = 1
FAILURE = 0
IS_SHARED = 1
BUF_NOT_INITIALIZED = -1
TEMP_ERROR = -2

# Other Defines
PROXY_NODE_ID = 0
CMD_QUIT = 1
MAXPKTSIZE  = 1000
SOCKET_TIMEOUT = 5



PROXY_UDP_PORT = 9999         #Proxy listens on this port for udp pkts from PowerSim
POWERSIM_UDP_PORT = 9998      #Power Simulator listens on this port for udp pkts from Proxy
DEFAULT_HOST_UDP_PORT = 5100  #Every network simulated node listens on this port by default for udp pkts from other nodes
DEFAULT_POWERSIM_IP = "127.0.0.1"
DEFAULT_PROXY_IP = "127.0.0.1"
POWERSIM_TYPE = "POWER_WORLD" # POWER_WORLD/RTDS
POWERSIM_ID_HDR_LEN = 10      # 10 characters for holding the length of power sim id. currently only used for power world


def extractPowerSimIdFromPkt(pkt):

	powerSimID = "test"
	if POWERSIM_TYPE == "POWER_WORLD":
		#print "Extract Power Sim ID, pkt = ", pkt
		powerSimIDLen = int(pkt[1:POWERSIM_ID_HDR_LEN])

		powerSimID = str(pkt[POWERSIM_ID_HDR_LEN:POWERSIM_ID_HDR_LEN + powerSimIDLen])

	return powerSimID

def print_pkt_info(pkt) :
	eth_frame = ethernet.Ethernet(pkt.raw())
	ip_packet = ip.IP(binascii.unhexlify(eth_frame.payload))

	print "Raw Pkt = ", pkt.raw()
	print "TimeStamp = ", pkt.timestamp
	print "Eth frame = ", eth_frame
	print "Eth src = ", eth_frame.src
	print "Eth dst = ", eth_frame.dst
	print "IP packet = ", ip_packet
	print "IP source = ", ip_packet.src
	print "IP dst = ", ip_packet.dst
	print "IP Payload = ", ip_packet.payload

def get_pkt_src_dst_IP(pkt):
	eth_frame = ethernet.Ethernet(pkt.raw())
	ip_packet = ip.IP(binascii.unhexlify(eth_frame.payload))

	return str(ip_packet.src),str(ip_packet.dst)

def get_raw_ip_pkt(pkt) :
	eth_frame = ethernet.Ethernet(pkt.raw())
	ip_packet = ip.IP(binascii.unhexlify(eth_frame.payload))
	return eth_frame.payload

def decode_raw_ip_payload_src_dst(pkt_str) :
	ip_packet = ip.IP(binascii.unhexlify(pkt_str))
	return ip_packet.src, ip_packet.dst

def is_pkt_from_attack_dispatcher(pkt_str):
	if pkt_str[0] == "1":
		return True
	else :
		return False
