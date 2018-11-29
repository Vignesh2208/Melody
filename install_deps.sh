#!/bin/bash

echo "#############################################################################"
echo "Installing python packages"
echo "#############################################################################"

sudo apt-get -y install python-pip
sudo apt-get -y install libpcap-dev
sudo apt-get -y install python-httplib2
sudo apt-get -y install python-paramiko
sudo pip install ryu==4.0
sudo pip install numpy
sudo pip install pypcapfile
sudo pip install dpkt
sudo pip install pcapy
sudo pip install six==1.9.0
sudo pip install networkx

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
git checkout 2.2.1
./util/install.sh -fnv
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

echo "#############################################################################"
echo "Setting up openvswitch"
echo "#############################################################################"

sudo cp -v start-ovs.sh ~/Downloads/openvswitch-2.4.0/
#sudo chmod +x ~/Downloads/openvswitch-2.4.0/start-ovs.sh
sudo sed "s/@HOME@/${HOME//\//\\/}/g" start_ovs.sh.template > start_ovs.sh
sudo cp -v start_ovs.sh /etc/init.d/
sudo rm start_ovs.sh
sudo chmod +x /etc/init.d/start_ovs.sh
sudo update-rc.d start_ovs.sh defaults
