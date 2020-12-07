#!/usr/bin/env python
"""
PXE-Z - A tool to install and configure a PXE server, and add/remove images.
https://github.com/ryanhartje/PXE-Z
"""

import argparse
import logging
import subprocess
import sys
from platform import linux_distribution

import isotool
import network_helper


def prompt(prompt):
    # Raw input varies between Python 2 and 3
    user_input = None
    if sys.version_info > (3, 0):
        user_input = input(prompt)
    else:
        user_input = raw_input(prompt)
    return user_input


def detect_os():
    """
    :return dist() - returns platform.dist() list [os, version, dist_name]
    """
    distro = linux_distribution()
    return distro[0].lower()


def distro_valid():
    """
    :return True/False based on if we support the distro
    """
    distro = detect_os()
    LOG.debug("Operating System Detected: %s", distro)
    supported = ['centos', 'centos linux', 'debian', 'ubuntu', 'redhat']
    if not distro or distro not in supported:
        raise Exception("Operating System not supported")
    return True


def get_banner():
    """
    """
    banner = """          _      _   __
         |_) \/ |_    /
         |   /\ |_   /_   v0.1
    """

    return banner


def get_images():
    """
    Prompt the user for the images they wish to select
    """
    images = [
        {'id': 1, 'name': 'Centos 7', 'type': 'iso',
         'url': 'http://yum.tamu.edu/centos/7/isos/x86_64/CentOS-7-x86_64-NetInstall-1511.iso'},
        {'id': 2, 'name': 'Ubuntu 14.04', 'type': 'tar',
         'url': 'http://archive.ubuntu.com/ubuntu/dists/trusty-updates/main/installer-amd64/'
                'current/images/netboot/netboot.tar.gz'},
        {'id': 3, 'name': 'Debian Jessie 8.4', 'type': 'iso',
         'url': 'http://cdimage.debian.org/debian-cd/10.7.0/amd64/iso-cd/'
                'debian-10.7.0-amd64-netinst.iso'},
        {'id': 4, 'name': 'Kali Linux 2016.1', 'type': 'iso',
         'url': 'http://cdimage.kali.org/kali-2016.1/kali-linux-2016.1-amd64.iso'},
        {'id': 5, 'name': 'Gparted', 'type': 'iso',
         'url': 'http://downloads.sourceforge.net/gparted/gparted-live-0.25.0-3-i686.iso'},
        {'id': 6, 'name': 'CoreOS', 'type': 'iso',
         'url': 'https://stable.release.core-os.net/amd64-usr/current/coreos_production_iso_image.iso',
         'extra_files': [
            'http://stable.release.core-os.net/amd64-usr/current/coreos_production_pxe_image.cpio.gz',
            'http://stable.release.core-os.net/amd64-usr/current/coreos_production_pxe_image.cpio.gz.sig'
         ]
        }
    ]
    return images


def get_image_url(id):
    images = get_images()
    for image in images:
        if image['id'] == id:
            return image['url']
    return None


def get_image_name(id):
    images = get_images()
    for image in images:
        if image['id'] == id:
            return image['name']
    return None


def get_user_image_selection():
    """
    """
    print("Please enter the number(s) corresponding to which images you want to use, separated "
          "by commas\n"
          "eg: 1, 5, 6\n"
          "Images\n"
          "------\n")
    for image in get_images():
        print("%s - %s" % (image['id'], image['name']))

    # We may have to help the user, so lets make a loop that repeats if images is empty
    #   We will set images to empty if we have non valid text too.
    user_images = []
    while not user_images:
        user_images = prompt("Images: ")
        if not user_images:
            print("Please select an image")

        user_images = user_images.split(',')

    return user_images


def get_network_settings():
    """
    """
    ifaces = network_helper.get_valid_interfaces()
    suggested_ip = network_helper.get_private_ip(ifaces[0])
    user_ip = prompt("Please enter IP [leave blank for: %s]: " % suggested_ip)
    if not user_ip:
        user_ip = suggested_ip

    suggested_subnet = network_helper.get_subnet(ifaces[0])
    user_subnet = prompt("Please enter subnet [leave blank for: %s]: " % suggested_subnet)
    if not user_subnet:
        user_subnet = suggested_subnet

    network_id = network_helper.get_network_id(user_ip, user_subnet)

    return user_ip, user_subnet, network_id


