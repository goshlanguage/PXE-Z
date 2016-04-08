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
    banner = """
          _      _   __
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


def install():
    """
    This method invokes the appropriate script to install services based on if the underlying distro
        is RHEL or Debian based.
    """
    distro = detect_os()
    settings = get_settings()
    print(settings)
    if distro in ["redhat", "centos"]:
        rhel_install(settings)
    elif distro in ["ubuntu", "debian"]:
        debian_install(settings)


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
