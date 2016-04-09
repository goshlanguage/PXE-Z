"""

"""
import urllib2
from os import mkdir
from subprocess import call


def get_iso_name(iso):
    iso_name_list = iso.split('/')
    iso_name = iso_name_list[len(iso_name_list)-1]
    iso_name = iso_name.split(".iso")[0]
    return iso_name


def download_iso(iso_url):
    name = get_iso_name(iso_url)
    iso_file = urllib2.urlopen(iso_url)
    tmp_file = "/tmp/%s" % name
    with open(tmp_file, 'wb') as output:
        output.write(iso_file.read())
    return tmp_file


def mount_iso(iso):
    """
    """
    iso_name = get_iso_name(iso)
    directory = "/tmp/%s" % iso_name
    mkdir(directory)
    mount_cmd = ["mount", "-o", "loop", iso, "/tmp/%s" % iso_name]
    call(mount_cmd)


def unmount_iso(iso):
    """
    """
    iso_name = get_iso_name(iso)
    directory = "/tmp/%s" % iso_name
    umount_cmd = ["umount", "/tmp/%s" % iso_name]
    call(umount_cmd)


def setup(iso_url):
    path = download_iso(iso_url)
    mount_iso(path)

