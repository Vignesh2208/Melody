import socket
import sys
import argparse
import time
import os
import datetime
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--port', dest="port", nargs='?', default=10000, type=int, help='Port Number')
parser.add_argument('--serv_ip', dest="serv_ip", help='Server IP address.')
args = parser.parse_args()

print "simple_udp_server.py: start script"
sys.stdout.flush()
time.sleep(1)
os.system("taskset -cp " + str(os.getpid()))
#os.nice(-20)

if args.serv_ip:
    serv_ip = args.serv_ip
else:
    serv_ip = '10.0.0.3'      # original hard-coded server value

i = 1
factorial = 1

print "Setup UDP server; server addr: %s, port: %s" % (serv_ip, str(args.port))

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = (serv_ip, args.port)
print 'starting up on %s port %s' % server_address
sys.stdout.flush()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setblocking(False)
sock.bind(server_address)
while True:
    print '\nwaiting to receive new message at', str(datetime.now())
    sys.stdout.flush()

    #data = ''

    #while len(data) == 0:

    try:
        if i < 10000000000 :
            factorial = factorial*i
            i = i + 1
        else:
            i = 1
            factorial = 1

        data, address = sock.recvfrom(4096)

            #print 'received %s bytes from %s' % (len(data), address)
            #print data
            #sys.stdout.flush()

    except:
        pass


