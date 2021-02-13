# Getting Started
Source: https://raspberrytips.com/raspberry-pi-cluster/

## Requirements
+ 2 or more Raspberry Pi (the Raspberry Pi 3B is recommended)
+ 2 or more SD Cards
+ 5V power cables
+ A 5-ports gigabit switch to connect all Pis together
+ A Network cable for each Pi (wireless is possible, but not recommended)

## Setup
### Install Raspian OS
1. Insert the SD card then run 
```
$ diskutil list
```
2. Unmount the target disk 
```
$ diskutil unmountDisk /dev/diskN (where N is the target disk)
```
3. Copy the image
```
$ sudo dd bs=1m if=path/to/your/image.img of=/dev/rdiskN; sync (where N is the target disk)
```
4. Eject the SD card
```
$ sudo diskutil eject /dev/rdiskN (where N is the target disk)
```

### Configure the Raspberry Pi for the first time
1. Change the hostname
```
$ raspi-config > System Options > Hostname > (master)
```
2. Enable SSH
```
$ raspi-config > Interface Options > SSH > Enable
```
3. Reboot

### Install the Master Pi
Note: This installation step can take up to 30-45 minutes to complete
1. Run the installation script
```
$ cd scripts/ && chmod +x install_master.sh
$ sudo install_master.sh
```
2. Run mpiexec from anywhere, anytime
```
$ sudo nano .bashrc
```
Add these two lines to the bottom of the (bashrc) file
```
export PATH=$PATH:/opt/mpi/bin
export PYTHONPATH=/home/pi/mpi4py-2.0.0
```
3. Reboot

### Duplicate the Master Pi
!Remember to change the hostname on each new node
1. Back up the master image 
```
$ diskutil list
$ sudo dd bs=1m if=/dev/rdiskN of=master-pi.dmg (where N is the target disk)
```
2. Restore/Copy image to other sd-card 
```
$ diskutil unmountDisk /dev/diskN
$ sudo dd bs=32m if=master-pi.dmg of=/dev/rdiskN (where N is the target disk)
```

### Create an IP list
1. Connect and power up all the Pis
2. Scan for IP addresses from master
```
$ sudo apt -y install nmap
$ nmap -sP 192.168.X.*  (where X is the subnet)
```
3. Create a file to store all the Pis IP addresses
```
$ cd /home/pi
$ nano cluster
```
4. Copy all IP addresses to this file (including the masters ip)
!To keep things in order, setup static IPs on all the nodes
https://www.raspberrypi.org/documentation/configuration/tcpip/
```
192.168.1.2
192.168.1.3
192.168.1.4
...
```

### SSH Keys Exchange
!We need to allow the master node to connect to any other nodes in the cluster via SSH and each node to master (bidirectional) without using passwords. Repeat the following steps for all the nodes (including master)
1. Generate an SSH key
```
$ ssh-keygen -t rsa
```
2. Copy SSH public key to other nodes
```
$ scp /home/pi/.ssh/id_rsa.pub pi@192.168.1.N:/home/pi/<piX>.pub (where N is the target IP address, and X is the source node i.e master, pi01, pi02 , ...)
```
3. Add the copied public key to authorized_keys file
3a. Create the .ssh/authorized_keys file if not already exists
```
$ touch /home/pi/.ssh/authorized_keys
$ chmod 600 /home/pi/.ssh/authorized_keys
```
3b. Add other node's public key
```
$ cat <piX>.pub >> .ssh/authorized_keys (where X is the public key of the other node i.e master, pi01, pi02 , ...)
```
4. Test SSH without password
!Repeat this step for all the nodes
From master node
```
$ ssh pi@192.168.1.N (where N is the target IP address)
```

## Usage
!Run from the master node
1. Basic command
!The command below should print out the hostname
```
$ mpiexec -n 4 hostname
```
2. Run a python script
!Each node needs to have the same script and at the same location
```
$ mpiexec --hostfile cluster -n 6 python mpi4py-2.0.0/demo/helloworld.py
```
