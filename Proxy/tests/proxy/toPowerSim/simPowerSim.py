import socket
from defines import *

HOST_IP = "127.0.0.1"
HOST_PORT = POWERSIM_UDP_PORT 


sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.bind((HOST_IP, HOST_PORT))

print "Waiting for data from Proxy ..."
data, addr = sock.recvfrom(MAXPKTSIZE)

if len(data) > 0 :
	assert(data == "Hello World!")
	print "POWER SIM TEST SUCCEEDED"