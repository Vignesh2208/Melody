import sys
import os
import threading
import Proxy.shared_buffer
from Proxy.shared_buffer import *
import Proxy.logger
from Proxy.logger import Logger
from Proxy.defines import *
from Proxy.basicHostIPCLayer import basicHostIPCLayer
from datetime import datetime
import time
import threading
import numpy as np


BUS_PUVOLT = {1:1.05178, 2:1.05987, 3:1.05655, 4:1.05919, 5:1.07359, 6:1.07428, 7:1.06115, 8:1.05858, 9:1.05402, 10:1.06106, 11:1.06429, 12:1.04934, 13:1.0587, 14:1.05614, 15:1.04089, 16:1.04853, 17:1.05174, 18:1.05233, 19:1.05599, 20:0.99422, 21:1.04355, 22:1.05611, 23:1.05132, 24:1.05258, 25:1.06582, 26:1.06229, 27:1.05173, 28:1.05541, 29:1.05357, 30:1.0475, 31:0.982, 32:0.9831, 33:0.9972, 34:1.0123, 35:1.0493, 36:1.0635, 37:1.0278, 38:1.0265, 39:1.03}
BUS_PILOT = sorted([2, 25, 29, 22, 23, 19, 20, 10, 6, 9])
LOAD_PQ = {(1,1):[0,0], (2,1):[0,0], (3,1):[322,2.4], (4,1):[500,184], (5,1):[0,0], (6,1):[0,0], (7,1):[233.8,84], (8,1):[522,176], (9,1):[0,0], (10,1):[0,0], (11,1):[0,0], (12,1):[7.5,88], (13,1):[0,0], (14,1):[0,0], (15,1):[320,153], (16,1):[329.4,32.3], (17,1):[0,0], (18,1):[158,30], (19,1):[0,0], (20,1):[680,103], (21,1):[274,115], (22,1):[0,0], (23,1):[247.5,84.6], (24,1):[308.6,-92.2], (25,1):[224,47.2], (26,1):[139,17], (27,1):[281,75.5], (28,1):[206,27.6], (29,1):[283.5,26.9], (31,1):[9.2,4.6], (39,1):[1104,250]}
GEN_PQ = {(30,1):[250.00,83.21], (31,1):[571.28,363.94], (32,1):[650.00,1.53], (33,1):[632.00,69.67], (34,1):[508.00,148.79], (35,1):[650.00,167.04], (36,1):[560.00,75.45], (37,1):[540.00,-35.35], (38,1):[830.00,-0.47], (39,1):[1000.00,-36.49]}
GEN_VOLTSP = {(30,1):1.0475, (31,1):0.982, (32,1):0.9831, (33,1):0.9972, (34,1):1.0123, (35,1):1.0493, (36,1):1.0635, (37,1):1.0278, (38,1):1.0265, (39,1):1.03}
Cpi = [[-3.8773794215,0.0462540353881,0.445488948511,0.114291503294,0.0964938227626,0.000228768247043,0.0698135636183,0.0458320468673,2.12081894333,0.0434895541706],
	   [0.23232599992,-3.6353931953,0.48077845388,2.05228195435,0.0738840197362,4.90437262095e-05,0.0528006061824,0.035753719451,0.0235538390242,0.0208466889431],
	   [0.133951139264,2.0302054979,0.0100225558525,-3.31592713204,0.115409712677,-3.1310000084e-05,0.0828596153908,0.0553852793093,0.0216527408272,0.0216368454497],
	   [0.0765360790559,0.0514599557642,0.00165833838361,0.0810811524812,-2.41723595394,1.02883504435,0.170930120667,0.113684173071,0.0350620896157,0.0356950749758],
	   [-0.000223264489512,0.000108037925461,6.29763988968e-05,-0.000108717524421,1.23266439776,-2.2592240397,-5.73779874521e-05,8.05088304276e-05,0.000152697446854,-9.71901451773e-05],
	   [0.053046665699,0.0359564489148,0.00118456768191,0.0563897535513,0.165619062729,-7.674351445e-05,-2.88178830758,1.60312845204,0.0246418372274,0.0248226288376],
	   [0.0647688459332,0.0439530217828,0.00140668498066,0.0689699197932,0.202793050063,-0.000206649925966,2.95212854059,-4.29700348961,0.0302901085438,0.0303798908043],
	   [2.63531932239,0.0190176947099,0.00243240651324,0.0227398912835,0.0522095945107,-0.000183142665783,0.0369274352688,0.0254188791184,-4.00858947923,0.280425040197],
	   [0.0317519875761,0.0150091390103,0.000322322739098,0.0156328365561,0.0372465827379,-0.000173567000534,0.0267990267543,0.0174782058509,0.190217271289,-1.22608812648],
	   [0.00799680557114,0.565846838902,-1.55752219055,0.0119803456199,0.00266238499839,4.47020176694e-06,0.00187523863478,0.00129301319772,0.00134282654644,0.000764772696896]]
GEN_ID = sorted(GEN_PQ.keys())
GEN_NO = len(GEN_ID)
LOAD_ID = sorted(LOAD_PQ.keys())
LOAD_NO = len(LOAD_ID)


