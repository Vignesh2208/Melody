#!/bin/bash

folder=$1
scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

allTapsDir=$scriptDir/microgrid_datasets/$folder/all_taps
config1Dir=$scriptDir/microgrid_datasets/$folder/tap_config_1
config2Dir=$scriptDir/microgrid_datasets/$folder/tap_config_2
config3Dir=$scriptDir/microgrid_datasets/$folder/tap_config_3


cd $allTapsDir
cp s7*s6* $config1Dir
cp s4*s5* $config1Dir
cp s1*s5* $config1Dir
cp s3*s5* $config1Dir
cp s1*s2* s4*s1* s2*s3* s3*s4* $config2Dir
cp s2*s4* s3*s4* s3*s5* s1*s3* $config3Dir


