# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.define 'grsec-build', primary: true do |build|
    build.vm.box = "ubuntu/trusty64"
    build.vm.hostname = "grsec-build"

    build.vm.provision :ansible do |ansible|
      # Two playbooks are available for building the kernel, for test and stable patches.
      # The stable playbook will prompt for HTTP auth credentials prior to running.
      # One subsequent runs of the stable playbook, you can simply hit enter to skip
      # the credential entry, since the files have already been downloaded.
      ansible.playbook = 'ansible/build-grsecurity-kernel-test.yml'
      ansible.playbook = 'ansible/build-grsecurity-kernel-stable.yml'
      ansible.verbose = 'vv'
      # Exposing the build strategy var for testing various build strategies quickly.
      ansible.extra_vars = {
        'grsecurity_build_strategy' => 'vanilla',
      }
    end
    build.vm.provider "virtualbox" do |v|
      v.memory = 2048
      v.customize ["modifyvm", :id, "--cpus", available_vcpus]
    end
  end

  # Separate machine for testing installation of .deb packages.
  # In case of problems, you don't want to pollute the build machine
  # with the test packages.
  config.vm.define 'grsec-install', autostart: false do |install|
    install.vm.box = "ubuntu/trusty64"
    install.vm.hostname = "grsec-install"
    # If grsec install works, the shared folder mount will fail.
    # Set `disabled: true` below to prevent the error post-install.
    install.vm.synced_folder './', '/vagrant', disabled: false
  end
end


def available_vcpus
  # Increase number of virtual CPUs in guest VM.
  # Rather than blindly set it to "2" or similar,
  # inspect the number of VCPUs on the host and use that,
  # to minimize compile time.
  available_vcpus = case RUBY_PLATFORM
    when /linux/
      `nproc`.to_i
    when /darwin/
      `sysctl -n hw.ncpu`.to_i
    else
      1
    end
  # If you want to restrict the resources available to the guest VM,
  # uncomment the return line below, and Vagrant will use half the
  # number available on the host, rounded down.
  # (Ruby will correctly return the quotient as an integer.)
  # return available_vcpus / 2
  return available_vcpus
end

