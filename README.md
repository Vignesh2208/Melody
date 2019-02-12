A TestBed which integrates PowerWorld/RTDS with Mininet to simulate a
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
#grpc
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

    - Do the following
      sudo visudo
      
      -Append this line
      Defaults env_keep += "PYTHONPATH"

```
