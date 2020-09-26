#!/bin/bash

echo "#############################################################################"
echo "Installing python packages"
echo "#############################################################################"

sudo apt-get -y install python3-pip
sudo apt-get -y install python3-dev
sudo apt-get -y install libyaml-dev
sudo apt-get -y install libpcap-dev
sudo apt-get -y install python3-httplib2
sudo apt-get -y install python3-paramiko
sudo python -m pip install ryu
sudo python -m pip install numpy
sudo python -m pip install pypcapfile
sudo python -m pip install dpkt
sudo python -m pip install pcapy
sudo python -m pip install six==1.9.0
sudo python -m pip install networkx==2.3.0
sudo python -m pip install pandas
sudo python -m pip install plotly
sudo python -m pip install -U pexpect
sudo apt-get -y install inetutils-ping
sudo apt-get -y install openssh-server
sudo apt-get -y install expect
sudo ufw disable

echo "#############################################################################"
echo "Setting up mininet"
echo "#############################################################################"

pushd ~/Downloads
git clone https://www.github.com/mininet/mininet.git
pushd mininet
git checkout 2.3.0d6
sudo ./util/install.sh -fnv
popd
popd


echo "#############################################################################"
echo "Building openvswitch"
echo "#############################################################################"

sudo apt-get -y purge openvswitch-common

pushd ~/Downloads

wget http://openvswitch.org/releases/openvswitch-2.4.0.tar.gz
tar -xzvf openvswitch-2.4.0.tar.gz
pushd openvswitch-2.4.0
sudo ./configure
sudo make
sudo make install
sudo make modules_install
sudo /sbin/modprobe openvswitch
popd
popd

#sudo apt-get -y install openvswitch-switch

echo "#############################################################################"
echo "Setting up openvswitch"
echo "#############################################################################"

sudo sed "s/@HOME@/${HOME//\//\\/}/g" start_ovs.sh.template > start_ovs.sh
sudo cp -v start_ovs.sh /etc/init.d/
sudo rm start_ovs.sh
sudo chmod +x /etc/init.d/start_ovs.sh
sudo update-rc.d start_ovs.sh defaults
sudo /etc/init.d/start_ovs.sh

echo "#############################################################################"
echo "Setting up Octave"
echo "#############################################################################"
sudo add-apt-repository ppa:octave/stable
sudo apt-get update
sudo apt-get install octave

echo "#############################################################################"
echo "Setting up Protocol Buffers and GRPC tools"
echo "#############################################################################"
sudo python -m pip install protobuf==3.7.0rc2
sudo python -m pip install cython
sudo python -m pip install grpcio
sudo python -m pip install grpcio-tools
