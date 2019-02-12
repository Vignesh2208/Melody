import shared_buffer
from shared_buffer import *
import logger
from logger import *
from basicNetworkServiceLayer import basicNetworkServiceLayer
import getopt
from src.utils.sleep_functions import sleep
import time


def extract_mappings(net_cfg_file):
    cyber_entity_id_to_ip = {}
    cyber_entity_id_to_mapped_powersim_ids = {}
    assert (os.path.isfile(net_cfg_file) == True)
    lines = [line.rstrip('\n') for line in open(net_cfg_file)]

    for line in lines:
        line = ' '.join(line.split())
        line = line.replace(" ", "")
        split_list = line.split(',')
        assert (len(split_list) >= 3)
        host_id = int(split_list[0][1:])
        ip_addr = split_list[1]
        port = int(split_list[2])
        cyber_entity_id_to_ip[host_id] = (ip_addr, port)

        for i in xrange(3, len(split_list)):
            powersim_id = str(split_list[i])
            if host_id not in cyber_entity_id_to_mapped_powersim_ids.keys():
                cyber_entity_id_to_mapped_powersim_ids[host_id] = []
            cyber_entity_id_to_mapped_powersim_ids[host_id].append(powersim_id)

    return cyber_entity_id_to_ip, cyber_entity_id_to_mapped_powersim_ids


def usage():
    print "python host.py <options>"
    print "Options:"
    print "-h or --help"
    print "-c or --netcfg-file=  Absolute path to network Cfg File <required>"
    print "-l or --log-file=     Absolute path to log File <optional>"
    print "-r or --run-time=    Run time of host in seconds before it is shut-down <optional - default forever>"
    print "-n or --project-name= Name of project folder <optional - default is test project>"
    print "-d or --id= Id of the node. Required and must be > 0"
    sys.exit(0)


def parseOpts():

    net_cfg_file_path = None
    host_id = None
    log_file = "stdout"
    run_time = 0
    project_name = "test"

    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "hc:l:r:n:id:",
                                     ["help", "netcfg-file=", "log-file=", "run-time=", "project-name=", "id="])
    except getopt.GetoptError as e:
        print (str(e))
        usage()
        return 1
    for (o, v) in opts:
        if o in ("-h", "--help"):
            usage()

        if o in ("-c", "--netcfg-file="):
            net_cfg_file_path = str(v)
        if o in ("-l", "--log-file="):
            log_file = str(v)
        if o in ("-r", "--run-time="):
            run_time = int(v)
        if o in ("-n", "--project-name="):
            project_name = str(v)
        if o in ("-d", "--id="):
            host_id = int(v)

    assert (net_cfg_file_path is not None and host_id is not None)
    return (net_cfg_file_path, log_file, run_time, project_name, host_id)


def init_shared_buffers(host_id, run_time, shared_buf_array, log):
    result = shared_buf_array.open(bufName="h" + str(host_id) + "-main-cmd-channel-buffer", isProxy=False)

    if result == BUF_NOT_INITIALIZED or result == FAILURE:
        log.error("Failed to open communication channel ! Not starting any threads !")
        sys.stdout.flush()
        if run_time == 0:
            while True:
                sleep(1)

        start_time = time.time()
        sleep(run_time + 2)
        while time.time() < start_time + float(run_time):
            sleep(1)
        sys.exit(0)


def main(host_id, net_cfg_file, log_file, run_time, project_name):
    cyber_entity_id_to_ip, cyber_entity_id_to_mapped_powersim_ids = extract_mappings(net_cfg_file)
    log = logger.Logger(log_file, "Host" + str(host_id) + ": ")
    script_location = os.path.dirname(os.path.realpath(__file__))
    project_location = script_location + "/../projects/" + project_name + "/"
    shared_buf_array = shared_buffer_array()

    host_control_layer_override_file = "h" + str(host_id) + "_control_layer"
    host_attack_layer_override_file = "h" + str(host_id) + "_attack_layer"
    if os.path.isfile(project_location + host_control_layer_override_file + ".py"):
        host_ipc_layer = __import__("src.projects." + str(project_name) + "." + host_control_layer_override_file,
                                  globals(), locals(), ['hostControlLayer'], -1)
        host_ipc_layer = host_ipc_layer.hostControlLayer
    else:
        host_ipc_layer = __import__("basicHostIPCLayer", globals(), locals(), ['basicHostIPCLayer'], -1)
        host_ipc_layer = host_ipc_layer.basicHostIPCLayer

    if os.path.isfile(project_location + host_attack_layer_override_file + ".py"):
        host_attack_layer = __import__("src.projects." + str(project_name) + "." + host_attack_layer_override_file,
                                   globals(), locals(),['hostAttackLayer'], -1)
        host_attack_layer = host_attack_layer.hostAttackLayer
    else:
        host_attack_layer = __import__("basicHostAttackLayer", globals(), locals(), ['basicHostAttackLayer'], -1)
        host_attack_layer = host_attack_layer.basicHostAttackLayer

    log.info("Initializing inter process communication channels ...")
    sys.stdout.flush()
    init_shared_buffers(host_id, run_time, shared_buf_array, log)

    log.info("Successfully opened an inter process communication channel !")
    sys.stdout.flush()

    ipc_layer = host_ipc_layer(host_id, log_file)
    ipc_layer.set_powersim_id_map(cyber_entity_id_to_mapped_powersim_ids)
    net_layer = basicNetworkServiceLayer(host_id, log_file, cyber_entity_id_to_ip)
    attack_layer = host_attack_layer(host_id, log_file, ipc_layer, net_layer)
    ipc_layer.set_attack_layer(attack_layer)
    net_layer.set_attack_layer(attack_layer)
    assert (ipc_layer is not None and net_layer is not None and attack_layer is not None)

    log.info("Waiting for start command ... ")
    sys.stdout.flush()
    recv_msg = ''
    while "START" not in recv_msg:
        dummy_id, recv_msg = shared_buf_array.read_until("h" + str(host_id) + "-main-cmd-channel-buffer",
                                                         cool_off_time=0.1)

    net_layer.start()
    attack_layer.start()
    ipc_layer.start()
    log.info("Signalled all threads to start ...")
    sys.stdout.flush()
    recv_msg = ''

    log.info("Waiting for stop command ...")
    sys.stdout.flush()
    while "EXIT" not in recv_msg:
        dummy_id, recv_msg = shared_buf_array.read_until("h" + str(host_id) + "-main-cmd-channel-buffer",
                                                         cool_off_time=0.1)

    ipc_layer.cancel_thread()
    attack_layer.cancel_thread()
    net_layer.cancel_thread()

    log.info("Shutting Down ... ")
    sys.stdout.flush()


if __name__ == "__main__":
    net_cfg_file_path, log_file, run_time, project_name, host_id = parseOpts()
    sys.exit(main(host_id, net_cfg_file_path, log_file, run_time, project_name))
