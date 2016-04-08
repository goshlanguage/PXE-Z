"""
"""
from socket import gethostname, gethostbyname
from urllib2 import urlopen

def get_subnet():
    subnet = "255.255.255.0"
    return subnet

def get_public_ip():
    """
    """
    canhaz = urlopen("http://icanhazip.com")
    ip = canhaz.read().split("\n")[0]
    return ip

def get_private_ip():
    ip = gethostbyname(gethostname())
    return ip