def get_settings():
    """
    This function should detect the current NAT or Network, and provide them to the user
        as defaults for network configuration
    This function should also allow the user a mechanism of configuring:
        * ISOs they want to setup
        * Title for PXE screen,
        * Background URL for PXE screen,
        * Option to install nginx as HTTP server for Kickstart and Preseed scripts,
    """
    image_list = get_user_image_selection()

    title = prompt("Please enter your PXE boot title message: ")
    ip, subnet, network_id = get_network_settings()
    first, last = network_helper.get_network_range(ip, subnet)
    settings = {'image_list': image_list,
                'title': title,
                'ip': ip,
                'subnet': subnet,
                'network_id': network_id,
                'first': first,
                'last': last
                }
    return settings


def get_default(settings):
    default = """
default menu.c32
prompt 0
timeout 300
ONTIMEOUT local
menu title ########## %s ##########
label 1
menu label ^1) Boot from local drive localboot
    """ % (settings['title'])
    count = 2
    for id in settings['image_list']:
        name = get_image_name(int(id))
        path_name = isotool.get_iso_name(get_image_url(int(id)))
        if name == "CoreOS":
            entry = """label %s
    menu label ^%s) %s
    kernel images/%s/vmlinuz
    initrd images/%s/coreos_production_pxe_image.cpio.gz
    append coreos.config.url=http://%s/pxe-config.ign
    """ % (count, count, name, path_name, path_name,
                         network_helper.get_public_ip())
            default = default + entry
        else:
            entry = """label %s
    menu label ^%s) %s
    kernel images/%s/vmlinuz
    append initrd=images/%s/initrd.img
    """ % (count, count, name, path_name, path_name)
            default = default + entry
    count = count + 1
    return default


def get_dhcpd_conf(settings):
    dhcpd_conf = """allow booting;
allow bootp;
option option-128 code 128 = string;
option option-129 code 129 = text;
default-lease-time 600;
max-lease-time 7200;
authoritative;
log-facility local7;

subnet %s netmask %s {
        option routers                  %s;
        option subnet-mask              %s;
        option domain-name-servers      8.8.8.8, 8.8.4.4;
        option time-offset              -18000;     # Eastern Standard Time
	range   %s   %s;
}

next-server %s;
filename "pxelinux.0";
    """ % (settings['network_id'],
           settings['subnet'],
           settings['first'],
           settings['subnet'],
           settings['first'],
           settings['last'],
           settings['ip']
           )
    return dhcpd_conf


def rhel_install(settings):
    """
    Run yum and install our dependencies and services for running a PXE service
    :param settings - user selected settings
    """
    update_cache = "yum update".split()
    add_epel_repo = "yum install -y epel-release".split()
    install_cmd = [
        "yum", "install", "-y",
        "xinetd",
        "dhcp",
        "nginx",
        "tftp-server",
        "syslinux"
    ]
    epel_process = subprocess.Popen(
                                        add_epel_repo,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE
    )
    install_process = subprocess.Popen(
                                        install_cmd,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE
    )
    subprocess.call(update_cache)
    epel_process.communicate()
    subprocess.call(update_cache)
    out, err = install_process.communicate()

    LOG.info("Package installation for RHEL:\n%s", out)
    return True


def debian_install(settings):
    """

    :param settings:
    :return:
    """
    return None


def setup_tftp():
    """
    sed replace disable yes with disable no to start tftp server with xinetd
    """
    try:
        tftp_conf = None
        with open('/etc/xinetd.d/tftp', 'r') as file:
            tftp_conf = file.read()

        tftp_conf = tftp_conf.replace('disable\t\t\t= yes', 'disable\t\t\t= no')

        with open('/etc/xinetd.d/tftp', 'w') as file:
            file.write(tftp_conf)
        enable_cmd = "service xinetd enable".split()
        subprocess.call(enable_cmd)
        return True
    except:
        return False

