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
#dpkt
#expect (sudo apt-get install expect)
```

```
Pre-Run Steps:

- Install expect
    - sudo apt-get install expect

- Install numpy
    - sudo pip install numpy

- Install pypcapfile
   - sudo pip install pypcapfile

- Install openssh-server
   - sudo apt-get install openssh-server

- Disable firewall (if any)
    sudo ufw disable
    
- Install shared buffer python IPC (for python 2.7)
    - cd NetPower_Testbed/src/Proxy/libs
    - sudo python setup.py build_ext --inplace
    
- Install Ryu
    - sudo pip install ryu==4.0
```
