import sys
import time
import os
import argparse
from src.proto import pss_pb2
from google.protobuf import text_format
from src.core.defines import rpc_write
import datetime


def main(path_to_disturbance_file):
    start_time = time.time()
    assert os.path.isfile(path_to_disturbance_file) is True
    disturbances = pss_pb2.Disturbances()
    with open(path_to_disturbance_file, 'r') as f:
        text_format.Parse(f.read(), disturbances)


    for disturbance in disturbances.disturbance:
        time_elapsed = time.time() - start_time
        if time_elapsed < float(disturbance.timestamp):
            time.sleep(float(disturbance.timestamp) - time_elapsed)

        print str(datetime.datetime.now()) + " >> Queueing disturbance: OBJ_TYPE: %s, OBJ_ID: %s, " \
              "FIELD_TYPE: %s, DISTURBANCE_VALUE: %s" % (disturbance.objtype, disturbance.objid,
                                                         disturbance.fieldtype, disturbance.value)
        sys.stdout.flush()
        rpc_write(obj_type=disturbance.objtype, obj_id=disturbance.objid, field_type= disturbance.fieldtype,
                  value=disturbance.value)

    print "Finished Sending all disturbances !"
    sys.stdout.flush()

    while True:
        time.sleep(1.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_to_disturbance_file', dest="path_to_disturbance_file", type=str,
                        help="Path to disturbance file", required=True)

    args = parser.parse_args()
    main(args.path_to_disturbance_file)