def setup_iptables():
    """
    Setup the necessary rules for iptables
    """
    tftp_process = "iptables -I INPUT -p udp --dport 69 -j ACCEPT".split()
    subprocess.call(tftp_process)

def downloads(settings):
    user_images = settings['image_list']
    images = get_images()

    for id in user_images:
        index = int(id)-1
        url = get_image_url(int(id))
        isotool.setup(url)
        if hasattr(images[index], "extra_files"):
            isotool.get_extra_files(
                images[index]['name'],
                images[index]['extra_files']
            )

def setup_dhcpd(settings):
    """
    """
    dhcp_conf = get_dhcpd_conf(settings)
    with open('/etc/dhcp/dhcpd.conf', 'w') as file:
        file.write(dhcp_conf)
    enable_cmd = "chkconfig dhcpd on".split()
    start_cmd = "service dhcpd start".split()
    subprocess.call(enable_cmd)
    subprocess.call(start_cmd)

    return True

def setup_nginx():
    enable_cmd = "chkconfig nginx on".split()
    start_cmd =  "service nginx start".split()
    subprocess.call(enable_cmd)
    subprocess.call(start_cmd)

def install():
    """
    This method invokes the appropriate script to install services based on if the underlying distro
        is RHEL or Debian based.
    """
    distro = detect_os()
    settings = get_settings()
    print(settings)

    print("Installing services and dependencies...")
    if distro in ["redhat", "centos", "centos linux"]:
        rhel_install(settings)
    elif distro in ["ubuntu", "debian"]:
        debian_install(settings)

    print("Copying TFTP files")
    # we use the binary itself because most RHEL systems alias cp to cp -i, meaning -f wont
    #    force it to copy, resulting in failure if the files are already there.
    cp_cmd = ["/bin/cp", "-f", "/usr/share/syslinux/pxelinux.0",
              "/usr/share/syslinux/menu.c32",
              "/usr/share/syslinux/memdisk",
              "/usr/share/syslinux/mboot.c32",
              "/usr/share/syslinux/chain.c32",
              "/var/lib/tftpboot/"]
    cp_process = subprocess.call(cp_cmd)
    if cp_process != 0:
        print " ".join(cp_cmd)
        raise Exception("Could not copy syslinux files from /usr/share/syslinux/ to /var/lib/tftpboot.\n"
                        "Please check that the folders exist, and that there files in /usr/share/syslinux")

    print("Setting up TFTP")
    setup_tftp()

    print("Creating /var/lib/tftpboot/pxelinux.cfg folder")
    mkdir_cmd = ["mkdir", "-p", "/var/lib/tftpboot/pxelinux.cfg"]
    subprocess.call(mkdir_cmd)

    print("Downloading Images and other files.")
    downloads(settings)


    print("Creating /var/lib/tftpboot/pxelinux.cfg/default config")
    with open('/var/lib/tftpboot/pxelinux.cfg/default', 'w+') as cfg:
        cfg.write(get_default(settings))

    print("Setting ownership on /var/lib/tftpboot")
    chown_process = "chown -R nobody. /var/lib/tftpboot".split()
    subprocess.call(chown_process)

    print("Starting TFTP")
    start_cmd = "service xinetd start".split()
    subprocess.call(start_cmd)

    print("Configuring DHCPD")
    setup_dhcpd(settings)

    print("Starting Nginx")
    setup_nginx()

def main():
    """
    """
    print(get_banner())
    install()

    return 0


if __name__ == "__main__":
    logging.basicConfig(filename="./pxe-z.log", level=logging.INFO)
    LOG = logging.getLogger(__name__)

    PARSER = argparse.ArgumentParser(description='PXE-Z is a tool for installing and '
                                                 'configuring PXE servers.')
    PARSER.add_argument('install',
                        action="store_true",
                        default=False,
                        help="Install PXE and dependencies")
    PARSER.add_argument('--config',
                        action="store_true",
                        default=False,
                        help="Configure PXE environment")
    PARSER.add_argument('--network',
                        action="store_true",
                        default=False,
                        help="Configure PXE Networking")
    ARGS = PARSER.parse_args()

    if distro_valid():
        main()
