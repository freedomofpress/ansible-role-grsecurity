# grsec

This repository contains all of the code and documentation related to the grsecurity kernels maintained by the Freedom of the Press Foundation for all SecureDrop instances.

The primary components of interest in this repository are:

1. `securedrop-grsec`, the kernel metapackage
2. `build.md`, the guide for building the grsecurity kernel for SecureDrop

## Building the metapackage

Use the Vagrant build VM. `vagrant up` will create the VM and run the Ansible playbook, which will build the `.deb` package and store it in the top level of this repository. You can re-build the package quickly by re-running the playbook with `vagrant provision`.
