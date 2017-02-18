#!/bin/bash

username=$1
password=$2
host=$3

PID=$$
ParPID=`ps -fp $PID | awk "/$PID/"' { print $3 } '`
GPPID=`ps -fp $ParPID | awk "/$ParPID/"' { print $3 } '`

echo "MY PID = " $$
echo "MY PARENT PID = " $ParPID
echo "MY GRAND PARENT PID = " $GPPID

#while :
#do

#	sleep 1
#done


echo "Sending Ping !!"
date +%s
ping -c1 $host -q
echo "Received Ping !!"
date +%s
