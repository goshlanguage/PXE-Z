# PXE-Z

A python project that aims to quickly and easily setup PXE on RHEL and Debian systems. If you are developing or running this from Mac or Windows, be sure to first install `vagrant`, and a viable hypervisor tool such as `Virtual Box` so that you can follow the directions below.

Vagrant
====

This project includes a Vagrant file, for ease of use/development.
To get started, simply run vagrant up and ssh in:

```sh
git clone https://github.com/ryanhartje/pxe-z
cd pxe-z
vagrant up pxe
vagrant ssh pxe
```

Once you are in the VM, escalate to root and run pxe_z.py:

```sh
sudo bash
cd pxe-z
./pxe_z.py
```

If the python version is broken, there is the bash fallback:

```ssh
sudo bash
cd pxe-z
./install.sh
```

This will get you started, you can use the defaults to get setup.


Features in 0.2:
====
What's left?

- finish dhcp and tftp services install Debian
- finish configurations wizard that:
- allows users to select images for PXE w/ given URL for background
- Finish vagrant and upload to Hashicorp for ease of testing/development


Backlog
====
- setup in a container
- create unittests
- setup gitlab ci job
- add nginx installer for automation scripts
- allow users to select automation scripts
- Undo sloppy Popens instead of python libraries
- Support Debian
- GPG check all images
