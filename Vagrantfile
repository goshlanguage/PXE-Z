# -*- mode: ruby -*-
# vi: set ft=ruby:
# PXE-Z Virtual Box -
#    https://github.com/ryanhartje/pxe-z

$script = <<SCRIPT

yum update
yum install -y git vim 

git clone https://github.com/ryanhartje/pxe-z
SCRIPT

Vagrant.configure(2) do |config|

  config.vm.define "pxe" do |pxe|
    pxe.vm.box = "bento/centos-6.7"

    pxe.vm.network "private_network", ip: "10.0.0.1"
    pxe.vm.network "public_network"
    pxe.vm.provider :virtualbox do |vb|
      # enable promiscuous mode on the public network
      # change allow-all to allow-vms if you indeed to test only on vms
      # [--nicpromisc<1-N> deny|allow-vms|allow-all]
      vb.customize ["modifyvm", :id, "--nicpromisc1", "allow-all"]
      vb.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]
    end
    pxe.vm.provision "shell", inline: $script  
  end

  config.vm.define "pxeclient" do |pxeclient|
    pxeclient.vm.network "private_network", ip: "10.0.1.2"
  end
    
end
