#!/bin/bash
# Author: Ryan Hartje
# github.com/ryanhartje

yum install -y syslinux xinetd dhcp tftp-server;

# Set these variables if you wish to change where your files reside (untested)
tftp_dir="/tftp/";
centos_dir="$tftp_dir/images/centos";
ubuntu_dir="$tftp_dir/images/ubuntu";
debian_dir="$tftp_dir/images/debian";

# Get folders set up for different distributions
mkdir -vp $tftp_dir\images/centos/;
mkdir -vp $tftp_dir\images/ubuntu/;
mkdir -vp $tftp_dir\images/debian/;

# Let's get our Pxe files copied into the right place
cp -v /usr/share/syslinux/{pxelinux.0,menu.c32} $tftp_dir;
mkdir -v $tftp_dir\pxelinux.cfg;

# I found the following mirrors that work well for me:
# Centos 6.5 - http://mirror.rackspace.com/CentOS/6.5/isos/x86_64/CentOS-6.5-x86_64-minimal.iso
# Ubuntu 14LTS Trusty Tahr - http://releases.ubuntu.com/14.04/ubuntu-14.04-server-amd64.iso
# Debian 7 Wheezy - http://ftp.utexas.edu/debian-cd/7.4.0/amd64/iso-cd/debian-7.4.0-amd64-kde-CD-1.iso 

while true; do
  read -p "Do you want a copy of Centos 6.5? [y/n]" input;
  case $input in
    [Yy]* ) cd /tftp/images/centos; wget http://mirror.rackspace.com/CentOS/6.5/isos/x86_64/CentOS-6.5-x86_64-minimal.iso; mkdir /tmp/mount; mount -o loop $tftp_dir\image/centos/CentOS-6.5-x86_64-minimal.iso /tmp/mount; cp -v /tmp/mount/images/{vmlinuz,initrd.img} $tftp_dir\images/centos/; echo "Centos Installed"; break; # We will add sanity checking to ensure everything downloaded correctly in the future. 
    [Nn]* ) break;
esac;
done;   

echo "end of script";
