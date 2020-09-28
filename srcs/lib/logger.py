"""Melody Logger

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>
"""

import sys
import os
import datetime
import logging


class Logger(object):
    """Simple Logger class for logging messages to stdout/log files

    """

    def __init__(self, log_file, tag):
        """Initialization

        :param log_file: Absolute path to log file or "stdout"
        :type log_file: str
        :param tag: A tag which is added to each message
        :type tag: str
        """
        if log_file != "stdout":
            with open(log_file, "w") as f:
                pass
            self.printable = False
        else:
            self.printable = True

        self.log_file = log_file
        self.tag = tag

    def log_msg(self, loglevel, tag, msg):
        """Appends message to file or prints to stdout

        :param loglevel: can be INFO or WARN or ERROR
        :type loglevel: str
        :param tag: a tag added to the message
        :type tag: str
        :param msg: actual message string
        :type msg: str
        :return: None
        """
        if self.printable:
            print (
                f"{str(datetime.datetime.now())} : {str(tag)} >> "
                f"{str(loglevel)} >>  {str(msg)} \n")
        else:
            with open(self.log_file, "a") as f:
                f.write(f"{str(datetime.datetime.now())} : {str(tag)} >> "
                        f"{str(loglevel)} >>  {str(msg)} \n")

    def info(self, msg):
        """Logs a INFO message

        :param msg: actual message string
        :type msg: str
        :return: None
        """
        self.log_msg("INFO", self.tag, msg)

    def warn(self, msg):
        """Logs a WARN message

        :param msg: actual message string
        :type msg: str
        :return: None
        """
        self.log_msg("WARN", self.tag, msg)

    def error(self, msg):
        """Logs a ERROR message

        :param msg: actual message string
        :type msg: str
        :return: None
        """
        self.log_msg("ERROR", self.tag, msg)
