from __future__ import division
from abc import ABCMeta, abstractmethod
import subprocess
import os
import numpy as np


DEVNULL = open(os.devnull, 'wb')


class PSSDriverAbstract:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__():
        pass

    @abstractmethod
    def open(self):
        pass
    
    @abstractmethod
    def read(self, case):
        pass
    
    @abstractmethod
    def write(self, objtype, objid, fieldtype, value):
        pass

    @abstractmethod
    def write_multiple(self, writelist):
        pass

    @abstractmethod
    def run_pf(self, method=None):
        pass

    
    @abstractmethod
    def save(self, newcase):
        pass

    
    @abstractmethod
    def close(self):
        pass


class MatPowerDriver(PSSDriverAbstract):
    def __init__(self, workingdir):
        self.workingdir = workingdir
        self.matfile = workingdir + "/simulation.m"
        self.case = workingdir + "/tmpcase"


    def _run_octave(self, matfile):
        subprocess.check_call(["octave", matfile],
                              stdout=DEVNULL, stderr=subprocess.STDOUT)


    def open(self, case):
        openfile = open(self.matfile, "w")
        openfile.write('''mpc = loadcase('%s');\n'''%case)
        openfile.write('''csvwrite("%s/bus.csv", mpc.bus);\n'''%self.workingdir)
        openfile.write('''savecase('%s', mpc);\n'''%self.case)
        openfile.close()

        self._run_octave(self.matfile)
        
        
    def write(self, objtype, objid, fieldtype, value):
        openfile = open(self.matfile, "w")
        openfile.write('''mpc = loadcase('%s');\n'''%self.case)
        if objtype == "gen" and fieldtype == "v":
            openfile.write('''mpc.gen(find(mpc.gen(:,1)==%s),6) = %s;\n'''%(objid, value))
        openfile.write('''savecase('%s', mpc);\n'''%self.case)
        openfile.close()

        self._run_octave(self.matfile)


    def write_multiple(self, writelist):
        openfile = open(self.matfile, "w")
        openfile.write('''mpc = loadcase('%s');\n'''%self.case)
        for objtype, objid, fieldtype, value in writelist:
            if objtype == "gen" and fieldtype == "v":
                openfile.write('''mpc.gen(find(mpc.gen(:,1)==%s),6) = %s;\n'''%(objid, value))
        openfile.write('''savecase('%s', mpc);\n'''%self.case)
        openfile.close()

        self._run_octave(self.matfile)


    def run_pf(self, method=None):
        openfile = open(self.matfile, "w")
        openfile.write('''mpc = loadcase('%s');\n'''%self.case)        
        openfile.write('''result = runpf(mpc);\n''')
        openfile.write('''csvwrite("%s/bus.csv", result.bus);'''%self.workingdir)
        openfile.close()

        self._run_octave(self.matfile)

    
    def read(self, objtype, objid, fieldtype):
        if objtype == "bus" and fieldtype == "v":
            data = np.genfromtxt("%s/bus.csv"%self.workingdir, delimiter=',')
            for d in data:
                if int(d[0]) == int(objid):
                    return str(d[7])


    def close(self):
        pass


    def save(self, newcase):
        openfile = open(self.matfile, "w")
        openfile.write('''mpc = loadcase('%s');\n'''%self.case)
        openfile.write('''savecase('%s', mpc);\n'''%newcase)
        openfile.close()
        
        self._run_octave(self.matfile)
