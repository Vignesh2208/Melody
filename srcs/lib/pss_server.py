"""The proxy is implemented as a GRPC server.

.. moduleauthor:: Hoang Hai Nguyen <nhh311@gmail.com>
"""


import time
import logging
import grpc
import sys
import argparse
import signal
import os

from threading import Event, Lock
from srcs.power_sim.drivers import MatPowerDriver
from concurrent import futures
from srcs.proto import pss_pb2
from srcs.proto import pss_pb2_grpc

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

kill_now = False

def exit_gracefully(signum, frame):
    global kill_now
    logging.info("Proxy Exiting Gracefully !")
    kill_now = True


REQUEST_LOG = "RLOG"
PROCESS_LOG = "PLOG"


class Job():
    '''A data structure to store the GRPC read/write request, the reply, and an Event() object to signal when the reply is ready to be returned to the requester.
    ''' 
    def __init__(self, request, request_type, reply):
        self.request = request
        self.reply = reply
        self.request_type = request_type
        self.event = Event()

    
    def to_string(self):
        # TODO: implement
        return ""


class PSSServicer(pss_pb2_grpc.pssServicer): # a.k.a. the Proxy
    def __init__(self,  pssDriver, caseFile):
        self.jobs = []
        self.jobLock = Lock()  # thread-safe access to job list
        self.driver = pssDriver
        self.driver.open(caseFile)
        self.rlog = logging.getLogger(REQUEST_LOG)
        self.plog = logging.getLogger(PROCESS_LOG)

        
    def read(self, readRequest, context):
        '''Function to handle GRPC read requests from the simulated cyber network. Each GRPC read request is appended to the proxy's job list, where each job contains the request and its related information. The proxy processes all items in the job list once it receives the GRPC process request. The GRPC process request is invoked by the simulation main loop.

        :param readRequest: a GRPC read request object, which is a list of requests sharing the same timestamp.
        :type readRequest: pss_pb2.ReadRequest

        :return: a pss_pb2.ReadResponse object.
        '''
        
        self.jobLock.acquire()
        for req in readRequest.request:
            self.rlog.info("%s,READ,%s,%s,%s,%s" % (readRequest.timestamp, req.id, req.objtype, req.objid, req.fieldtype))
        job = Job(readRequest, "READ", None)
        self.jobs.append(job)
        self.jobLock.release()
        job.event.wait()
        readResponse = job.reply

        return readResponse

    
    def write(self, writeRequest, context):
        '''Function to handle GRPC write requests from the simulated cyber network. Similar to GRPC read requests, each GRPC write request is also appended to the proxy's job list, where each job contains the request and its related information. The proxy processes all items in the job list once it receives the GRPC process request. The GRPC process request is invoked by the simulation main loop.

        :param writeRequest: a GRPC write request object, which is a list of requests sharing the same timestamp.
        :type writeRequest: pss_pb2.WriteRequest

        :return: a pss_pb2.WriteStatus object
        '''

        self.jobLock.acquire()
        for req in writeRequest.request:
            self.rlog.info("%s,WRITE,%s,%s,%s,%s,%s" % (
            writeRequest.timestamp, req.id, req.objtype, req.objid, req.fieldtype, req.value))
        job = Job(writeRequest, "WRITE", None)
        self.jobs.append(job)
        self.jobLock.release()
        job.event.wait()
        writeStatus = job.reply

        return writeStatus

    
    def process(self, request, context):
        '''Function to handle GRPC process requests from simulation main loop. Requests, including both read and write requests, are processed in the timing order as given by their timestamps, not by the order in which they were enlisted to the job list. Process time may vary depending on the size of the job list and the type of requests.

        :param request: a GRPC process request object.
        :type request: pss_pb2.ProcessRequest

        :return: a pss_pb2.Status object.
        '''
        if len(self.jobs) == 0:
            return pss_pb2.Status(id=request.id, status=pss_pb2.SUCCEEDED)
            

        else:
            self.jobLock.acquire()
            processStatus = pss_pb2.Status(id=request.id)
            self.plog.info("--------------------")

            while len(self.jobs) > 0:
                # Pop the earliest job from job list
                timestamps = [float(job.request.timestamp) for job in self.jobs]
                idx = timestamps.index(min(timestamps))
                job = self.jobs.pop(idx)
                request = job.request

                if job.request_type == "READ":
                    readResponse = pss_pb2.ReadResponse()

                    for req in request.request:
                        res = readResponse.response.add()
                        res.id = req.id
                        res.value = self.driver.read(req.objtype, req.objid, req.fieldtype)
                        self.plog.info("%s,READ,%s,%s,%s,%s,%s" % (
                        request.timestamp, req.id, req.objtype, req.objid, req.fieldtype, res.value))

                    job.reply = readResponse
                    job.event.set()

                elif job.request_type == "WRITE":
                    writelist = [(req.objtype, req.objid, req.fieldtype, req.value) for req in request.request]
                    self.driver.write_multiple(writelist)
                    self.driver.run_pf()

                    writeStatus = pss_pb2.WriteStatus()

                    for req in request.request:
                        res = writeStatus.status.add()
                        res.id = req.id
                        res.status = pss_pb2.SUCCEEDED  # TODO: get write status from pss
                        self.plog.info("%s,WRITE,%s,%s,%s,%s,%s,%s" % (
                        request.timestamp, req.id, req.objtype, req.objid, req.fieldtype, req.value, res.status))

                    job.reply = writeStatus
                    job.event.set()

            self.jobLock.release()
            processStatus.status = pss_pb2.SUCCEEDED
            return processStatus
        
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--driver_name", dest="driver_name")
    parser.add_argument("--listen_ip", dest="listen_ip")
    parser.add_argument("--case_file_path", dest="case_file_path")

    kill_now = False

    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)
    args = parser.parse_args()

    logging.info(f"Driver Name: {args.driver_name}")
    logging.info(f"Case File: {args.case_file_path}")
    logging.info(f"Listening ON: {args.listen_ip} Port: 50051")
    

    if not os.path.isfile(args.case_file_path):
        logging.info("Specified case file not found !")
        
        raise NotImplementedError

    if args.driver_name == "MatPowerDriver":
        pss_driver = MatPowerDriver.MatPowerDriver()

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=1000),
        maximum_concurrent_rpcs = 1000)
    pss_pb2_grpc.add_pssServicer_to_server(
        PSSServicer(pss_driver, args.case_file_path), server)
    server.add_insecure_port(f"{args.listen_ip}:50051")
    server.start()


    
    try:
        while True:
            time.sleep(1.0)
            if kill_now:
                logging.info("Exiting gracefully !")
                
                server.stop(0)
                break
    except KeyboardInterrupt:
        logging.info("Exiting gracefully !")
        
        server.stop(0)

