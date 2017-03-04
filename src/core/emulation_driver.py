import argparse
import os
import json
from utils.sleep_functions import sleep

TRAFFIC_FLOW_PERIODIC = 'Periodic'
TRAFFIC_FLOW_EXPONENTIAL = 'Exponential'
TRAFFIC_FLOW_ONE_SHOT = 'One Shot'


class EmulationDriver(object):

    def __init__(self, input_params):

        self.type = input_params["type"]
        self.cmd = input_params["cmd"]
        self.offset = input_params["offset"]
        self.inter_flow_period = input_params["inter_flow_period"]
        self.run_time = input_params["run_time"]
        self.long_running = input_params["long_running"]
        self.root_user_name = input_params["root_user_name"]
        self.root_password = input_params["root_password"]

    def trigger(self):

        if self.type == TRAFFIC_FLOW_ONE_SHOT:
            sleep(self.offset)
            os.system(self.cmd)
            sleep(self.run_time - self.offset)

        elif self.type == TRAFFIC_FLOW_EXPONENTIAL:
            pass
        elif self.type == TRAFFIC_FLOW_PERIODIC:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_params_file_path", dest="input_params_file_path")

    args = parser.parse_args()

    input_params = json.loads(open(args.input_params_file_path, "r"))
    d = EmulationDriver(input_params)
    sleep(5)
    d.trigger()

if __name__ == "__main__":
    main()


