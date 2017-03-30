import sys
import telnetlib
import argparse
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument('--dest_ip', dest="dest_ip", help='IP Address of the Destination node.', required=True)
args = parser.parse_args()

dest_ip = args.dest_ip
username = "ubuntu"
password = "ubuntu"

tn = telnetlib.Telnet(dest_ip)
tn.expect(["login: "])
print "Got login prompt"
sys.stdout.flush()
tn.write(username + "\n")

if password :
    tn.expect(["Password: "])
    tn.write(password + "\n")

print "Sent password"
sys.stdout.flush()

i = 0
while i < 2 :
    time.sleep(1)
    tn.write("echo \'Hello\'\n")
    i = i + 1

tn.write("exit\n")
print tn.read_all()
sys.stdout.flush()