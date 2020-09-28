Project Configuration
=====================

A Melody project consists of two components: (1) a cyber emulation and (2) a power simulation. This section specifies how to create a new project and configure its components.

Creating a New Project
^^^^^^^^^^^^^^^^^^^^^^

* To create a new project with a <project_name>, please do the following::

    cp -R ~/Melody/srcs/projects/blank_project ~/Melody/srcs/projects/<project_name>

Specifying a Project Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The project configuration can be specified by editing the project_configuration.prototxt file located inside the project directory. The project configuration must be specified according to the `configuration.proto <https://github.com/Vignesh2208/Melody/tree/master/srcs/proto/configuration.proto/>`_ format. We briefly describe the format below with an example. For the complete configuration, see `this <https://github.com/Vignesh2208/Melody/tree/master/srcs/projects/secondary_voltage_control/project_configuration.prototxt/>`_. 

* project_name: must match the name of the project directory::
  
    project_name: "secondary_voltage_control"

* cyber_emulation_spec: describes the cyber topology::

    cyber_emulation_spec {
      topology_name: "clique_topo"
      num_hosts: 5
      num_switches: 5
      inter_switch_link_latency_ms: 1
      host_switch_link_latency_ms: 1
      additional_topology_param {
        parameter_name: "per_switch_links"
        parameter_value_int: 2
      }
      additional_topology_param {
        parameter_name: "num_hosts_per_switch"
        parameter_value_int: 1
      }
    }

  In this example, we specify to use the clique_topo. The name "clique_topo" is automatically resolved to a "clique_topo.py" file located inside::

    ~/Melody/srcs/cyber_network/topologies

  directory. The rest of the topology attributes are converted into a "**params**" dictionary and passed as a run time argument to the clique_topo object. In this example the generated "**params**" dictionary will be equal to::

    params = {
                "num_hosts": 5,
                "num_switches" : 5,
                "inter_switch_link_latency_ms": 1,
                "host_switch_link_latency_ms" : 1,
                "per_switch_links" : 2,
                "num_hosts_per_switch" : 1,
             }

  The cyber topology implementation may use these parameters to construct a mininet topology by using the mininet Topo API.

* power_simulation_spec: describes the power simulator driver which will be used by proxy to handle incoming requests::

    power_simulation_spec {
      power_sim_driver_name: "MatPowerDriver"
      case_file_path: "/home/kronos/Melody/srcs/power_sim/cases/case39.m"
    }

  In this example, we use the MatPowerDriver. The specified driver name is automatically resolved to a "MatPowerDriver" class located in srcs/power_sim/drivers/MatPowerDriver.py. The case_file_path is passed as an argument to the "**open**" function implemented by the driver.

* cyber_physical_map: describes which applications are running on a specific mininet host::

    cyber_physical_map {
      cyber_host_name	:	"h3"
      mapped_application {
        application_id	:	"PMU_Pilot_Bus_2"
        application_src : "pmu.py"
        listen_port : 5100
      }
      mapped_application {
        application_id   :   "PMU_Pilot_Bus_6"
        application_src : "pmu.py"
        listen_port : 5101
      }
      mapped_application {
        application_id   :   "PMU_Pilot_Bus_9"
        application_src : "pmu.py"
        listen_port : 5102
      }
      mapped_application {
        application_id   :   "PMU_Pilot_Bus_10"
        application_src : "pmu.py"
        listen_port : 5103
      }
      mapped_application {
        application_id   :   "PMU_Pilot_Bus_19"
        application_src : "pmu.py"
        listen_port : 5104
      }
      mapped_application {
        application_id   :   "PMU_Pilot_Bus_20"
        application_src : "pmu.py"
        listen_port : 5105
      }
      mapped_application {
        application_id   :   "PMU_Pilot_Bus_22"
        application_src : "pmu.py"
        listen_port : 5106
      }
      mapped_application {
        application_id   :   "PMU_Pilot_Bus_23"
        application_src : "pmu.py"
        listen_port : 5107
      }
      mapped_application {
        application_id   :   "PMU_Pilot_Bus_25"
        application_src : "pmu.py"
        listen_port : 5108
      }
      mapped_application {
        application_id   :   "PMU_Pilot_Bus_29"
        application_src : "pmu.py"
        listen_port : 5109
      }
      description :	"PMUs for reading pilot buses"
    }

  In this example, on mininet host "h3", 10 applications are configured to run. Each mapped application has a unique id and a port on which it is listening for packets. All applications in this case share the same source file which is automatically resolved to the file::

    ~/Melody/srcs/projects/secondary_voltage_control/pmu.py. 

  All 10 applications are started as separate processes which execute the same source file but they are passed their respective application_id and the application_ids of all other applications running in the network as arguments. The source file may perform different operations based on the passed/assigned application_id.

