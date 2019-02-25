"""Disturbance generator

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>
"""

import argparse
from src.proto import configuration_pb2
from google.protobuf import text_format
import datetime
import shared_buffer
from shared_buffer import *



def init_shared_buffers(shared_buf_array):
    """Initialize shared buffers used for communication with the main Melody process

    :param shared_buf_array: A shared buffer array object (defined in src/core/shared_buffer.py)
    :return: None
    """

    result = shared_buf_array.open(bufName="disturbance-gen-cmd-channel-buffer", isProxy=False)
    if result == BUF_NOT_INITIALIZED or result == FAILURE:
        print "Failed to open communication channel ! Not starting any threads !"
        sys.exit(0)
    print "Buffer opened: disturbance-gen-cmd-channel-buffer"
    sys.stdout.flush()

def main(path_to_disturbance_file):
    """Starts the disturbance generator and sends disturbances to the power simulation at specified relative timestamps

    Disturbances and their relative timestamps are specified in a file according to the Disturbance message format
    defined in src/proto/configuration.proto

    :param path_to_disturbance_file: Absolute path to file containing disturbances specified in Disturbance proto
                                     format. (Refer src/proto/configuration.proto : Disturbances)
    :type path_to_disturbance_file: str
    :return: None
    """
    shared_buf_array = shared_buffer_array()
    init_shared_buffers(shared_buf_array)

    recv_msg = ''
    while "START" not in recv_msg:
        dummy_id, recv_msg = shared_buf_array.read_until("disturbance-gen-cmd-channel-buffer", cool_off_time=0.1)

    start_time = time.time()
    assert os.path.isfile(path_to_disturbance_file) is True
    disturbances = configuration_pb2.Disturbances()
    with open(path_to_disturbance_file, 'r') as f:
        text_format.Parse(f.read(), disturbances)

    for disturbance in disturbances.disturbance:
        time_elapsed = time.time() - start_time
        if time_elapsed < float(disturbance.timestamp):
            time.sleep(float(disturbance.timestamp) - time_elapsed)

        print "-----------------------------------------------------------------------------"
        print "Sending Following Disturbances at : ", str(datetime.datetime.now()), "  >> "
        sys.stdout.flush()

        write_list = []
        for request in disturbance.request:
            print "Disturbance Description: OBJ_TYPE: %s, OBJ_ID: %s, " \
              "FIELD_TYPE: %s, DISTURBANCE_VALUE: %s" % (request.objtype, request.objid,
                                                         request.fieldtype, request.value)
            write_list.append((request.objtype, request.objid, request.fieldtype, request.value))
        rpc_write(write_list)

    print "-----------------------------------------------------------------------------"
    print "Finished Sending all disturbances !"
    sys.stdout.flush()

    recv_msg = ''
    while "EXIT" not in recv_msg:
        dummy_id, recv_msg = shared_buf_array.read_until("disturbance-gen-cmd-channel-buffer", cool_off_time=0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_to_disturbance_file', dest="path_to_disturbance_file", type=str,
                        help="Path to disturbance file", required=True)

    args = parser.parse_args()
    main(args.path_to_disturbance_file)


