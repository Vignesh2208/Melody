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

'''
Implementation of PSS Driver for MatPower
Commands are executed indirectly by running simulation.m file using Octave
Changes are accumulated in tmpcase file
Mapping follows the data file format at http://www.pserc.cornell.edu/matpower/manual.pdf
'''
MATPOWERCONST = {"bus":{"bus_i":1, "type":2, "Pd":3, "Qd":4, "Gs":5, "Bs":6, "area":7, "Vm":8, "Va":9, "baseKV":10, "zone":11, "Vmax":12, "Vmin":13},
                 "gen":{"bus":1, "Pg":2, "Qg":3, "Qmax":4, "Qmin":5, "Vg":6, "mBase":7, "status":8, "Pmax":9, "Pmin":10, "Pc1":11, "Pc2":12, "Qc1min":13,
                        "Qc1max":14, "Qc2min":15, "Qc2max":16, "ramp_agc":17, "ramp_10":18, "ramp_30":19, "ramp_q":20, "apf":21},
                 "branch":{"fbus":1, "tbus":2, "r":3, "x":4, "b":5, "rateA":6, "rateB":7, "rateC":8, "ratio":9,	"angle":10, "status":11, "angmin":12, "angmax":13}}


class MatPowerDriver(PSSDriverAbstract):
    def __init__(self, workingdir="."):
        self.workingdir = workingdir
        self.matfile = self.workingdir + "/simulation.m"
        self.case = self.workingdir + "/tmpcase"


    def _run_octave(self, matfile):
        subprocess.check_call(["octave", matfile],
                              stdout=DEVNULL, stderr=subprocess.STDOUT)


    def open(self, case):
        openfile = open(self.matfile, "w")
        openfile.write('''mpc = loadcase('%s');\n'''%case)
        for objtype in MATPOWERCONST.keys():
            openfile.write('''csvwrite("%s/%s.csv", mpc.%s);'''%(self.workingdir, objtype, objtype))
        openfile.write('''savecase('%s', mpc);\n'''%self.case)
        openfile.close()

        self._run_octave(self.matfile)
        
        
    def write(self, objtype, objid, fieldtype, value):
        openfile = open(self.matfile, "w")
        openfile.write('''mpc = loadcase('%s');\n'''%self.case)
        assert(objtype in MATPOWERCONST)
        assert(fieldtype in MATPOWERCONST[objtype])
        if objtype in ["gen", "bus"]:
            openfile.write('''mpc.%s(find(mpc.%s(:,1)==%s),%d) = %s;\n'''%(objtype, objtype, objid, MATPOWERCONST[objtype][fieldtype], value))

        #TODO: implement branch
            
        openfile.write('''savecase('%s', mpc);\n'''%self.case)
        openfile.close()

        self._run_octave(self.matfile)


    def write_multiple(self, writelist):
        openfile = open(self.matfile, "w")
        openfile.write('''mpc = loadcase('%s');\n'''%self.case)

        for objtype, objid, fieldtype, value in writelist:
            assert(objtype in MATPOWERCONST)
            assert(fieldtype in MATPOWERCONST[objtype])
            if objtype in ["gen", "bus"]:
                openfile.write('''mpc.%s(find(mpc.%s(:,1)==%s),%d) = %s;\n'''%(objtype, objtype, objid, MATPOWERCONST[objtype][fieldtype], value))
                
        #TODO: implement branch

        openfile.write('''savecase('%s', mpc);\n'''%self.case)
        openfile.close()

        self._run_octave(self.matfile)


    def run_pf(self, method=None):
        openfile = open(self.matfile, "w")
        openfile.write('''mpc = loadcase('%s');\n'''%self.case)        
        openfile.write('''result = runpf(mpc);\n''')
        for objtype in MATPOWERCONST.keys():
            openfile.write('''csvwrite("%s/%s.csv", result.%s);'''%(self.workingdir, objtype, objtype))
        openfile.close()

        self._run_octave(self.matfile)

    
    def read(self, objtype, objid, fieldtype):
        assert(objtype in MATPOWERCONST)
        assert(fieldtype in MATPOWERCONST[objtype])

        if objtype in ["bus", "gen"]:
            data = np.genfromtxt("%s/%s.csv"%(self.workingdir, objtype), delimiter=',')
            for d in data:
                if int(d[0]) == int(objid):
                    return str(d[MATPOWERCONST[objtype][fieldtype]-1])
        
        return None

    
    def close(self):
        return


    def save(self, newcase):
        openfile = open(self.matfile, "w")
        openfile.write('''mpc = loadcase('%s');\n'''%self.case)
        openfile.write('''savecase('%s', mpc);\n'''%newcase)
        openfile.close()
        
        self._run_octave(self.matfile)