* bg_flow: describes a background traffic flow. A single project configuration may have multiple background flow descriptions::

    bg_flow {
      src_cyber_entity	:	"h2"
      dst_cyber_entity	:	"h3"
      cmd_to_run_at_src	:	"ping -i 0.2 h3"
      cmd_to_run_at_dst	:	""
      flow_start_time		:	1
      description		    :	"Ping flow between h2 to h3 starting at time 1.0 seconds"
    }

  In this examples, it describes a ping flow which is run between h2 and h3 every 200 ms starting at time 1.0 seconds from the beginning of the emulation. Note that the ping is simply given the name of the destination host h3 instead of its IP address. This is because Melody can automatically resolve the host name into its IP address at run time before executing the command. 

* replay_flow: describes a replay traffic flow. A single project configuration may have multiple replay flow descriptions::

    replay_flow {
      involved_cyber_entity: "h1"
      involved_cyber_entity: "h3"
      pcap_file_path: "/home/moses/Melody/srcs/projects/secondary_voltage_control/replay_pcaps/pmu_fuzzing_h1_h3.pcap"
      description: "Replaying a PMU fuzzing attack gathered from a real network over the path between h1-h3"
    }

  In this example, the pcap specified by the given absolute path is replayed between h1 and h3 when it is "**triggered**". We describe trigerring replays in a subsequent subsection. Note that a replay flow must have atleast 2 involved_cyber_entities and they must all be valid mininet host names.

Specifying/Sending Disturbances to the Power Simulation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A power system may be affected by outside sources of interference such as load changes. Melody allows specifying these disturbances in a file inside the project directory. The disturbances are specified in a "**disturbances.prototxt**" file according to the "**Disturbances**" message defined in srcs/proto/configuration.proto. In the working example we send five `disturbances <https://github.com/Vignesh2208/Melody/tree/master/srcs/projects/secondary_voltage_control/disturbances.prototxt>`_ at 2, 2.5, 3, 3.5 and 4 seconds after the start of the emulation.


Creating custom cyber topologies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a new cyber topology, follow the steps given below::

  cp ~/Melody/srcs/cyber_network/topologies/blank_topology.py ~/Melody/srcs/cyber_network/topologies/<cyber_topology_name>.py

You may now edit the file and use the mininet API to implement a custom topology. It will then be accessible from the project configuration by simply specifying the same <cyber_topology_name> in the configuration.

.. note:: Do not modify the class name inside the new file. It must remain as CyberTopology.

Creating custom host applications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a new application inside a <project_name>, follow the steps given below::

  cp ~/Melody/srcs/projects/<project_name>/blank_application.py ~/Melody/srcs/projects/<project_name>/<application_name>.py

You may now edit the file and override specific functions of the `basicHostIPCLayer <https://github.com/Vignesh2208/Melody/tree/master/srcs/lib/basicHostIPCLayer.py>`_  class. Please refer the module documentation for more details. This file <application_name>.py may now be specified as an "application_src" attribute in the project configuration.

.. note:: Do not modify the class name inside the new file. It must remain as hostApplicationLayer.

Changing the Power Simulation Tool
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Melody supports flexible interchange of the power simulation tool used. By default it ships with support for MatPower. If the power simulator is to be changed, a new driver has to be implemented for the specific power simulator in question. The driver must implement the abstract class defined in ~/Melody/srcs/lib/pss_driver.py and it must be placed in ~/Melody/srcs/power_sim/drivers.

The following additional edits must also be made to srcs/lib/pss_server.py::

  # import the new driver <driver-name>
  from srcs.power_sim.drivers import <driver-name>

  # instantiate a driver object in __main__
  if args.driver_name == <driver-name> :
      pss_driver  = <driver-name>.<driver-class-name>()


Experiment control API
^^^^^^^^^^^^^^^^^^^^^^

Melody offers some simple API to control experiment flow. These may be used inside the main.py script of the project.

* Creating an experiment container::

    exp = parse_experiment_configuration(project_run_time_args)

  project_run_time_args must be a dictionary with the following keys::

    {
        "project_directory": <directory of the main script>,
        "run_time": <running time in seconds>,
        "enable_kronos": <is kronos enabled: 1 or 0>,
        "rel_cpu_speed": <relative cpu speed for a kronos experiment>,
    }

*  Initializing the project::

      exp.initialize_project()

   This starts all the hosts, proxy and application processes and waits until the experiment is triggered to run.

*  Running the experiment::

      exp.run_for(duration_ns)

   This runs the experiment for the specified duration in nano seconds. It then automatically synchronizes with the proxy and the power simulator. The mininum duration possible is 100 us. If a duration smaller than 100 us is passed, it will be capped to 100 us.

*  Triggering replays::

      exp.trigger_nxt_replay()

   It can be used to trigger/start the next replay flow. Replays can be triggered only in the order in which they are specified in the project configuration. A variant of this call is::

      exp.trigger_nxt_k_replays(k)

   It will simultaneously send a start command for the next k replays. But only the largest first "n" non-conflicting replays will be immediately activated. Two replay flows are non-conflicting if they do not share any common "involved" hosts. Conflicting replays are scheduled at the earliest feasible time.

*  Closing the project::

     exp.close_project()
