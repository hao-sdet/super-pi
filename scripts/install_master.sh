#!/bin/bash

# Installing MPICH
mkdir /opt/mpi
mkdir /opt/mpi-dl
mkdir /opt/mpi-build

apt-get update
apt -y install gfortran

cd /opt/mpi-dl && wget http://www.mpich.org/static/downloads/3.3/mpich-3.3.tar.gz
tar zxvf mpich-3.3.tar.gz

cd /opt/mpi-build && /opt/mpi-dl/mpich-3.3/configure --prefix=/opt/mpi
make
make install

export PATH=$PATH:/opt/mpi/bin
mpiexec -n 1 hostname

# Installing MPI4Y
apt -y install python-pip python-dev libopenmpi-dev
cd /home/pi && wget https://bitbucket.org/mpi4py/mpi4py/downloads/mpi4py-2.0.0.tar.gz && tar -zxf mpi4py-2.0.0.tar.gz
cd mpi4py-2.0.0 && python setup.py build && python setup.py install

export PYTHONPATH=/home/pi/mpi4py-2.0.0
cd /home/pi/mpi4py-2.0.0 && mpiexec -n 4 python demo/helloworld.py
