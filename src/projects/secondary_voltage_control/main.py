import sys
import argparse
sys.path.append("./")
from src.core.parse_project_configuration import *
from src.core.net_power import *
import grpc
from src.proto import pss_pb2
from src.proto import pss_pb2_grpc
from google.protobuf.empty_pb2 import Empty


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--run_time', dest="run_time", type=int, default=10,
                        help="Running time secs for the experiment (in virtual/real time)")
    parser.add_argument('--enable_kronos', dest="enable_kronos", default=0, type=int,
                        help="Enable Kronos ?")
    parser.add_argument('--rel_cpu_speed', dest="rel_cpu_speed", default=1, type=int,
                        help="Relative cpu speed of processes if kronos is enabled")
    parser.add_argument('--admin_user_name', dest="admin_user_name", default="melody", type=str,
                        help="Admin user name")
    parser.add_argument('--admin_password', dest="admin_password", default="davidmnicol", type=str,
                        help="Admin password")

    args = parser.parse_args()
    project_dir = os.path.dirname(os.path.realpath(__file__))

    project_run_time_args = {
                                "project_directory": project_dir,
                                "run_time": args.run_time,
                                "enable_kronos": args.enable_kronos,
                                "rel_cpu_speed": args.rel_cpu_speed,
                                "admin_user_name": args.admin_user_name,
                                "admin_password": args.admin_password,
                            }
    exp = parse_experiment_configuration(project_run_time_args)
    


    exp.initialize_project()
    total_time_ran = 0
    timestep_size = 500*MS

    
    # Main Loop of Co-Simulation
    while True:
        exp.run_for(timestep_size)
        exp.send_disturbance_to_powersim(obj_type="load", obj_id="4", field_type="v", value="202")
        exp.trigger_proxy_batch_processing()

        total_time_ran += timestep_size
        print "Time Elapsed: ", total_time_ran
        if total_time_ran >= args.run_time*SEC:
            break


        #if total_time_ran == 1*SEC:
        #    exp.trigger_nxt_replay()
    
    exp.close_project()
    


if __name__ == "__main__":
    main()



