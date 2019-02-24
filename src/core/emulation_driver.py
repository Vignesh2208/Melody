"""Emulation Driver

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>, Rakesh Kumar (gopchandani@gmail.com)
"""

import argparse
import json
import datetime
from datetime import datetime
import shared_buffer
from shared_buffer import *
import time
import subprocess


class EmulationDriver(object):
    """An emulation driver is responsible for emulating background flow traffic in the mininet network.

    It is assigned a command to execute and spawned inside a mininet host. It forks a child process and executes
    the assigned command.
    """

    def __init__(self, input_params):
        """Initialization

        :param input_params: A dictionary of input parameters including command to execute and when to start the
                             command.
        :type input_params: dict
        :return None
        """

        self.cmd = input_params["cmd"]
        self.offset = input_params["offset"]
        self.run_time = input_params["run_time"]
        self.driver_id = input_params["driver_id"]
        self.shared_buf_array = shared_buffer_array()
        self.init_shared_buffers(self.driver_id, self.run_time)

    def init_shared_buffers(self, driver_id, run_time):
        """Initialize shared buffers used for communication with the main Melody process

        If the shared buffers cannot be opened successfully, the driver just sleeps for the specified amount of
        run time.

        :param driver_id: A unique id string assigned to this driver. The shared buffer is opened with this ID.
        :type driver_id: str
        :param run_time: Running time of driver in seconds
        :type run_time: int
        :return: None
        """

        result = self.shared_buf_array.open(bufName=str(driver_id) + "-main-cmd-channel-buffer", isProxy=False)
        if result == BUF_NOT_INITIALIZED or result == FAILURE:
            print "Cmd channel buffer open failed!. Not starting any processes !"
            if run_time == 0:
                while True:
                    time.sleep(1)

            time.sleep(run_time)
            sys.exit(0)

        print "Cmd channel buffer open succeeded !"
        sys.stdout.flush()

    def trigger(self):
        """Start executing the assigned command.

        Forks a new process and starts the command.

        :return: None
        """
        if self.cmd == "":
            print "Nothing to execute ..."
            return

        time.sleep(int(self.offset))
        print "Started executing command at ", str(datetime.now())
        sys.stdout.flush()
        try:
            cmd_list = self.cmd.split(' ')
            for arg in cmd_list:
                if arg == '':
                    cmd_list.remove(arg)
            print cmd_list
            sys.stdout.flush()
            subprocess.Popen(cmd_list, shell=False)
        except RuntimeError:
            print "Error running command: ", sys.exec_info()[0]



def main():
    """Main entry point of the emulation_driver

    Creates an emulation driver, initializes it and triggers executing the command at the right time. It also
    handles shutting down the driver.

    :return: None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_params_file_path", dest="input_params_file_path")

    print "Started background flow emulation driver ..."
    sys.stdout.flush()
    args = parser.parse_args()

    with open(args.input_params_file_path) as f:
        input_params = json.load(f)

    d = EmulationDriver(input_params)

    print "Waiting for START command ... "
    sys.stdout.flush()
    recv_msg = ''
    while "START" not in recv_msg:
        dummy_id, recv_msg = d.shared_buf_array.read_until(str(d.driver_id) + "-main-cmd-channel-buffer")

    print "Triggered emulation driver at ", str(datetime.now())
    sys.stdout.flush()
    d.trigger()

    print "Waiting for STOP command ... "
    sys.stdout.flush()
    recv_msg = ''
    while "EXIT" not in recv_msg:
        dummy_id, recv_msg = d.shared_buf_array.read_until(str(d.driver_id) + "-main-cmd-channel-buffer")

    print "Shutting down background flow emulation driver ..."
    sys.stdout.flush()


if __name__ == "__main__":
    main()
