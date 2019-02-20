About
============

Melody is a dataset generation tool for the modern power grid. Melody synthesizes network traffic for scalable systems, modeling both the cyber and physical components of the smart grid. It utilizes virtual time to generate traffic with high fidelity from a simulated physical network integrated with an emulated cyber network. 

Motivation
------------------

As control devices become increasingly prevalent in smart grid systems, the detection and prevention of attacks on these devices also become more critical, since attacks focused on the inherent security vulnerabilities of these devices could result in catastrophic failures. Machine learning based Network Intrusion Detection Systems (NIDS) seek to identify such attacks, but in order to do so, they rely on learning the normal traffic patterns of the system in question and subsequently finding anomalies in future network traffic. Due to associated security risks and operational resource constraints, this type of system network traffic data is not readily available for research purposes. Melody provides a framework for synthesizing these types of datasets.

Researchers can utilize Melody to generate both normal background network traffic and attack traffic in a modeled smart grid control network. Melody synthesizes high temporal fidelity datasets using a virtual time system that allows for fine-grained control over the execution of the system processes. Adversarial traffic is embedded within background traffic via emulation and traffic replay mechanisms. Melody has been evaluated to demonstrate that its synthesized datasets have temporal characteristics analogous to data obtained from a real network. Melody has the capability to generate datasets representing networks containing thousands of simultaneous flows while maintaining temporal and causal fidelity.


Architecture
------------------

Smart grid communication networks typically use a two-layered architecture containing a corporate network and a fieldbus/control network. The corporate network handles IT management, operator control, and the storage and analysis of process control data. The control network consists of a topology of controllers and field devices interconnected through multiple switches.

.. image:: images/cyber_phys_components.png
  :alt: Cyber-Physical Components 

Melody uses Mininet to emulate the communication network and MatPower to simulate the electrical behavior of the power grid. Melody generates packets either by emulating actual production software when possible or by embedding packet traces collected from arbitrary networks in the modelled network.

.. image:: images/melody_architecture.png
  :alt: Melody Architecture Diagram

<Virtual Time Discussion?>


