"""Shared Buffer

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>
"""


import ctypes
import sys
import os
import time

import srcs.lib.defines as defines
import shared_buf as sb

class shared_buffer(object):
    """Uses the shared_buffer library defined in srcs/lib/libs

    """
    def __init__(self, bufName, isProxy):

        self.sharedBufName = bufName

        if isProxy:
            self.isProxy = 1
        else:
            self.isProxy = 0

        self.shared_buf = sb
        self.shared_buf.init()

    def open(self):
        """Opens the shared buffer
        """
        result = self.shared_buf.open(self.sharedBufName, self.isProxy)
        return result

    def close(self):
        """Closes the shared buffer
        """
        self.shared_buf.close()

    def read(self):
        """Reads from the shared buffer
        :return: str or None
        """
        ret = self.shared_buf.read(self.sharedBufName, self.isProxy)
        #time.sleep(0.001)
        return ret

    def write(self, msg, dstID=defines.PROXY_NODE_ID):
        """Write message to the shared buffer

        :param msg: message to write
        :type msg: str
        :param dstID: Not used
        """
        return self.shared_buf.write(self.sharedBufName, str(msg),
            len(str(msg)), self.isProxy, dstID)


class shared_buffer_array(object):
    """Can be used to create an array of shared buffers
    """
    def __init__(self):
        self.sharedBufs = []
        self.sharedBufNames = []
        self.shared_buf = sb
        self.shared_buf.init()

    def open(self, bufName, isProxy):
        """Opens a new shared buffer and adds it to the array

        :param bufName: buffer name
        :type bufName: str
        :param isProxy: Specifies if the buffer is opened by the master or slave. 1-Master, 0-Slave
        :type isProxy: int
        :return: None
        """
        if isProxy:
            self.sharedBufs.append((bufName, 1))
        else:
            self.sharedBufs.append((bufName, 0))

        self.sharedBufNames.append(bufName)
        result = self.shared_buf.open(bufName, isProxy)
        return result

    def close(self):
        """Closes all opened shared buffers

        :return: None
        """
        self.shared_buf.close()

    def read(self, bufName):
        """Reads a buffer specified by buffer name. It is Non-Blocking.

        :param bufName: buffer name to read
        :type bufName: str
        :return: str or None if there is nothing to read in the buffer.
        """
        idx = self.sharedBufNames.index(bufName)
        assert (idx >= 0 and idx < len(self.sharedBufNames))
        isProxy = self.sharedBufs[idx][1]

        return self.shared_buf.read(bufName, isProxy)

    def read_until(self, bufName, cool_off_time=0.01):
        """Reads until something appears in the buffer.

        :param bufName: buffer name to read
        :type bufName: str
        :param cool_off_time: time to sleep in secs between two successive reads
        :type cool_off_time: float
        :return: str
        """
        while True:
            id, msg = self.read(bufName)
            if msg != '':
                return id, msg
            time.sleep(cool_off_time)

    def write(self, bufName, msg, dstID=defines.PROXY_NODE_ID):
        """Write a message to the buffer.

        :param bufName: buffer name to write
        :type bufName: str
        :param msg: Message to write
        :type msg: str
        :param dstID: Not used
        :return: number of bytes written (int)
        """
        idx = self.sharedBufNames.index(bufName)
        assert (idx >= 0 and idx < len(self.sharedBufNames))
        isProxy = self.sharedBufs[idx][1]

        return self.shared_buf.write(
            bufName, str(msg), len(str(msg)), isProxy, dstID)
