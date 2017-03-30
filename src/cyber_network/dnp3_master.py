from utils.sleep_functions import sleep
import sys
import argparse
import os

# import opendnp3 instead of from opendnp3 import *
# In DataObserver._Update, there is a serious of ifs
# which check the type of a point (if (t == opendnp3.Binary)).
# It was causing a SWIG director method exception to be thrown
# when the ifs were written if (t == Binary).
import opendnp3

binary_list = []
analog_list = []
counter_list = []
controlstatus_list = []
setpointstatus_list =[]

class StackObserver(opendnp3.IStackObserver):
	def __init__(self):
		super(StackObserver, self).__init__()

	def OnStateChange(self, change):
		print('The stack state has changed: %s' % opendnp3.ConvertStackStateToString(change))

class DataObserver(opendnp3.IDataObserver):
	def __init__(self):
		# call the IDataObserver class's init function
		super(DataObserver, self).__init__()
		self.newData = False

	def Load(self, point, point_map, index):
		if (len(point_map) <= index):
			point_map.append([])

		point_map[index] = point

	# this implements the following virtual functions in the IDataObserver class
	# virtual void _Update(const Binary& arPoint, size_t) = 0;
	# virtual void _Update(const Analog& arPoint, size_t) = 0;
	# virtual void _Update(const Counter& arPoint, size_t) = 0;
	# virtual void _Update(const ControlStatus& arPoint, size_t) = 0;
	# virtual void _Update(const SetpointStatus& arPoint, size_t) = 0;
	def _Update(self, point, index):
		self.newData = True
		t = type(point)

		if (t == opendnp3.Binary):
			print("Update Binary %d: %d" % (index, point.GetValue()))
			self.Load(point, binary_list, index)
		elif (t == opendnp3.Analog):
			print("Update Analog %d: %d" % (index, point.GetValue()))
			self.Load(point, analog_list, index)
		elif (t == opendnp3.Counter):
			print("Update Counter %d: %d" % (index, point.GetValue()))
			self.Load(point, counter_list, index)
		elif (t == opendnp3.ControlStatus):
			print("Update ControlStatus %d: %d" % (index, point.GetValue()))
			self.Load(point, controlstatus_list, index)
		elif (t == opendnp3.SetpointStatus):
			print("Update SetpointStatus %d: %d" % (index, point.GetValue()))
			self.Load(point, setpointstatus_list, index)

	# this implements a virtual function in the ITransactable class
	# virtual void _Start() = 0;
	def _Start(self):
		# nothing to do
		print('Start')
		sys.stdout.flush()

	# this implements a virtual function in the ITransactable class
	# virtual void _End() = 0;
	def _End(self):
		print('End')
		self.newData = False
		print('Start')
		sys.stdout.flush()

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--slave_ip', dest="slave_ip", help='IP Address of the slave node.', required=True)
	args = parser.parse_args()
    
	# 1. Extend IDataObserver and IStackObserver
	# 2. Add a Physical Layer (TCP Client) to the StackManager
	# 3. Create a MasterConfig.
	# 4. Add a Master Stack to the StackManager
	# 5. Let the process run
	
	print "Running the Master. Pid = ", os.getpid()
	sys.stdout.flush()
	
	stack_observer = StackObserver()
	observer = DataObserver()

	phys_layer_settings = opendnp3.PhysLayerSettings()
	
	#opendnp3.ClassMask.class1 = True
	
	stack_manager = opendnp3.StackManager()
	stack_manager.AddTCPClient('tcpclient', phys_layer_settings, args.slave_ip, 20000)
	master_stack_config = opendnp3.MasterStackConfig()
	master_stack_config.master.DoUnsolOnStartup = True

	master_stack_config.link.LocalAddr = 100
	master_stack_config.link.RemoteAddr = 1
    #master_stack_config.link.useConfirms = True

	# set the stack observer callback to our Python-extended class
	master_stack_config.master.mpObserver = stack_observer
	
	# the integrity rate is the # of milliseconds between integrity scans
	master_stack_config.master.IntegrityRate = 100
	#master_stack_config.master.TaskRetryRate = 10
	print master_stack_config.master.IntegrityRate
	sys.stdout.flush()
	
	#master_stack_config.master.UnsolClassMask = opendnp3.IntToPointClass(1)
	#print master_stack_config.master.TaskRetryRate 
	# The third argument needs to be a log FilterLevel.  The Python
	# API does not have access to this enum, but it can be "fed" to
	# the AddMaster method because the PhysLayerSettings LogLevel
	# member is a FilterLevel enum.
	command_acceptor = stack_manager.AddMaster('tcpclient', 'master', phys_layer_settings.LogLevel, observer, master_stack_config)
	# Need to wait because the polling is now occurring on its own
	# thread.  If we exited immediately, the callbacks would never
	# be called.
	sleep(2)

	print('Binaries: %d' % (len(binary_list)))
	print('Analogs: %d' % (len(analog_list)))
	print('Counters: %d' % (len(counter_list)))
	print('ControlStatus: %d' % (len(controlstatus_list)))
	print('Setpointstatus: %d' % (len(setpointstatus_list)))
	sys.stdout.flush()

	while (True):
		sleep(10)
		break

if __name__ == '__main__':
	main()