def loadObjectBinary(filename):
	with open(filename, "rb") as input:
		obj = pickle.load(input)
	return obj


class controlLoopThread(threading.Thread) :
	def __init__(self,controlLayer) :
		self.controlLayer = controlLayer
		threading.Thread.__init__(self)
		
		self.vg = np.array([GEN_VOLTSP[gid] for gid in GEN_ID])
		self.vp0 = np.array([BUS_PUVOLT[p] for p in BUS_PILOT])
		self.Cpi = np.matrix(Cpi, dtype="float")
		self.alpha = 0.5

	def run(self) :
		while True:
			self.controlLayer.stoppingLock.acquire()
			if self.controlLayer.stopping:
				self.controlLayer.stoppingLock.release()
				break
			self.controlLayer.stoppingLock.release()
			
			u = np.dot(self.Cpi, self.alpha * (self.vp0 - self.controlLayer.vp)).A1 # 1-d base array
			u *= -1
			self.vg = np.array(self.vg + u)
			for i in range(GEN_NO):
				busnum, gid, voltsp = GEN_ID[i][0], GEN_ID[i][1], self.vg[i]
				#self.controlLayer.txPktToPowerSim("%d;%d"%(busnum,gid), str(voltsp))
			# self.controlLayer.txPktToPowerSim("2","HelloWorld!")
			time.sleep(0.5)

			
class hostControlLayer(basicHostIPCLayer) :

	def __init__(self,hostID,logFile,sharedBufferArray) :
		basicHostIPCLayer.__init__(self,hostID,logFile,sharedBufferArray)
		self.stoppingLock = threading.Lock()
		self.vp = np.array([BUS_PUVOLT[p] for p in BUS_PILOT])

	# Returns the set of power sim node Ids [list of strings] that
	# are mapped to the given cyber node (int). It returns None if the
	# mapping does not exist.
	def getPowerSimIDsforNode(self, cyberNodeID):
		return basicHostIPCLayer.getPowerSimIDsforNode(self,cyberNodeID)

	# Returns the cyber node id (int) when given a power sim node id (string)
	# If the mapping does not exist, it returns None
	def getCyberNodeIDforNode(self, powerSimNodeID):
		return basicHostIPCLayer.getCyberNodeIDforNode(self,powerSimNodeID)


	# Returns the power sim id present in the pkt (string)
	def extractPowerSimIdFromPkt(self, pkt):
		return basicHostIPCLayer.extractPowerSimIdFromPkt(self,pkt)

	# Returns the payload present in the pkt (string)
	def extractPayloadFromPkt(self, pkt):
		return basicHostIPCLayer.extractPayloadFromPkt(self,pkt)


	# transmits to power simulator 
	# Arguments:
	# 	powerSimNodeID (string)
	#   payload (string)
	def txPktToPowerSim(self,powerSimNodeID,payload) :
		return basicHostIPCLayer.txPktToPowerSim(self,powerSimNodeID,payload)


	# Callback on each received pkt from Attack layer.
	# Arguments:
	#   pkt - full pkt including powerSimID(string)
	def onRxPktFromAttackLayer(self,pkt):
		# process the pkt here
		try:

			idlen = int(pkt[:10])
			busnum = int(pkt[10:10+idlen])
			buspuvolt = float(pkt[10+idlen:])
			self.vp[BUS_PILOT.index(busnum)] = buspuvolt
		except Exception as e:
			pass

		return None

	def run(self):
		self.log.info("Started control layer run")
		self.control_loop_thread = controlLoopThread(self)
		self.control_loop_thread_running = False
		self.stopping = False
		assert(self.attackLayer != None)

		while True :
			currCmd = self.getcurrCmd()
			if currCmd != None and currCmd == CMD_QUIT :
				self.stoppingLock.acquire()
				self.stopping = True
				self.stoppingLock.release()

				self.control_loop_thread.join()
				self.log.info("Stopping ...")
				break

			callbackFns = []
			self.threadCallbackLock.acquire()
			if self.nPendingCallbacks == 0:
				self.threadCallbackLock.release()
			else:

				values = list(self.threadCallbackQueue.values())
				for i in xrange(0, len(values)):
					if len(values[i]) > 0:
						callbackFns.append(values[i].pop())
				self.nPendingCallbacks = 0
				self.threadCallbackLock.release()

				for i in xrange(0, len(callbackFns)):
					function, args = callbackFns[i]
					function(*args)

			self.idle()


		
	
	# Could be modified to implement specific control algorithms
	# Function called repeatedly
	def idle(self) :
		# Put control logic here
		if not self.control_loop_thread_running:
			self.control_loop_thread.start()
			self.control_loop_thread_running = True


		else:
			recvPkt = ""
			dstCyberNodeID, recvPkt = self.sharedBufferArray.read(self.sharedBufName)

			if len(recvPkt) != 0:
				self.log.info("Received pkt: " + str(recvPkt) + " from Proxy for Dst Node Id =  " + str(dstCyberNodeID))
				self.onRxPktFromProxy(recvPkt, dstCyberNodeID)








