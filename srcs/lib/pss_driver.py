"""Drivers for interacting with power system simulator.

.. moduleauthor:: Hoang Hai Nguyen <nhh311@gmail.com>
"""


from __future__ import division
from abc import ABCMeta, abstractmethod


class PSSDriverAbstract:
    '''Abstract class for implementing power system simulation-specific driver.
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
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

