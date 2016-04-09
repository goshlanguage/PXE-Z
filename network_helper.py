"""
Network Helper - a set of network tools for getting network related data from the system
"""
import fcntl
import socket
import struct
from os import listdir
from urllib2 import urlopen


def get_interfaces():
    """
    :return list of system's interfaces
    """
    net_list = os.listdir('/sys/class/net/')
    try:
        net_list.remove('lo')
    except ValueError:
        pass
    return net_list


def get_valid_interfaces():
    ifaces = get_interfaces()
    valid_list = []
    for i in ifaces:
        try:
            get_private_ip(i)
        except:
            continue
        valid_list.append(i)
    return valid_list


def get_subnet(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x891b,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

    return subnet


def get_public_ip():
    """
    Get public IP (outside NAT)
    """
    canhaz = urlopen("http://icanhazip.com")
    ip = canhaz.read().split("\n")[0]
    return ip


def get_private_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])



