# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.define 'grsec-build' do |build|
    build.vm.box = "trusty64"
    build.vm.hostname = "grsec-build"
    build.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

    build.vm.provision :ansible do |ansible|
      ansible.playbook = 'ansible/build-deb-pkg.yml'
      ansible.verbose = 'v'
      # The grsec build playbook defaults to targeting
      # the Debian kernel. Since we want packages for Ubuntu,
      # provide an extra var.
      ansible.extra_vars = {
        'target_os' => 'ubuntu',
      }
    end

    build.vm.provider "virtualbox" do |v|
      v.name = "grsec-build"
      v.memory = 2048
    end
  end
end
