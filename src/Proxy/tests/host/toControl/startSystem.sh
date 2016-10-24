#!/bin/bash

scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
netCfgFile=$scriptDir/netCfg.txt
logHost=$scriptDir/logHost.txt
logControl=$scriptDir/logControl.txt
logProxy=$scriptDir/logProxy.txt

echo "" > $logHost
echo "" > $logControl
echo "" > $logProxy


echo "Starting SimControl"
python simControl.py >> $logControl 2>&1 &


sleep 1

echo "Starting Host"
python $scriptDir/../../../host.py -c $netCfgFile -r 5 -n test -d 1 >> $logHost 2>&1 &

sleep 1

echo "Starting SimProxy"
python simProxy.py >> $logProxy 2>&1 &



echo "See Log files for results."