A TestBed which integrates Power System Simulation with Mininet to simulate a
Micro Grid control Architecture. This TestBed will be used for 
Anomaly Detection Purposes.

Full documentation can be found [here](https://melody-by-projectmoses.readthedocs.io/).

```
Dependencies:

python-httplib2
python-ryu
ryu-bin and ryu-manager
python 3.7
numpy
pypcapfile
openssh-server
paramiko
dpkt
expect 
mininet
openvswitch
protobuf version >= 3.7
grpc (sudo pip install grpcio && sudo pip install grpcio-tools)
Kronos

```

```
Pre-Run Steps:

- Install Kronos.
- Install protobuf, protoc.
- Install grpc.

- Setup the environment
    - cd Melody
    - sudo ./install_deps.sh
    - sudo python setup.py install

- Setting up the python path
    - Add the following to ~/.bashrc
      export PYTHONPATH=$PYTHONPATH:<path-to-melody>/srcs
      export PYTHONPATH=$PYTHONPATH:<path-to-melody>/srcs/proto

    - Do the following
      sudo visudo
      
      -Append this line
      Defaults env_keep += "PYTHONPATH"

```

```
Copyright (c) 2020, Information Trust Institute
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. 

```

