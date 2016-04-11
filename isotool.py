"""

"""
import os
import urllib2
from subprocess import call


def get_iso_name(iso):
    iso_name_list = iso.split('/')
    iso_name = iso_name_list[-1]
    iso_name = iso_name.split(".iso")[0]
    return iso_name


def get_iso_path(iso):
    return "/tmp/%s" % iso.split('/')[-1]


def download_iso(iso_url):
    iso_file = urllib2.urlopen(iso_url)
    iso_path = get_iso_name(iso_url)
    with open(iso_path, 'wb') as output:
        output.write(iso_file.read())
    return iso_path


def mount_iso(iso_path):
    """
    """
    iso_name = get_iso_name(iso_path)
    mkdir_cmd = "mkdir /tmp/%s" % iso_name
    call(mkdir_cmd.split())
    mount_cmd = ["mount", "-o", "loop", iso_path, "/tmp/%s" % iso_name]
    call(mount_cmd)


def unmount_iso(iso_path):
    """
    """
    iso_name = get_iso_name(iso_path)
    directory = "/tmp/%s" % iso_name
    umount_cmd = ["umount", directory]
    call(umount_cmd)


def find_files(path):
    """
    This helper is responsible for finding vmlinux and initrd.img
    """
    pxe_files = []
    for match in ['vmlinuz', 'initrd.img']:
        for root, dirs, files in os.walk(path):
            if match in files:
                pxe_files.append(os.path.join(root, match))
    return pxe_files


def setup(iso_url):
    if not os.path.exists(get_iso_path(iso_url)):
        path = download_iso(iso_url)
    else:
        path = get_iso_path(iso_url)
    mount_iso(path)
    mkdir_process = "mkdir -p /var/lib/tftpboot/images/%s" % get_iso_name(path)
    call(mkdir_process.split())
    files = find_files("/tmp/%s" % get_iso_name(iso_url))
    for file in files:
        cp_process = "cp -v %s /var/lib/tftpboot/images/%s/" % (file, get_iso_name(path))
        call(cp_process.split())
    unmount_iso(path)
