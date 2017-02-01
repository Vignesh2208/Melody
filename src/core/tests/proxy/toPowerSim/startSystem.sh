#!/bin/bash

scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
netCfgFile=$scriptDir/netCfg.txt
logHost=$scriptDir/logHost.txt
logPowerSim=$scriptDir/logPowerSim.txt
logProxy=$scriptDir/logProxy.txt

echo "" > $logHost
echo "" > $logPowerSim
echo "" > $logProxy


echo "Starting SimPowerSim"
python simPowerSim.py >> $logPowerSim 2>&1 &


sleep 1

echo "Starting Proxy"
python $scriptDir/../../../proxy.py -c $netCfgFile -r 5 -p 127.0.0.1 >> $logProxy 2>&1 &

sleep 1

echo "Starting SimHost"
python simHost.py >> $logHost 2>&1 &



echo "See Log files for results."