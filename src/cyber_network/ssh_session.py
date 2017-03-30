import paramiko
import sys
import telnetlib
import argparse
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument('--dest_ip', dest="dest_ip", help='IP Address of the Destination node.', required=True)
parser.add_argument('--username', dest="username", help='User name for login', required=True)
parser.add_argument('--password', dest="password", help='Password for login', required=True)
args = parser.parse_args()

dest_ip = args.dest_ip
username = args.username
password = args.password

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(hostname=dest_ip,port=22,username=username,password=password)
print "connected"

sys.stdout.flush()
ssh.exec_command('ps -ef')
ssh.close()
print "closed connection"
sys.stdout.flush()
