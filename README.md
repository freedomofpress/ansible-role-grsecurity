# ansible-role-grsecurity

Build and install Linux kernels with the grsecurity patches applied.
Supports "test" and "stable" grsecurity patches. Using the "stable"
patches will [require subscription](https://grsecurity.net/business_support.php).

These configurations were developed by [Freedom of the Press Foundation] for
use in all [SecureDrop] instances. Experienced sysadmins can leverage these
configuration roles to compile custom kernels for SecureDrop or non-SecureDrop
architecture.

## Requirements

Only Debian and Ubuntu are supported, but that's mostly due to lack of testing,
rather than an inherent deficiency in the configs. If you plan to the stable patches,
you'll need to sign up for a [grsecurity subscription](https://grsecurity.net/business_support.php).
For compiling the kernel, 2GB and 2 VCPUs is plenty. Depending on the config options
you specify, the compilation should take two to three hours on that hardware.

## Role structure

There are three roles contained in this repository:

* build-grsec-metapackage
* build-grsec-kernel
* install-grsec-kernel

The metapackage role is SecureDrop-specific, so you can ignore it if you're compiling
for non-SecureDrop machines. The build role will download the Linux kernel source tarball
and the latest grsecurity patch and prepare the system for a manual build. The install role
expects a .deb package filepath on the Ansible controller, and will install that package
on the target host.



The primary components of interest in this repository are:

1. `securedrop-grsec`, the kernel metapackage
2. `build.md`, the guide for building the grsecurity kernel for SecureDrop

## Building the metapackage

Use the Vagrant build VM. `vagrant up` will create the VM and run the Ansible playbook, which will build the `.deb` package and store it in the top level of this repository. You can re-build the package quickly by re-running the playbook with `vagrant provision`.
=======
This repository contains code and documentation related to the grsecurity kernels used by the Freedom of the Press Foundation internally.

There is a role for building the kernel and one for the host to install it on.

The Ansible playbook is compatible with both Debian jessie and Ubuntu trusty — just modify the `target_os` in `./ansible/vars/main.yml`.


[Freedom of the Press Foundation]: https://freedom.press
[SecureDrop]: https://securedrop.org
[grsecurity]: https://grsecurity.net/
