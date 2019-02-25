A TestBed which integrates Power System Simulation with Mininet to simulate a
Micro Grid control Architecture. This TestBed will be used for 
Anomaly Detection Purposes.

```
Dependencies:

#python-httplib2
#python-ryu-4.0 or above
#ryu-bin and ryu-manager
#python 2.7
#numpy
#pypcapfile
#openssh-server
#paramiko
#dpkt
#expect 
#mininet
#openvswitch
#protobuf version >= 3.7
#grpc (sudo pip install grpcio && sudo pip install grpcio-tools)
#Kronos

```

```
Pre-Run Steps:

- Install Kronos.
- Install protobuf, protoc.
- Install grpc.

- Setup the environment
    - cd Melody
    - sudo ./install_deps.sh
    - sudo ./install_opendnp3.sh
    - sudo make install

- Setting up the python path
    - Add the following to ~/.bashrc
      export PYTHONPATH=$PYTHONPATH:<path-to-melody>/src
      export PYTHONPATH=$PYTHONPATH:<path-to-melody>/src/core
      
    - Do the following
      sudo visudo
      
      -Append this line
      Defaults env_keep += "PYTHONPATH"

```

```
TODO: the powersim case name ishardcoded for now, need to fix it
Need to change the name of mapped_powersim_entity_id
Change PSSService to remove MatPower dependency

```
