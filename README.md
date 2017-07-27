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
# Can be "stable" or "stable2". Defaults to "stable2" because "stable"
# applies to the 3.14.79 kernel source, which has been EOL'd.
grsecurity_build_patch_type: stable2

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

# Specify targets for make-kpkg, e.g. kernel_image, kernel_headers, or binary.
# See `man make-kpkg` for details.
grsecurity_build_kpkg_targets:
  - kernel_image

# The command to run to perform the compilation. Does not include environment
# variables, such as PATH munging for ccache and setting workers to number of VCPUs.
grsecurity_build_compile_command:
  fakeroot make-kpkg
  --revision 10.00.{{ grsecurity_build_strategy }}
  {% if grsecurity_build_include_ubuntu_overlay == true %} --overlay-dir=../ubuntu-package {% endif %}
  --initrd {{ grsecurity_build_kpkg_targets|join(' ') }}

# Whether built .deb files should be fetched back to the Ansible controller.
# Useful when compiling remotely, but not so much on a local workstation.
grsecurity_build_fetch_packages: true

# Credentials for downloading the grsecurity "stable" pages. Requires subscription.
# The "test" patches do not require authentication or a subscription.
grsecurity_build_download_username: ''
grsecurity_build_download_password: ''

# List of GPG keys required for building grsecurity-patched kernel.
grsecurity_build_gpg_keys:
  - name: Greg Kroah-Hartman GPG key (Linux stable release signing key)
    fingerprint: 647F28654894E3BD457199BE38DBBDC86092693E
  - name: kernel.org checksum autosigner GPG key
    fingerprint: B8868C80BA62A1FFFAF5FDA9632D3A06589DA6B1
  - name: Bradley Spengler GPG key (grsecurity maintainer key)
    fingerprint: DE9452CE46F42094907F108B44D1C0F82525FE49

# List of GPG keys required for building grsecurity-patched kernel with the ubuntu-overlay.
# Only imported if the ubuntu-overlay is included via the `grsecurity_build_include_ubuntu_overlay` var.
grsecurity_build_gpg_keys_ubuntu:
  - name: Brad Figg GPG key (Canonical/Ubuntu Kernel Team)
    fingerprint: 11D6ADA3D9E83D93ACBD837F0C7B589B105BE7F7
  - name: Luis Henriques GPG key (Canonical/LKM)
    fingerprint: D4E1E31744709144B0F8101ADB74AEB8FDCE24FC
  - name: Stefan Bader GPG key (Canonical/Ubuntu Kernel Team)
    fingerprint: DB5D7CCAF3994E3395DA4D3EE8675DEECBEECEA3
  - name: Thadeu Lima de Souza Cascardo (Canonical)
    fingerprint: 279357DB6127376E6D1DF1BCAAD56799FBFD0D3E
```

### install-grsec-kernel

```yaml
# The filepath of the .deb package on the Ansible controller. This var is required,
# but can't be known ahead of time, so you must specify it manually. The role will
# fail if this var is not updated. Use the build role to create a package first.
grsecurity_install_deb_package: ''

# Secondary list var to support multiple deb packages, e.g. image, headers, src.
# This list will be concatenated with the scalar var above when generating the
# the list of deb packages to be installed.
grsecurity_install_deb_packages: []

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

# If the target host is remote, assume that rebooting is desired, but don't
# reboot if we're installing on localhost.
grsecurity_install_reboot: "{{ false if ansible_connection == 'local' else true }}"
```
## Access to stable patches
The "stable" and "stable2" patch types are restricted to grsecurity subscribers, and require
authentication when downloading the patches. Subscribers can also request
automated on-demand builds for more distributions than supported by the build role.
See the [grsecurity commercial support] page for more information.

## Further reading

* [Official grsecurity website](https://grsecurity.net/)
* [Grsecurity/PaX wikibook](https://en.wikibooks.org/wiki/Grsecurity/Appendix/Grsecurity_and_PaX_Configuration_Options)
* [Linux Kernel in a Nutshell](http://www.kroah.com/lkn/)

[Freedom of the Press Foundation]: https://freedom.press
[SecureDrop]: https://securedrop.org
[grsecurity]: https://grsecurity.net/
[grsecurity commercial support]: https://grsecurity.net/business_support.php
