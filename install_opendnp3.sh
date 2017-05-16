pushd ~/Downloads 
git clone https://github.com/gec/dnp3.git
cd dnp3/
autoreconf -i -f
mkdir build
cd build
sudo apt-get install libboost-all-dev
sudo apt-get install swig
../configure --with-boost-libdir=/usr/lib/x86_64-linux-gnu --with-python
make -j16
sudo make install
