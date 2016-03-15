Ubuntu kernel with grsecurity
=============================

------------------------------------------------------------------------

**Note:** This document is deprecated in favor of the [automated
Ansible roles](https://github.com/freedomofpress/ansible-role-grsecurity)
for building and installing grsecurity-patched kernels.
If you want to compile the kernel by hand, consider reading through
the Ansible playbooks in depth. They're YAML, and liberally commented.

FPF staff should refer to the `securedrop_metapackage.md` document
for step-by-step instructions on compiling the kernel packages
used for SecureDrop instances.

------------------------------------------------------------------------

This guide outlines the steps required to compile a kernel for
[Ubuntu Server 14.04 (Trusty Tahr)](http://releases.ubuntu.com/14.04/)
with [Grsecurity](https://grsecurity.net/), specifically for use
with [SecureDrop](https://freedom.press/securedrop).
At the end of this guide, you will have two Debian packages
that you transfer to the *App* and *Monitor* servers.

## Before you begin

The steps in this guide assume you have the following set up and running:

 * SecureDrop App and Monitor servers (see the
   [installation guide](https://github.com/freedomofpress/securedrop/blob/develop/docs/install.md))
 * An offline server running
   [Ubuntu Server 14.04 (Trusty Tahr)](http://releases.ubuntu.com/14.04/)
   that you use to compile the kernel
 * An online server that you use to download package dependencies

Since SecureDrop is only supported on 64-bit platforms,
make sure you download a 64-bit version of Ubuntu to build the kernel.
The `.iso` filename will have an `-amd64` suffix.

The idea is that you will use the online server to download package
dependencies, put the files on a USB stick and transfer them to the
offline server, then use the offline server to verify digital signatures
and compile the new kernel.

The current version of this document assumes you are compiling Linux
kernel version *3.14.21* and Grsecurity version
*3.0-3.14.21-201410131959*. When running commands that include filenames
and/or version numbers, make sure it all matches what you have on your
server.

## Update packages on online and offline servers

Run the following set of commands to ensure all packages are up to date
on the online and offine servers.


```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
sudo reboot  # to use the upgraded kernel from dist-upgrade
```

## Install dependencies on the offline server

Run the following command to install the package dependencies required
to compile the new kernel with Grsecurity.

```
sudo apt-get install libncurses5-dev build-essential kernel-package git-core \
                     gcc-4.8 gcc-4.8-plugin-dev make
```

Create a directory for Grsecurity and download the public keys that you
will later use to verify the Grsecurity and Linux kernel downloads.

```
mkdir grsec
cd grsec/
wget https://grsecurity.net/spender-gpg-key.asc
gpg --import spender-gpg-key.asc
gpg --keyserver pool.sks-keyservers.net --recv-key 647F28654894E3BD457199BE38DBBDC86092693E
```

Verify that the keys you have received are authentic by checking the fingerprint for each one:

```
gpg --with-fingerprint spender-gpg-key.asc
gpg --fingerprint 647F28654894E3BD457199BE38DBBDC86092693E
```

Bradley Spengler should have a fingerprint of "DE94 52CE 46F4 2094 907F 108B
44D1 C0F8 2525 FE49" and Greg Kroah-Hartman should have a fingerprint of "647F
2865 4894 E3BD 4571 99BE 38DB BDC8 6092 693E". If either of the fingerprints do
not match what you see here, please get in touch at securedrop@freedom.press.

At this point, you should disconnect this server from the Internet and
treat it as an offline (air-gapped) server.

## Download kernel and Grsecurity on online server

Create a directory for Grsecurity, the Linux kernel, and the other tools
you will be downloading.

```
mkdir grsec
cd grsec/
```

Make a copy of the *kernel-package* directory on the online server.

```
cp -a /usr/share/kernel-package ubuntu-package
```

When downloading the Linux kernel and Grsecurity, make sure you get the
long term stable versions and that the version numbers match up.

```
wget https://www.kernel.org/pub/linux/kernel/v3.x/linux-3.14.21.tar.xz
wget https://www.kernel.org/pub/linux/kernel/v3.x/linux-3.14.21.tar.sign
wget https://grsecurity.net/stable/grsecurity-3.0-3.14.21-201410131959.patch
wget https://grsecurity.net/stable/grsecurity-3.0-3.14.21-201410131959.patch.sig
```

Download the Ubuntu kernel overlay.

```
git clone git://kernel.ubuntu.com/ubuntu/ubuntu-trusty.git
```

This repo is very large, so cloning it will take a while.

### Verifying the Ubuntu kernel overlay

Verifying the Ubuntu kernel overlay is a little tricker than the other things
we've verified so far because the latest tag may be signed by one of several
Ubuntu developers. Unfortunately, there is nothing we can do about this. You
will need to determine how to establish trust in the key that signed the repo
for yourself.

Basically, you should check out the most recent signed tag and look up the
developer who signed it. You can do this easily by running:

```
cd ubuntu-trusty/
git tag -v `git describe`
```

`git describe` finds the most recent annotated tag (all signed tags are
annotated tags), and `git tag -v` verifies it. It will check the keyid that made
the signature, automatically download the public key from the keyservers if it
is not available in your local keyring, and use it to check the signature.

The difficult thing is establishing trust in the automatically downloaded public
key. Even if you get a "Good signature", you should still make sure the key is
that of an actual Ubuntu developer and not from an impostor. Depending on your
level of paranoia, you may wish to check the key against other online sources,
ask some Ubuntu developers that you know, meet the developer in question in
person and sign their key, etc. Most Ubuntu developers appear to use the Web of
Trust (WoT), so you should be able to meet *some* Ubuntu developer(s), sign
their key(s), and use the WoT to verify the key that signed the kernel overlay
repo tag.

Verifying this repo is especially important because it is only available via the
unauthenticated `git://` protocol, so MITM-ing the download is trivial.

If verifying the repo fails, please get in touch at
securedrop@freedom.press. Only continue if you have a "Good signature" from a
trusted key.

Once you have verified the most recent tag, check it out before
continuing. `HEAD` on master is usually the same commit that the most recent tag
points to, but better safe than sorry.

```
git checkout `git describe`
```

Transfer all the files in the *grsec* directory from the online server
to the offline server using a USB stick.

## Before you compile on the offline server

After moving the files from the online server to the offline server, you
should have the following in your *grsec* directory.

```
grsecurity-3.0-3.14.21-201410131959.patch	    spender-gpg-key.asc
grsecurity-3.0-3.14.21-201410131959.patch.sig	ubuntu-package/
linux-3.14.21.tar.sign				            ubuntu-trusty/
linux-3.14.21.tar.xz
```

### Gather the required files for the Ubuntu kernel overlay

Copy the required directories from the Ubuntu kernel overlay directory
to the correct *ubuntu-package* directory.

```
cp ubuntu-trusty/debian/control-scripts/p* ubuntu-package/pkg/image/
cp ubuntu-trusty/debian/control-scripts/headers-postinst ubuntu-package/pkg/headers/
```

### Verify the digital signatures

Verify the digital signature for Grsecurity.

```
gpg --verify grsecurity-3.0-3.14.21-201410131959.patch.sig grsecurity-3.0-3.14.21-201410131959.patch
```

Verify the digital signature for the Linux kernel.

```
unxz linux-3.14.21.tar.xz
gpg --verify linux-3.14.21.tar.sign linux-3.14.21.tar
```

Do not move on to the next step until you have successfully verified both
signatures. If either of the signatures fail to verify, go back to the online
server, re-download both the package and signature and try again.

### Apply Grsecurity patch to the Linux kernel

Extract the Linux kernel archive and apply the Grsecurity patch.

```
tar -xf linux-3.14.21.tar
cd linux-3.14.21/
patch -p1 < ../grsecurity-3.0-3.14.21-201410131959.patch
```

### Configure Grsecurity

Configure Grsecurity with the following command.

```
make menuconfig
```

You will want to follow the steps below to select and configure the
correct options.

 * Navigate to *Security options*
   * Navigate to *Grsecurity*
     * Press *Y* to include it
     * Set *Configuration Method* to *Automatic*
     * Set *Usage Type* to *Server* (default)
     * Set *Virtualization Type* to *None* (default)
     * Set *Required Priorities* to *Security*
     * Select *Exit*
   * Select *Exit*
 * Select *Exit*
 * Select *Yes* to save

### Compile the kernel with Grsecurity

We recommend setting `CONCURRENCY_LEVEL` to use all available cores when
compiling the kernel. Note that this step may fail if you are using a small
VPS/virtual machine. In our experience you will need at least 20GB of free
storage to build the kernel.

```sh
export CONCURRENCY_LEVEL="$(grep -c '^processor' /proc/cpuinfo)"
make-kpkg --rootcmd fakeroot clean
make-kpkg --rootcmd fakeroot --initrd --overlay-dir=../ubuntu-package kernel_image kernel_headers
```

When the build process is done, you will have the following Debian
packages in the *grsec* directory:

```
linux-headers-3.14.21-grsec_3.2.61-grsec-10.00.Custom_amd64.deb
linux-image-3.14.21-grsec_3.2.61-grsec-10.00.Custom_amd64.deb
```

Put the packages on a USB stick and transfer them to the SecureDrop App
and Monitor servers.

## Speeding up Repeated Builds

If you are testing different kernel configurations, or otherwise plan to
build a Linux kernel multiple times on the same hardware, you can speed up
subsequent builds by using `ccache`. Read this [blog post][] to see how to
install and configure it specifically for kernel builds.

[blog post]: http://linuxdeveloper.blogspot.com/2012/05/using-ccache-to-speed-up-kernel.html

## Set up PaX on App and Monitor servers

Proceed with the following steps only if the SecureDrop App and Monitor
servers are up and running.

Both servers need to have PaX installed and configured. PaX is part of
common security-enhancing kernel patches and secure distributions, such
as Grsecurity.

```
sudo apt-get install paxctl
sudo paxctl -Cpm /usr/sbin/grub-probe
sudo paxctl -Cpm /usr/sbin/grub-mkdevicemap
sudo paxctl -Cpm /usr/sbin/grub-setup
sudo paxctl -Cpm /usr/bin/grub-script-check
sudo paxctl -Cpm /usr/bin/grub-mount
```

### Install new kernel on both App and Monitor servers

Install the new kernel with Grsecurity on both servers.

```
sudo dpkg -i *.deb
sudo update-grub
```

### Configure App and Monitor servers to use new kernel by default

Set the new kernel to be the default on both servers. Start by finding
the exact menuentry name for the new kernel.

```
grep menuentry /boot/grub/grub.cfg | cut -d "'" -f2 | grep "grsec$"
```

Copy the output and use it in the *sed* command below to set this kernel
as the default.

```
sudo sed -i "s/^GRUB_DEFAULT=.*$/GRUB_DEFAULT=\"2>Ubuntu, with Linux 3.14.21-grsec\"/" /etc/default/grub
sudo update-grub
sudo reboot
```

After reboot, verify the you booted the new kernel by running `uname -a`.
Confirm that the `-grsec` kernel is the one shown. If it is not,
double-check the value you set for `GRUB_DEFAULT` in the previous sed command.

### Test SecureDrop functionality

Before you move on to the final step, ensure that SecureDrop is working
as expected by testing SSH, browsing to the .onion sites, completing the
submission and reply process, and so on.

### Lock it down

Once you have confirmed that everything works, configure the Grsecurity
lock in *sysctl.conf*.

```
sudo su -
echo "kernel.grsecurity.grsec_lock = 1" >> /etc/sysctl.conf
exit
sudo sysctl -p /etc/sysctl.conf
```
