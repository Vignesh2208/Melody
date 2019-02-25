Quick Start
===========
In this section we will help you install Melody and run you through a simple tutorial that helps you generate your first dataset.

Example: Secondary Voltage Control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`This example <https://github.com/Vignesh2208/Melody/tree/Melody_Matpower_project/src/projects/secondary_voltage_control/>`_ uses Melody to implement Secondary Voltage Control (SVC) for the `IEEE 39-bus New England <https://icseg.iti.illinois.edu/ieee-39-bus-system//>`_ power system model. The goal of SVC is to maintain the voltages at specifically chosen load buses called pilot buses at nominal values, subjected to random demand fluctuations throughout the day, by adjusting the voltages at generator buses. In this example, we implement SVC as a standard textbook p-controller which works on the first-order approximation of the power system. Being part of a close-loop control system, SVC is sensitive to the timing of (i) the input signals, which are voltages at pilot buses reported to the SCADA controller by the emulated PMUs, and (ii) the output signals, which are voltage setpoints of generator buses that are sent from the same SCADA server to the emulated PLCs. It is therefore crucially important that Melody is capable of precisely controlling the advance of virtual simulation time using Kronos.


PMUs
----
The PMU application is implemented in `this <https://github.com/Vignesh2208/Melody/blob/Melody_Matpower_project/src/projects/secondary_voltage_control/pmu.py/>`_ Python script. Each PMU is mapped to one pilot bus and is run as a process inside a mininet host. The PMU configuration can be found in the `projection configuration file <https://github.com/Vignesh2208/Melody/blob/Melody_Matpower_project/src/projects/secondary_voltage_control/project_configuration.prototxt/>`_, which is explained further below. During runtime, each PMU periodically sends GRPC read requests to the Proxy process to get the voltage measurement at its pilot bus::
  
  # Creating a list of read requests
  # self.obj_type = "bus"
  # self.obj_id = 2 (for pilot bus #2)
  # self.fieldtype = "Vm" (Vm for voltage magnitude)
  pilot_busses_to_read = [(obj_type_to_read, obj_id_to_read, field_type_to_read)]

  # Making a GRPC call to get the voltage measurement
  # The call blocks until Proxy returns the values
  ret = rpc_read(pilot_busses_to_read)

Once receiving the voltage reading, the PMU forwards it to the SCADA server over UDP::

  # pkt is a css_pb2.CyberMessage object that contains information about
  # the PMU, including its application ID and voltage measurement 
  self.host_control_layer.tx_pkt_to_powersim_entity(pkt.SerializeToString())


SCADA controller
----------------
The SCADA controller is implemented in `this <https://github.com/Vignesh2208/Melody/blob/Melody_Matpower_project/src/projects/secondary_voltage_control/scada.py/>`_ Python script. The SCADA process contains two main threads:

* One that keeps listening to UDP packets sent by PMUs containing voltage measurements
  
* The other that periodically (i) runs the SVC algorithm using the most up-to-date voltage measurements to compute the voltage setpoints at generator buses and (ii) sends them to the PLCs


PLCs
----
The PLC application is implemented in `this <https://github.com/Vignesh2208/Melody/blob/Melody_Matpower_project/src/projects/secondary_voltage_control/plc.py/>`_ Python script. Each PLC is mapped to one generator bus that it directly controls. Unlike PMUs and the SCADA server, PLCs do not run periodically. Instead, each PMU application waits for UDP packets sent by the SCADA controller, parses the packets to extract the generator voltage setpoints, then updates them to the power system simulation by issueing a GRPC write request to the Proxy::

  # Making a GRPC call to change the generator voltage setpoint
  rpc_write([(obj_type_to_write, obj_id_to_write, field_type_to_write, voltage_setpoint)])

Note that _all_ packets sent from PMUs to the SCADA controller and from the SCADA controller to the PLCs will travel through mininet network. Hence, they can be monitored using our packet capturing tool. However, the same tool will not capture the GRPC read and write requests. Interactions with the Proxy will be logged by the Proxy itself.


Disturbances
------------


Configuration
-------------
Configuration of the simulation is specified in the `project configuration file <https://github.com/Vignesh2208/Melody/blob/Melody_Matpower_project/src/projects/secondary_voltage_control/project_configuration.prototxt/>`_. Below we provide the high level summarization of the project:

* System model: IEEE 39-bus New England case
* Power sytem simulation tool: `MatPower <http://www.pserc.cornell.edu/matpower/>`_
* Network simulation tool: Mininet
* Application: Secondary Voltage Control
* Generator buses (controlled by SVC): 30, 31, 32, 33, 34, 35, 36, 37, 38, 39
* Pilot buses: 2, 6, 9, 10, 19, 20, 22, 23, 25, 29
* Cyber network: 5-switch clique/ring topology

Starting the example
--------------------
Switch to the project directory::

  cd ~/Melody/src/projects/secondary_voltage_control
  # set enable_kronos=0 if you wish to run without kronos support
  # if enable_kronos is set to 1, ensure that kronos module is pre-loaded
  sudo python main.py --enable_kronos=1 --run_time=10

This would run the example for 10 seconds in virtual time.

Generated Log files
-------------------
Log files and pcaps which are generated are stored inside::

  ~/Melogy/logs/secondary_voltage_control

One log file is generated for each application id.

Results
-------

We setup three following experiments:

* Without Kronos
* With Kronos, minimal network link delay (1ms)
* With Kronos, large network link delay (500ms)

For each experiment, we measure SVC's step response when there is a step change in reactive power consumption at bus #4 from 184 to 230 MVAR (25% increment). The data are collected for 25 seconds of virtual time. Using our lab's setup, it takes about 10 to 15 minutes to complete one experiment.

.. figure:: images/without_kronos.png
  :alt: Without Kronos
  :width: 100%
  :align: center
	  
  Without Kronos

As can be seen from the above graph, without Kronos, the timings of the measurements are totally messed up. Since SVC is time sensitive, that leads to unstable behaviors towards the end of the simulation.

.. figure:: images/with_kronos.png
  :alt: With Kronos and 1ms network link delay
  :width: 100%
  :align: center

  With Kronos and 1ms network link delay

With Kronos, we can see that SVC makes the right adjustment to bring the voltages at pilot buses back to their nominal values, which is indicated by all relative change of pilot bus voltages being at 1.0. The generator voltage setpoints slightly overshoot but finally stabilize 15 seconds after the onset of the disturbance.

.. figure:: images/with_kronos_and_delay_500.png
  :alt: With Kronos and 500ms network link delay
  :width: 100%
  :align: center

  With Kronos and 500ms network link delay

By introducing the network link delay of 500ms, it takes on average 2 seconds for each PMU to send data to the SCADA controller (i.e. 4 hops) and another 1.5 seconds for the SCADA controller to send to the PLCs (3 hops). The net result is a delay of at least 3.5 seconds for every change in the power system to be reflected back, which results in the observed oscillation. This experiment showcases the ability of Melody as a cosimulation tool, i.e. changes in the cyber network setting has the potential of affecting the performance of a cyber-physical system.

