#!/bin/bash
# Author: Ryan Hartje
# github.com/ryanhartje

yum install -y syslinux xinetd dhcp tftp-serveri wget;

# Set these variables if you wish to change where your files reside (untested)
# Please be sure to place your web root here
webroot="/usr/share/nginx/html/";
tftp_dir="/var/lib/tftpboot/";
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
# Centos 7 NETBOOT - http://mirror.utexas.edu/centos/7/os/x86_64/isolinux/
# Ubuntu 14LTS Trusty Tahr - http://releases.ubuntu.com/14.04/ubuntu-14.04-server-amd64.iso
# Ubuntu 14LTS NETBOOT - http://mirror.utexas.edu/ubuntu/dists/trusty/main/installer-amd64/current/images/netboot/
# Debian 7 Wheezy - http://ftp.utexas.edu/debian-cd/7.4.0/amd64/iso-cd/debian-7.4.0-amd64-kde-CD-1.iso 
# Debian 8 Jessie - http://mirror.utexas.edu/debian/dists/jessie/main/installer-amd64/current/images/netboot/



# Case example http://stackoverflow.com/questions/226703/how-do-i-prompt-for-input-in-a-linux-shell-script

while true; do
  #read -p "Do you want a copy of Centos 6.5? [y/n] " input;
  case $input in
    #[Yy]* ) centos=1; cd $tftp_dir\images/centos; if [ ! -f $tftp_dir\images/centos/CentOS-6.5-x86_64-minimal.iso ]; then wget http://mirror.rackspace.com/CentOS/6.5/isos/x86_64/CentOS-6.5-x86_64-minimal.iso; fi; mkdir /tmp/mount; mount -o loop $tftp_dir\images/centos/CentOS-6.5-x86_64-minimal.iso /tmp/mount; cp -v /tmp/mount/images/pxeboot/{vmlinuz,initrd.img} $tftp_dir\images/centos/; echo "Centos Installed"; break;; # We will add sanity checking to ensure everything downloaded correctly in the future. 
    [Yy]* ) centos=1; cd $tftp_dir\images/centos; if [ ! -f $tftp_dir\images/centos/isolinux ]; then wget http://mirror.utexas.edu/centos/7/os/x86_64/isolinux/vmlinuz; wget http://mirror.utexas.edu/centos/7/os/x86_64/isolinux/initrd.img; fi; break;; # We will add sanity checking to ensure everything downloaded correctly in the future. 
    [Nn]* ) break;;
    * ) echo "Please enter either y or n";;
esac;
done;   

my_ip=$(ifconfig|grep "inet addr"|egrep -v "127.0.0.1"|awk -F: '{print $2}'|awk '{print $1}'|head -1);

# Copy over the sample dhcpd conf, backup the current one first.
echo "Setting up dhcpd... ";
read -p "What is your network address (ex: 192.168.0.0): " dhcp;
read -p "What is your network mask (ex: 255.255.255.0): " netmask;
read -p "What is your gateway (ex: 192.168.0.1): " gateway;
read -p "What is your domain name (ex: myhouse.com): " domain;
read -p "Please enter your IP range (ex: 192.168.1.1 192.168.1.100): " range;
read -p "Please enter your TFTP server IP (ex: 192.168.1.1): " next_server;
# should we add nameservers?

# If we got any blank responses back
if [ -z $dhcp ];
  then dhcp=192.168.1.0;
fi;

if [ -z $netmask ];
  then netmask=255.255.255.0;
fi; 

if [ -z $gateway ];
  then gateway=192.168.1.1;
fi; 

if [ -z $domain ];
  then domain="domain.com";
fi; 

if [ -z $range ];
  then range="192.168.1.1 192.168.1.255";
fi;

if [ -z $next_server ];
  #then range="192.168.1.1 192.168.1.255";
  then next_server=$my_ip; 
fi;

# Backup any existing dhcpd configurations
if [ -f /etc/dhcp/dhcpd.conf ]; 
  then mv /etc/dhcp/dhcpd.conf{,.backup};
fi;

# The example takes a lot of configuration, but if you need more control over DHCP use
# cp /usr/share/doc/dhcp*/dhcpd.conf.sample /etc/dhcp/dhcpd.conf
# then configure as you wish.

# This is the most simplistic setup for DHCP. 
# Should work fine with existing networks, as dhcp will not lease out a used ip
# Report bugs at https://github.com/RyanHartje/pxe4Centos/issues

cat > /etc/dhcp/dhcpd.conf << EOF
ddns-update-style interim;
ignore client-updates;
ddns-domainname "$domain.";
ddns-rev-domainname "in-addr.arpa.";
allow booting;
allow bootp;

subnet $dhcp netmask $netmask {
        option domain-name              "$domain";
        option routers                  $gateway;
        option subnet-mask              $netmask;
        option domain-name-servers      8.8.8.8,8.8.4.4;
        range dynamic-bootp             $range;
        default-lease-time              10800;
        max-lease-time                  10800;
      next-server $next_server;
      filename "pxelinux.0";
}
EOF

# Set up PXE directives in dhcpd.conf 
#if [ -z $(grep -i "allow booting" /etc/dhcp/dhcpd.conf) ]; 
#  then echo "allow booting" >> /etc/dhcp/dhcpd.conf; 
#fi; 
#
#if [ -z $(grep -i "allow bootp" /etc/dhcp/dhcpd.conf) ]; 
#  then echo "allow bootp" >> /etc/dhcp/dhcpd.conf; 
#fi; 

# Turn on tftp in xinetd and restart the xinetd service
sed -ie "$(grep -n disable /etc/xinetd.d/tftp|awk -F: '{print $1}')s/yes/no/g" /etc/xinetd.d/tftp;
sed -ie "$(grep -n server_args /etc/xinetd.d/tftp|awk -F: '{print $1}')s|/var/lib/tftpboot|$tftp_dir|g" /etc/xinetd.d/tftp;
service xinetd restart;

# Add a default menu 
cat > $tftp_dir\pxelinux.cfg/default << "EOF"
default menu.c32
prompt 0
timeout 100
ontimeout local
MENU TITLE Pxe4Me
LABEL local
  MENU LABEL Boot from HD
  LOCALBOOT 0 

LABEL Centos 7 x_86_64
  KERNEL images/centos/vmlinuz
  APPEND initrd=images/centos/initrd.img #ks=http://$my_ip/kickstart.cfg

EOF
#LABEL Centos 6.5 x86_64
#  KERNEL images/centos/vmlinuz
#  APPEND initrd=images/centos/initrd.img #ks=http://$my_ip/kickstart.cfg


# Be sure to open the firewall where necessary
iptables -I INPUT -p udp --dport 69 -j ACCEPT
service iptables save;

# Setup chkconfig so that our services stay on
chkconfig xinetd on;
chkconfig dhcpd on;

service xinetd restart;
service dhcpd restart;

tail -15 /var/log/messages;

# Setup the default kickstart to automate installs (later)

echo "end of script";
