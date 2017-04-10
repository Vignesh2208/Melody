import socket
import sys
import argparse
import time
import os
import datetime
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--port', dest="port", nargs='?', default=10000, type=int, help='Port Number')
parser.add_argument('--freq', dest="freq", nargs='?', default=1, type=float, help='Frequency to send packets.')
parser.add_argument('--serv_ip', dest="serv_ip", help='Server IP address.')
args = parser.parse_args()

print "simple_udp_client.py: start script"
sys.stdout.flush()
time.sleep(1)
os.system("taskset -cp " + str(os.getpid()))
#os.nice(-20)

if args.serv_ip:
    serv_ipaddr = args.serv_ip
else:
    serv_ipaddr = '10.0.0.3'      # original hard-coded server value

print "Setup UDP client; server addr: %s, port: %s, freq: %s" % (serv_ipaddr, str(args.port), str(args.freq))

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (serv_ipaddr, args.port)
message = 'Hello World'

i = 1
factorial = 1

while 1:
    try:

        # Send data
        print "TX:" + str(datetime.now()) + 'sending "%s"' % message
        sys.stdout.flush()
        sent = sock.sendto(message, server_address)

        # Receive response
        #data, server = sock.recvfrom(4096)
        #print "RX:" + str(datetime.now()) + 'received "%s"' % data
        sys.stdout.flush()
        time.sleep(args.freq)

        if i < 10000000000 :
            factorial = factorial*i
            i = i + 1
        else:
            i = 1
            factorial = 1

    except socket.error as err:
        print "Socket Error : ", err
        sys.stdout.flush()
        time.sleep(args.freq)
