# grsec

This repository contains code and documentation related to the grsecurity kernels used by the Freedom of the Press Foundation internally.

There is a role for building the kernel and one for the host to install it on.

The Ansible playbook is compatible with both Debian jessie and Ubuntu trusty — just modify the `target_os` in `./ansible/vars/main.yml`.
