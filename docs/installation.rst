Installation
============

Minimum System Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Melody and Kronos have been tested on Ubuntu 16.04.5 LTS. Kronos uses a modified linux kernel v4.4.50 patch. The system should consist of an Intel i5 or later processor with atleast 4 cores and 8 GB of RAM for good performance. It is preferable to install Kronos and Melody inside a VM with Virtualized Intel-VTx and CPU performance counters. This is known to avoid display driver issues on newer laptops/machines.

Installing Kronos
^^^^^^^^^^^^^^^^^

To get started on Kronos, please perform the following setup steps:

* Disable Transparent HugePages: (Add the following to /etc/rc.local to permanently disable them)::

    if test -f /sys/kernel/mm/transparent_hugepage/enabled; then
      echo never > /sys/kernel/mm/transparent_hugepage/enabled
    fi
    if test -f /sys/kernel/mm/transparent_hugepage/defrag; then
      echo never > /sys/kernel/mm/transparent_hugepage/defrag
    fi
* Ensure that /etc/rc.local has execute permissions::

    sudo chmod +x /etc/rc.local

* Clone Repository into /home/${user} directory. Checkout the master branch::

    git clone https:://github.com/Vignesh2208/Kronos.git

* Compile and configure Kronos kernel patch::
 
    cd ~/Kronos && sudo make setup_kernel

  During the setup process do not allow kexec tools to handle kernel reboots.
  Over the course of kernel setup, a menu config would appear. 

  The following additional config steps should also be performed inside menuconfig:

  Under General setup 
		     -->  Append a local kernel version name. (e.g it could be "-ins-VT")
  Under kernel_hacking 
		     --> enable Collect kernel timers statistics
  Under Processor types and features 
                     --> Transparent Huge Page support 
                                                      --> Transparent Huge Page support sysfs defaults should be set to always

* Reboot the machine and into the new kernel (identifiable by the appended local kernel version name in the previous step)

* Build and load Kronos module::
 
    cd ~/Kronos && sudo make build load

Verifying Installation
----------------------

The following tests (optional) can run to verify the Kronos installation:

* INS-SCHED specific test::
    
    cd ~/Kronos/src/tracer/tests && sudo make run_repeatability_test

* Kronos integration tests::

    cd ~/Kronos/tests && sudo make run

All of the above tests should print a SUCCESS message.

Loading Kronos
^^^^^^^^^^^^^^

Inorder to use Kronos, it must be loaded after being built and after each VM/machine reboot. It can be loaded with the following command::

  cd ~/Kronos && sudo make load


Installing Melody
^^^^^^^^^^^^^^^^^
Melody depends on the following packages and tools:

* python-httplib2
* python-ryu-4.0
* numpy
* pypcapfile
* openssh-server
* dpkt 
* mininet
* openvswitch-2.4.0
* protobuf && protoc version >= 3.7
* grpcio and grpcio tools
* Kronos
* Matpower

It may be installed before/after Kronos installation. Please follow the steps given below to download and install melody and its dependencies. It is preferable to install Melody in the /home/${user} directory::

  cd ~/ && git clone https://github.com/Vignesh2208/Melody.git
  cd ~/Melody
  sudo ./install_deps.sh
  sudo make install

* Install Matpower by following instructions listed `here`_.

.. _here: https://github.com/MATPOWER/matpower/blob/master/README.md

* After installation of Melody, please reboot the VM/machine


  
