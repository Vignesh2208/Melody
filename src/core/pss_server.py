"""The proxy process

.. moduleauthor:: Hoang Hai Nguyen <email>
"""

from concurrent import futures
import time
import logging
import grpc
from threading import Event, Lock
import sys
from src.proto import pss_pb2
from src.proto import pss_pb2_grpc
import argparse
import signal
from pss_driver import MatPowerDriver


kill_now = False
def exit_gracefully(signum, frame):
    global kill_now
    print "Proxy Exiting Gracefully !"
    kill_now = True

class Job():
    def __init__(self, request, reply, event):
        self.request = request
        self.reply = reply
        self.event = event

    def to_string(self):
        # TODO: implement
        return ""

class PSSServicer(pss_pb2_grpc.pssServicer): # a.k.a. the Proxy
    def __init__(self,  case_directory, case_name):
        self.jobs = []
        self.jobLock = Lock()  # thread-safe access to job list
        self.mp = MatPowerDriver("/tmp")
        self.mp.open(case_directory + "/" + case_name)
        self.rlog = logging.getLogger("request_order")
        self.plog = logging.getLogger("process_order")


    def read(self, readRequest, context):
        self.rlog.info("%f %s" % (readRequest.timestamp, "Read"))

        event = Event()
        job = Job(readRequest, None, event)

        self.jobLock.acquire()
        try:
            self.jobs.append(job)
        finally:
            self.jobLock.release()

        event.wait()
        readResponse = job.reply

        return readResponse

    def write(self, writeRequest, context):
        self.rlog.info("%f %s" % (writeRequest.timestamp, "Write"))

        event = Event()
        job = Job(writeRequest, None, event)

        self.jobLock.acquire()
        try:
            self.jobs.append(job)
        finally:
            self.jobLock.release()

        event.wait()
        writeStatus = job.reply

        return writeStatus

    def process(self, request, context):
        self.jobLock.acquire()
        self.rlog.info("Process id=%s" % request.id)

        status = pss_pb2.Status()
        status.id = request.id

        self.plog.info("Start batch processing")

        try:
            while len(self.jobs) > 0:
                # Pop the earliest job from job list
                timestamps = [job.request.timestamp for job in self.jobs]
                idx = timestamps.index(min(timestamps))
                job = self.jobs.pop(idx)
                request = job.request

                self.plog.info("timestamp=%f, type=%s" % (request.timestamp, type(request)))

                if type(request) == pss_pb2.ReadRequest:
                    readResponse = pss_pb2.ReadResponse()

                    for req in request.request:
                        res = readResponse.response.add()
                        res.id = req.id
                        res.value = self.mp.read(req.objtype, req.objid, req.fieldtype)
                        self.plog.info("READ <%s,%s,%s,%s> returns <%s>" % (
                        req.id, req.objtype, req.objid, req.fieldtype, res.value))

                    job.reply = readResponse
                    job.event.set()

                elif type(request) == pss_pb2.WriteRequest:
                    writelist = [(req.objtype, req.objid, req.fieldtype, req.value) for req in request.request]
                    self.mp.write_multiple(writelist)
                    self.mp.run_pf()

                    writeStatus = pss_pb2.WriteStatus()

                    for req in request.request:
                        res = writeStatus.status.add()
                        res.id = req.id
                        res.status = pss_pb2.SUCCEEDED  # TODO: get write status from pss
                        self.plog.info("WRITE <%s,%s,%s,%s,%s> returns <%s>" % (
                        req.id, req.objtype, req.objid, req.fieldtype, req.value, res.status))

                    job.reply = writeStatus
                    job.event.set()

        finally:
            self.jobLock.release()
            self.plog.info("Stop batch processing")

            status.status = pss_pb2.SUCCEEDED
            return status
        
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--project_directory", dest="project_directory")
    parser.add_argument("--listen_ip", dest="listen_ip")

    global kill_now
    kill_now = False

    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)
    args = parser.parse_args()

    print "Project Directory: ", args.project_directory
    print "Listening ON: ", args.listen_ip, " Port: 50051"
    sys.stdout.flush()
    logging.basicConfig(level=logging.DEBUG)
    # how many workers is sufficient?
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10000))
    pss_pb2_grpc.add_pssServicer_to_server(PSSServicer(args.project_directory, "powersim_case"), server)
    server.add_insecure_port(args.listen_ip + ':50051')
    server.start()
    
    try:
        while True:
            time.sleep(1.0)
            if kill_now:
                server.stop(0)
                break
    except KeyboardInterrupt:
        server.stop(0)

