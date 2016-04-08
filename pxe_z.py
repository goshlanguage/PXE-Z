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
    supported = ['centos', 'debian', 'ubuntu', 'redhat']
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
         'url': 'http://cdimage.debian.org/debian-cd/8.4.0/amd64/iso-cd/'
                'debian-8.4.0-amd64-netinst.iso'},
        {'id': 4, 'name': 'Kali Linux 2016.1', 'type': 'iso',
         'url': 'http://cdimage.kali.org/kali-2016.1/kali-linux-2016.1-amd64.iso'}
        ]
    return images


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
        # Raw input varies between Python 2 and 3
        if sys.version_info > (3, 0):
            user_images = input("Images: ")
        else:
            user_images = raw_input("Images: ")

        if not user_images:
            print("Please select an image")

        user_images = user_images.split(',')

    return user_images


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

    settings = {'image_list': image_list}
    return settings


def get_default(settings):
    default = """
default menu.c32
prompt 0
timeout 300
ONTIMEOUT local
menu title ########## PXE Boot Menu ##########
label 1
menu label ^1) Install CentOS 7
kernel centos7_x64/images/pxeboot/vmlinuz
append initrd=centos7_x64/images/pxeboot/initrd.img method=http://192.168.1.150/centos7_x64 devfs=nomount
label 2
menu label ^2) Boot from local drive localboot
    """
    return default


def rhel_install(settings):
    """
    Run yum and install our dependencies and services for running a PXE service
    :param settings - user selected settings
    """
    install_cmd = ["yum", "install", "-y", "xinetd", "dhcpd", "tftp-server", "syslinux"]
    install_process = subprocess.Popen(install_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = install_process.communicate()
    return_code = install_process.returncode

    LOG.info("Package installation for RHEL:\n%s", out)

    if return_code != 0:
        LOG.fatal("FATAL - pacakges failed to install\n------\n%s", err)
        raise Exception("Failed to install packages:\n %s" % err)

    return True


def debian_install(settings):
    """

    :param settings:
    :return:
    """
    print(settings)


def update_tftp_conf():
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
        return True
    except:
        return False


def install():
    """
    This method invokes the appropriate script to install services based on if the underlying distro
        is RHEL or Debian based.
    """
    distro = detect_os()
    settings = get_settings()
    print(settings)

    print("Installing services and dependencies...")
    if distro in ["redhat", "centos"]:
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

    print("Updating /etc/xinetd.d/tftp")
    update_tftp_conf()

    print("Creating /var/lib/tftpboot/pxelinux.cfg folder")
    mkdir_cmd = ["mkdir", "-p", "/var/lib/tftpboot/pxelinux.cfg"]
    subprocess.call(mkdir_cmd)

    print("Creating /var/lib/tftpboot/pxelinux.cfg/default config")
    with open('/var/lib/tftpboot/pxelinux.cfg/default', 'w+') as cfg:
        cfg.write(get_default(settings))



def config():
    """
    """
    print("configuratin")


def main():
    """
    """
    print(get_banner())
    install()

    return 0


if __name__ == "__main__":
    logging.basicConfig(filename="./pxe-z.log", level=logging.INFO)
    LOG = logging.getLogger(__name__)

    PARSER = argparse.ArgumentParser(description='PXE-Z is a tool for installing and '\
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
