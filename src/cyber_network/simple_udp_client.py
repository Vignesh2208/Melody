import socket
import sys
import time
import datetime
from datetime import datetime

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


server_address = ('10.0.0.3', 10000)
message = 'Hello World'

while 1:
    try:

        # Send data
        print "TX:" + str(datetime.now()) + 'sending "%s"' % message
        sys.stdout.flush()
        sent = sock.sendto(message, server_address)

        # Receive response
        data, server = sock.recvfrom(4096)
        print "RX:" + str(datetime.now()) + 'received "%s"' % data
        sys.stdout.flush()
        time.sleep(1)

    except socket.error as err:
        print "Socket Error : ", err
        sys.stdout.flush()
        time.sleep(1)
        

