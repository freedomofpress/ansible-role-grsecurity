# ansible-role-grsecurity

Build and install Linux kernels with the grsecurity patches applied.
Supports "test" and "stable" grsecurity patches. Using the "stable"
patches will [require subscription](https://grsecurity.net/business_support.php).

These configurations were developed by [Freedom of the Press Foundation] for
use in all [SecureDrop] instances. Experienced sysadmins can leverage these
roles to compile custom kernels for SecureDrop or non-SecureDrop projects.

## Requirements

Only Debian and Ubuntu are supported, but that's mostly due to lack of testing,
rather than an inherent deficiency in the configs.
For compiling the kernel, 2GB and 2 VCPUs is plenty. Depending on the config options
you specify, the compilation should take two to three hours on that hardware.
Naturally, you can speed up the build by providing more resources.

## Quickstart
Use the Vagrant VMs to build a grsecurity-patched kernel:

```
vagrant up grsec-build
vagrant ssh
cd linux/linux-<version>
make menuconfig
export CONCURRENCY_LEVEL="$(nproc)"
export PATH="/usr/lib/ccache:$PATH" # recommended if you plan to recompile
fakeroot make-kpkg --initrd kernel_image
```

When the build is finished, copy the .deb file in `~/linux` back to
your host machine. You can then use the install role to apply it.
Make sure to update the `examples/install-grsecurity-kernel.yml` playbook
and set the `grsecurity_install_deb_package` variable to the path
where you saved the deb package.

```
vagrant up grsec-install
```

The role will automatically fail if the desired kernel version (inferred
from the package name) with grsecurity patches was not installed.

## Role structure

There are three roles contained in this repository:

* build-grsec-metapackage
* build-grsec-kernel
* install-grsec-kernel

The metapackage role is SecureDrop-specific, so you can ignore it if you're compiling
for non-SecureDrop machines. The build role will download the Linux kernel source tarball
and the latest grsecurity patch and prepare the system for a manual build, then prompt
for you to login and perform the configuration manually. After building, copy the .deb
file back to your host machine.

The install role expects a .deb package filepath on the Ansible controller, the same
file that was created by the build role, and will install that package on the target host.

To add this role to an existing Ansible project:

```
ansible-galaxy install freedomofpress.grsecurity
```

Since there are multiple roles in this repository, you will need to
specify the path to the specific role in your playbook include:

```
- name: Build the grsecurity-patched Linux kernel.
  hosts: grsecurity-builder
  roles:
    - role: freedomofpress.grsecurity/roles/build-grsecurity-kernel
```

In the future, these roles may be broken out into separate repositories. Feel free to
[open an issue](https://github.com/freedomofpress/ansible-role-grsecurity/issues)
to discuss how such a change might affect your workflow.

## Role variables

### build-grsec-kernel
```yaml
# Can be "stable" or "test". Note that stable patches
# requires authentication to download. See the grsecurity
# blog for more information: https://grsecurity.net/announce.php
grsecurity_build_patch_type: test

# The default "manual" strategy will prep a machine for compilation,
# but stop short of configuring and compiling. You can instead choose
# to compile a kernel based on a static config shipped with this role,
# for a "Look ma, no hands!" kernel compilation. See the "files" dir
# for possible config options. The var below is interpolated as
# "config-{{ grsecurity_build_strategy }}" when searching for files.
grsecurity_build_strategy: manual

# Premade config file for use during compilation. Useful if you've previously
# run `make menuconfig` and want to restore the custom settings.
grsecurity_build_custom_config: ''

# When building for installation on Ubuntu, one should include the
# overlay to ensure that Ubuntu-specific options for AppArmor work.
# Honestly this needs a lot more testing, so leaving off by default.
grsecurity_build_include_ubuntu_overlay: false

# Parent directory for storing source tarballs and signature files.
grsecurity_build_download_directory: "{{ ansible_env.HOME }}/linux"

# Extracted source directory, where you should run `make menuconfig`.
grsecurity_build_linux_source_directory: >-
  {{ grsecurity_build_download_directory }}/linux-{{ linux_kernel_version }}

grsecurity_build_gpg_keyserver: hkps.pool.sks-keyservers.net

# Assumes 64-bit (not reading machine architecture dynamically.)
grsecurity_build_deb_package: >-
  linux-image-{{ linux_kernel_version }}-grsec_10.00.{{ grsecurity_build_strategy }}_amd64.deb

# Using ccache can dramatically speed up subsequent builds of the
# same kernel source. Disable if you plan to build only once.
grsecurity_build_use_ccache: true

# Credentials for downloading the grsecurity "stable" pages. Requires subscription.
# The "test" patches do not require authentication or a subscription.
grsecurity_build_download_username: ''
grsecurity_build_download_password: ''
```

### install-grsec-kernel

```yaml
# The filepath of the .deb package on the Ansible controller. This var is required,
# but can't be known ahead of time, so you must specify it manually. The role will
# fail if this var is not updated. Use the build role to create a package first.
grsecurity_install_deb_package: ''

# For easier console recovery and debugging, the GRUB timeout value (default: 5)
# can be overridden here. Without a lengthier timeout, it can be very difficult
# to get into the GRUB menu and select a working kernel to boot. Debian uses 5
# by default, which we're replicating here for consistency and predictability.
grsecurity_install_grub_timeout: 5

# paxctld is a better alternative than paxctl for maintaining the PaX flags on binaries.
# The paxctld role isn't a dependency yet, so assume the paxctl approach is safest.
# If you're using the paxctld role, set this to false.
grsecurity_install_set_paxctl_flags: true

# Location where the .deb files will be copied on the target host, prior to install.
grsecurity_install_download_dir: /usr/local/src

# The role will skip installation if the kernel version, e.g. "4.4.2-grsec",
# of the deb package matches that of the target host, provided the checksum
# for the deb file is the same. If you want to reinstall the same kernel version,
# for example while developing a new kernel config, set this to true.
grsecurity_install_force_install: false
```

## Further reading

* [Official grsecurity website](https://grsecurity.net/)
* [Grsecurity/PaX wikibook](https://en.wikibooks.org/wiki/Grsecurity/Appendix/Grsecurity_and_PaX_Configuration_Options)
* [Linux Kernel in a Nutshell](http://www.kroah.com/lkn/)

[Freedom of the Press Foundation]: https://freedom.press
[SecureDrop]: https://securedrop.org
[grsecurity]: https://grsecurity.net/

