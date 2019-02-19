#!/bin/bash
sudo mn -c
sudo killall python
sudo ifconfig connect down
sudo ifconfig h1base down
sudo ip link del h1base
sudo ifconfig h2base down
sudo ip link del h2base
sudo ifconfig h3base down
sudo ip link del h3base
sudo ifconfig h4base down
sudo ip link del h4base
sudo ifconfig h5base down
sudo ip link del h5base
sudo ifconfig base down
sudo ip link del base
sudo brctl delbr connect
sudo fuser -k 50051/tcp
