"""Disturbance generator

.. moduleauthor:: Vignesh Babu <vig2208@gmail.com>
"""

import argparse
import logging
import sys
import datetime
import time
import os
import srcs.lib.shared_buffer

import srcs.lib.defines as defines

from srcs.proto import configuration_pb2
from google.protobuf import text_format
from srcs.lib.shared_buffer import *



def init_shared_buffers(shared_buf_array):
    """Initialize shared buffers used for communication with the main Melody process

    :param shared_buf_array: A shared buffer array object (defined in srcs/core/shared_buffer.py)
    :return: None
    """

    result = shared_buf_array.open(
        bufName="disturbance-gen-cmd-channel-buffer", isProxy=False)
    if result == defines.BUF_NOT_INITIALIZED or result == defines.FAILURE:
        logging.error("Failed to open communication channel ! Not starting any threads !")
        sys.exit(defines.FAILURE)
    logging.info("Buffer opened: disturbance-gen-cmd-channel-buffer")
    

def main(path_to_disturbance_file):
    """Starts the disturbance generator and sends disturbances to the power simulation at specified relative timestamps

    Disturbances and their relative timestamps are specified in a file according to the Disturbance message format
    defined in srcs/proto/configuration.proto

    :param path_to_disturbance_file: Absolute path to file containing disturbances specified in Disturbance proto
                                     format. (Refer srcs/proto/configuration.proto : Disturbances)
    :type path_to_disturbance_file: str
    :return: None
    """
    shared_buf_array = shared_buffer_array()
    init_shared_buffers(shared_buf_array)

    recv_msg = ''
    while defines.START_CMD not in recv_msg:
        dummy_id, recv_msg = shared_buf_array.read_until(
            "disturbance-gen-cmd-channel-buffer", cool_off_time=0.1)

    start_time = time.time()
    assert os.path.isfile(path_to_disturbance_file) is True
    disturbances = configuration_pb2.Disturbances()
    with open(path_to_disturbance_file, 'r') as f:
        text_format.Parse(f.read(), disturbances)

    for disturbance in disturbances.disturbance:
        time_elapsed = time.time() - start_time
        if time_elapsed < float(disturbance.timestamp):
            time.sleep(float(disturbance.timestamp) - time_elapsed)

        logging.info("-----------------------------------------------------------------------------")
        logging.info("Sending Disturbances ...")

        write_list = []
        for request in disturbance.request:
            logging.info("Disturbance Description: OBJ_TYPE: %s, OBJ_ID: %s, "
                         "FIELD_TYPE: %s, DISTURBANCE_VALUE: %s" % (
                             request.objtype, request.objid,
                             request.fieldtype, request.value))
            write_list.append(
                (request.objtype, request.objid, request.fieldtype, request.value))
        defines.rpc_write(write_list)

    logging.info("-----------------------------------------------------------------------------")
    logging.info("Finished Sending all disturbances !")

    recv_msg = ''
    while defines.EXIT_CMD not in recv_msg:
        dummy_id, recv_msg = shared_buf_array.read_until(
            "disturbance-gen-cmd-channel-buffer", cool_off_time=0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_to_disturbance_file',
                        dest="path_to_disturbance_file", type=str,
                        help="Path to disturbance file", required=True)

    args = parser.parse_args()
    main(args.path_to_disturbance_file)


