"""Ryu controller management

.. moduleauthor:: Rakesh Kumar (gopchandani@gmail.com)
"""

import subprocess
import os
import time


class ControllerMan(object):
    def __init__(self,  controller):
        self.controller = controller

        if controller == "ryu":
            self.ryu_proc = None

        elif controller == "sel":
            pass

    def get_next_ryu(self):

        os.system("sudo killall ryu-manager")
        os.system("sudo fuser -k 8080/tcp")
        os.system("sudo fuser -k 8081/tcp")
        os.system("sudo fuser -k 6633/tcp")
        ryu_cmd = ["ryu-manager", "--observe-links",
                   "ryu.app.ofctl_rest", "ryu.app.rest_topology"]

        with open("/tmp/ryu_stdout.txt", "wb") as out, open("/tmp/ryu_stderr.txt", "wb") as err:
            self.ryu_proc = subprocess.Popen(ryu_cmd, stderr=err, stdout=out)
        print ("Starting ryu-manager ...")
        print ("Waiting 5 secs ...")
        time.sleep(5.0)

        return 6633

    def start_controller(self):
        if self.controller == "odl":
            raise NotImplementedError
        elif self.controller == "sel":
            pass
        elif self.controller == "ryu":
            return self.get_next_ryu()

    def stop_controller(self):

        if self.controller == "ryu":
            self.ryu_proc.kill()
            subprocess.Popen.wait(self.ryu_proc)
        elif self.controller == "sel":
            pass
        else:
            raise NotImplementedError


