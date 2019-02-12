import sys
import os
import datetime


class Logger(object):

    def __init__(self, log_file, tag):

        if log_file != "stdout":
            with open(log_file, "w") as f:
                pass
            self.printable = False
        else:
            self.printable = True

        self.log_file = log_file
        self.tag = tag

    def log_msg(self, loglevel, tag, msg):
        if self.printable:
            print str(datetime.datetime.now()) + ": " + str(tag) + " >> " + str(loglevel) + " >> " + str(msg) + "\n"
        else:
            with open(self.log_file, "a") as f:
                f.write(str(datetime.datetime.now()) + ": " + str(tag) + " >> " + str(loglevel)
                        + " >> " + str(msg) + "\n")

    def info(self, msg):
        self.log_msg("INFO", self.tag, msg)

    def warn(self, msg):
        self.log_msg("WARN", self.tag, msg)

    def error(self, msg):
        self.log_msg("ERROR", self.tag, msg)
