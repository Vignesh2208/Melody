A TestBed which integrates PowerWorld/RTDS with Mininet to simulate a
Micro Grid control Architecture. This TestBed will be used for 
Anomaly Detection Purposes.

```
Dependencies:

#python-httplib2
#ryu
#python 2.7
```

```
Pre-Run Steps:

- Install shared buffer python IPC (for python 2.7)
    - cd NetPower_Testbed/src/Proxy/libs
    - sudo python setup.py build_ext --inplace
```