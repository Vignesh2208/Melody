import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--dest_ip', dest="dest_ip", help='IP Address of the Destination node.', required=True)
args = parser.parse_args()

os.system("curl " + args.dest_ip + ":8000 &")
