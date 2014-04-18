#!/bin/bash
# Author: Ryan Hartje
# github.com/ryanhartje

yum install -y syslinux xinetd dhcp tftp-server;

# Set these variables if you wish to change where your files reside (untested)
# Please be sure to place your web root here
webroot="/usr/share/nginx/html/";
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

# Case example http://stackoverflow.com/questions/226703/how-do-i-prompt-for-input-in-a-linux-shell-script

while true; do
  read -p "Do you want a copy of Centos 6.5? [y/n]" input;
  case $input in
    [Yy]* ) centos=1; cd $tftp_dir\images/centos; if [ ! -f $tftp_dir\images/centos/CentOS-6.5-x86_64-minimal.iso ]; then wget http://mirror.rackspace.com/CentOS/6.5/isos/x86_64/CentOS-6.5-x86_64-minimal.iso; fi; mkdir /tmp/mount; mount -o loop $tftp_dir\images/centos/CentOS-6.5-x86_64-minimal.iso /tmp/mount; cp -v /tmp/mount/images/pxeboot/{vmlinuz,initrd.img} $tftp_dir\images/centos/; echo "Centos Installed"; break;; # We will add sanity checking to ensure everything downloaded correctly in the future. 
    [Nn]* ) exit;;
    * ) echo "Please enter either y or n";;
esac;
done;   

# Copy over the sample dhcpd conf, backup the current one first.
if [ -f /etc/dhcp/dhcpd.conf ]; 
  then mv /etc/dhcp/dhcpd.conf{,.backup};
fi;

cp /usr/share/doc/dhcp*/dhcpd.conf.sample /etc/dhcp/dhcpd.conf

# Set up PXE directives in dhcpd.conf 
if [ -z $(grep -i "allow booting" /etc/dhcp/dhcpd.conf) ]; 
  then echo "allow booting" >> /etc/dhcp/dhcpd.conf; 
fi; 

if [ -z $(grep -i "allow bootp" /etc/dhcp/dhcpd.conf) ]; 
  then echo "allow bootp" >> /etc/dhcp/dhcpd.conf; 
fi; 

# Turn on tftp in xinetd and restart the xinetd service
sed -ie "$(grep -n disable /etc/xinetd.d/tftp|awk -F: '{print $1}')s/yes/no/g" /etc/xinetd.d/tftp;
service xinetd restart;

# Add a default menu 
my_ip=$(ifconfig|grep "inet addr"|egrep -v "127.0.0.1"|awk -F: '{print $2}'|awk '{print $1}');
cat > $tftp_dir\pxelinux.cfg/default << "EOF"
default menu.c32
prompt 0
timeout 100
ontimeout local
MENU TITLE Pxe4Me
LABEL local
  MENU LABEL Boot from HD
  LOCALBOOT 0 

LABEL Centos 6.5 x86_64
  KERNEL images/centos/vmlinuz
  APPEND initrd=images/centos/initrd.img #ks=http://$my_ip/kickstart.cfg
EOF

# Setup the default kickstart to automate installs (later)

echo "end of script";
