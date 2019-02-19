import logging
import grpc
import time
import random
from google.protobuf.empty_pb2 import Empty
import threading
import logging

import pss_pb2
import pss_pb2_grpc


def rpc_read(ts, objtype, objid, fieldtype):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = pss_pb2_grpc.pssStub(channel)
        readRequest = pss_pb2.ReadRequest(timestamp=ts, objtype=objtype, objid=objid, fieldtype=fieldtype)
        response = stub.read(readRequest)
        logging.info("Read <%s> return <%s>"%(",".join([ts, objtype, objid, fieldtype]), response.value))


def rpc_write(ts, objtype, objid, fieldtype, value):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = pss_pb2_grpc.pssStub(channel)
        writeRequest = pss_pb2.WriteRequest(timestamp=ts, objtype=objtype, objid=objid, fieldtype=fieldtype, value=value)
        status = stub.write(writeRequest)
        logging.info("Write <%s> return <%s>"%(",".join([ts, objtype, objid, fieldtype, value]), status.status))
        

def rpc_process():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = pss_pb2_grpc.pssStub(channel)
        status = stub.process(Empty())
        logging.info("Process return <%s>"%status.status)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        while True:
            choice = random.randint(0,2)
            ts = str(time.time() + 4 * (0.5 - random.random()))

            if choice == 0:
                # busid = str(random.randint(1,39))
                busid = "1"
                threading.Thread(target=rpc_read, args=(ts,"bus",busid,"v",)).start()

            elif choice == 1:
                # genid = str(random.randint(30,39))
                genid = "30"
                genv = str(1 + 0.1 * random.random())
                threading.Thread(target=rpc_write, args=(ts,"gen",genid,"v",genv,)).start()

            else:
                threading.Thread(target=rpc_process).start()

            time.sleep(1)

    except KeyboardInterrupt:
        exit()

