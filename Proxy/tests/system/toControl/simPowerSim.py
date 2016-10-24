import socket
from defines import *

HOST_IP = "127.0.0.1"
HOST_PORT = PROXY_UDP_PORT
MESSAGE = "Hello World!"

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (HOST_IP, HOST_PORT))

print "Power Sim Msg Sent"