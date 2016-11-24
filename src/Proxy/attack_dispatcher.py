import sys
import os
from pcapfile import savefile
import fnmatch

scriptDir = os.path.dirname(os.path.realpath(__file__))
if scriptDir not in sys.path:
	sys.path.append(scriptDir)

srcDir = scriptDir + "/.."
if srcDir not in sys.path:
	sys.path.append(srcDir)

from logger import *
import time
import getopt
import socket
from defines import *

def extractIPMapping(netCfgFile) :
	IPMapping = {}
	PowerSimIdMapping = {}
	IPToHostMapping = {}
	assert(os.path.isfile(netCfgFile) == True)
	lines = [line.rstrip('\n') for line in open(netCfgFile)]

	for line in lines:
		line = ' '.join(line.split())
		line = line.replace(" ","")
		splitLs = line.split(',')
		assert(len(splitLs) >= 3)
		hostID = int(splitLs[0][1:])
		IPAddr = splitLs[1]
		Port = int(splitLs[2])

		IPMapping[hostID] = (IPAddr,Port)
		IPToHostMapping[IPAddr] = hostID
		for i in xrange(3, len(splitLs)):
			PowerSimId = str(splitLs[i])
			if hostID not in PowerSimIdMapping.keys():
				PowerSimIdMapping[hostID] = []
			PowerSimIdMapping[hostID].append(PowerSimId)

	return IPMapping,PowerSimIdMapping,IPToHostMapping

def usage() :
	print "python attack_dispatcher.py <options>"
	print "Options:"
	print "-h or --help"
	print "-c or --pcap-file-dir=    Absolute path to directory containing pcap replay files <required>"
	print "-l or --netcfg-file=     Absolute path to netcfg File <required>"
	print "-r or --run-time=    Run time of host in seconds before it is shut-down <optional - default forever>"
	print "-p or --proxy-ip=     IP Address of proxy <optional - default 127.0.0.1>"

	sys.exit(0)

def parseOpts() :


	netcfgFile = None
	runTime = 0
	proxyIP=DEFAULT_PROXY_IP
	pcapsDirPath = "/home/ubuntu/Desktop/Workspace/NetPower_TestBed"


	try:
		(opts, args) = getopt.getopt(sys.argv[1:],
			"hc:l:r:p:",
			[ "help", "pcap-file-dir=", "netcfg-file=", "run-time=","proxy-ip="])
	except getopt.GetoptError as e:
		print (str(e))
		usage()
		return 1
	for (o, v) in opts:
		if o in ("-h", "--help"):
			usage()

		if o in ("-c", "--pcap-file-dir=") :
			pcapsDirPath = str(v)
		if o in ("-l", "--netcfg-file=") :
			netcfgFile = str(v)
		if o in ("-r", "--run-time=") :
			runTime = int(v)

		if o in ("-p", "--proxy-ip=") :
			proxyIP = str(v)


	assert(pcapsDirPath != None)
	return (pcapsDirPath,netcfgFile,runTime,proxyIP)



def main(pcapsDirPath,netcfgFile,runTime,proxyIP):
	assert os.path.exists(pcapsDirPath)

	replay_pcaps = fnmatch.filter(os.listdir(pcapsDirPath), 'replay*.pcap')
	replay_pcaps = sorted(replay_pcaps)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	IPMapping, PowerSimIdMapping, IPToHostMapping = extractIPMapping(netcfgFile)
	start_time = time.time()
	for replay_pcap_f_name in replay_pcaps :
		pcapFilePath = pcapsDirPath + "/" + replay_pcap_f_name
		assert os.path.isfile(pcapFilePath)
		replay_pcap = open(pcapFilePath,'rb')
		pcap_file = savefile.load_savefile(replay_pcap,verbose=True)

		print "Current Replay file = ", replay_pcap_f_name
		nPackets = len(pcap_file.packets)
		idx = 0

		while idx < nPackets :
			if time.time() - start_time >= runTime :
				sock.close()
				sys.exit(0)

			curr_pkt = pcap_file.packets[idx]
			src_ip, dst_ip = get_pkt_src_dst_IP(curr_pkt)
			raw_ip_pkt = get_raw_ip_pkt(curr_pkt)


			try :
				hostID = IPToHostMapping[src_ip]
				powerSimNodeID = PowerSimIdMapping[hostID][0]
				powerSimNodeIDLen = str(len(powerSimNodeID))

				txpktpad = "1" + powerSimNodeIDLen.zfill(POWERSIM_ID_HDR_LEN-1) + powerSimNodeID
				txpkt = txpktpad + raw_ip_pkt


			except Exception as e:
				print "Error in resolving pkt no: ", idx, " Error = ", str(e), " File - ", replay_pcap_f_name
				sock.close()
				sys.exit(0)

			print "Dispatching Attack pkt no = ", idx, " Len = ", len(txpkt)
			if idx == 0 :
				sock.sendto(txpkt,(proxyIP,PROXY_UDP_PORT))
			else :
				#sleep_time = curr_pkt.timestamp - pcap_file.packets[idx-1].timestamp
				sleep_time = 0.1
				time.sleep(sleep_time)
				sock.sendto(txpkt,(proxyIP,PROXY_UDP_PORT))

			idx = idx + 1








if __name__ == "__main__":

	pcapFilePath,netcfgFile,runTime,proxyIP = parseOpts()
	sys.exit(main(pcapFilePath,netcfgFile,runTime,proxyIP))

