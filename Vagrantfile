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
      # The grsec build playbook defaults to patching
      # and building the vanilla kernel. Building for
      # Ubuntu hosts requires a few tricks, so enable them.
      ansible.extra_vars = {
        'grsecurity_build_strategy' => 'vanilla',
      }
    end

    build.vm.provider "virtualbox" do |v|
      v.name = "grsec-build"
      v.memory = 2048
    end
  end
end
