"""The proxy is implemented as a GRPC server.

.. moduleauthor:: Hoang Hai Nguyen <nhh311@gmail.com>
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


REQUEST_LOG = "RLOG"
PROCESS_LOG = "PLOG"


class Job():
    '''A data structure to store the GRPC read/write request, the reply, and an Event() object to signal when the reply is ready to be returned to the requester.
    ''' 
    def __init__(self, request, reply):
        self.request = request
        self.reply = reply
        self.event = Event()

    
    def to_string(self):
        # TODO: implement
        return ""


class PSSServicer(pss_pb2_grpc.pssServicer):
    '''The proxy class.

    @TODO: decouple MatPowerDriver logic from the proxy initialization. This should be straightforward.

    :param case_directory: directory containing the power system simulation case
    :type case_directory: str
    :param case_name: name of the power system simulation case
    :type case_name: str
    '''
    def __init__(self,  case_directory, case_name):
        self.jobs = []
        self.jobLock = Lock()  # thread-safe access to job list
        self.mp = MatPowerDriver("/tmp")
        self.mp.open(case_directory + "/" + case_name)
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
        job = Job(readRequest, None)
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
        job = Job(writeRequest, None)
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

                if type(request) == pss_pb2.ReadRequest:
                    readResponse = pss_pb2.ReadResponse()

                    for req in request.request:
                        res = readResponse.response.add()
                        res.id = req.id
                        res.value = self.mp.read(req.objtype, req.objid, req.fieldtype)
                        self.plog.info("%s,READ,%s,%s,%s,%s,%s" % (
                        request.timestamp, req.id, req.objtype, req.objid, req.fieldtype, res.value))

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
                        self.plog.info("%s,WRITE,%s,%s,%s,%s,%s,%s" % (
                        request.timestamp, req.id, req.objtype, req.objid, req.fieldtype, req.value, res.status))

                    job.reply = writeStatus
                    job.event.set()

            self.jobLock.release()
            processStatus.status = pss_pb2.SUCCEEDED
            return processStatus
        
    
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

