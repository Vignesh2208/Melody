import argparse
import logging
import srcs.lib.defines as defines
from srcs.lib.parse_project_configuration import *
from srcs.lib.net_power import *



def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--run_time', dest="run_time", type=int, default=10,
                        help="Running time secs for the experiment (in virtual/real time)")
    parser.add_argument('--enable_kronos', dest="enable_kronos", default=0, type=int,
                        help="Enable Kronos ?")
    parser.add_argument('--rel_cpu_speed', dest="rel_cpu_speed", default=1, type=int,
                        help="Relative cpu speed of processes if kronos is enabled")

    args = parser.parse_args()

    # project_dir is the directory in which this script is located
    project_dir = os.path.dirname(os.path.realpath(__file__))

    project_run_time_args = {
                                "project_directory": project_dir,
                                "run_time": args.run_time,
                                "enable_kronos": args.enable_kronos,
                                "rel_cpu_speed": args.rel_cpu_speed,
                            }
    exp = parse_experiment_configuration(project_run_time_args)
    exp.initialize_project()

    total_time_ran = 0

    #MS, SEC are defined in srcs/lib/defines.py
    timestep_size = 500*defines.MS

    
    # Main Loop of Co-Simulation
    while True:
        exp.run_for(timestep_size)
        total_time_ran += timestep_size

        logging.info(
            f"Time Elapsed (Secs): {float(total_time_ran)/float(defines.SEC)}")
        if total_time_ran >= args.run_time*defines.SEC:
            break

    exp.close_project()


if __name__ == "__main__":
    main()



