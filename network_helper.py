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
    net_list = listdir('/sys/class/net/')
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


def get_subnet_mask(subnet):
    """
    Subnets can be calculated by breaking them into binary and calculating bits
    I spent a few hours looking into it, but found it much faster to just look it up
    in a dictionary
    """
    masks = {
        '240.0.0.0': '4',
        '248.0.0.0': '5',
        '252.0.0.0': '6',
        '254.0.0.0': '7',
        '255.0.0.0': '8',
        '255.128.0.0': '9',
        '255.192.0.0': '10',
        '255.224.0.0': '11',
        '255.240.0.0': '12',
        '255.248.0.0': '13',
        '255.252.0.0': '14',
        '255.254.0.0': '15',
        '255.255.0.0': '16',
        '255.255.128.0': '17',
        '255.255.192.0': '18',
        '255.255.224.0': '19',
        '255.255.240.0': '20',
        '255.255.248.0' : '21',
        '255.255.252.0': '22',
        '255.255.254.0': '23',
        '255.255.255.0': '24',
        '255.255.255.128': '25',
        '255.255.255.192': '26',
        '255.255.255.224': '27',
        '255.255.255.240': '28',
        '255.255.255.248': '29',
        '255.255.255.252': '30',
    }

    return masks[subnet]


def get_network_id(ip, subnet):
    """
    This function will convert IP and Subnet into Binary to use bitwise
    operations to calculate the network Id
    :return network_id's IP address in decimal octets
    """
    ip_list = ip.split('.')
    subnet_list = subnet.split('.')
    network_id_list = []
    for i in range(0,4):
        int_ip = int(ip_list[i])
        int_subnet = int(subnet_list[i])
        compared = bin(int_ip & int_subnet)
        network_id_list.append(str(int(compared, 2)))

    return ".".join(network_id_list)


def get_network_range(ip, subnet):
    """
    This function will return the first and last possible IPs for
    a network to be used in DHCP configurations or wherever helpful
    """
    network_id = get_network_id(ip, subnet)
    first_list = network_id.split(".")
    first_list[3] = str(int(network_id.split(".")[3]) + 1)
    first = ".".join(first_list)

    # To find number of possible Ips, you can subtract the class in question
    #   from 256 to find number of possibilities
    num_ips = 255 - int(network_id.split(".")[3])
    print(num_ips)

    last_list = network_id.split(".")
    last_list[3] = str(int(network_id.split(".")[3]) + num_ips)
    last = ".".join(last_list)

    return first, last


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



