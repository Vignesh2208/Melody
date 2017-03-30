import socket
import sys
import datetime
from datetime import datetime

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('10.0.0.3', 10000)
print 'starting up on %s port %s' % server_address
sys.stdout.flush()
sock.bind(server_address)
while True:
    print '\nwaiting to receive new message at', str(datetime.now())
    sys.stdout.flush()
    
    data = ''
    
    while len(data) == 0:
    
        try:
            data, address = sock.recvfrom(4096)

            #print 'received %s bytes from %s' % (len(data), address)
            #print data
            #sys.stdout.flush()

            if data != None and len(str(data)) > 0:
                sent = sock.sendto(data, address)
                print 'sent %s bytes back to %s' % (sent, address)
                sys.stdout.flush()
                break
        except:
            pass
            

