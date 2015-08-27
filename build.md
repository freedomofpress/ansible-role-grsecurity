# Build a grsec-patched kernel for a Debian jessie server

Install dependencies:

    apt-get install libncurses5-dev build-essential kernel-package git-core gcc-4.9 gcc-4.9-plugin-dev make

Grab Spender's key and verify it:

    wget https://grsecurity.net/spender-gpg-key.asc
    gpg --import spender-gpg-key.asc
    gpg --keyserver pool.sks-keyservers.net --recv-key 647F28654894E3BD457199BE38DBBDC86092693E
    gpg --with-fingerprint spender-gpg-key.asc
    gpg --fingerprint 647F28654894E3BD457199BE38DBBDC86092693E

Grab the kernel source and grsecurity patch, plus signatures for each:

    wget https://www.kernel.org/pub/linux/kernel/v3.x/linux-3.14.51.tar.xz
    wget https://www.kernel.org/pub/linux/kernel/v3.x/linux-3.14.51.tar.sign
    wget https://grsecurity.net/stable/grsecurity-3.1-3.14.51-201508181951.patch
    wget https://grsecurity.net/stable/grsecurity-3.1-3.14.51-201508181951.patch.sig

Verify the signatures:

    gpg --verify grsecurity-3.1-3.14.51-201508181951.patch.sig
    gpg --verify linux-3.14.51.tar.sign

Extract the kernel source and apply the patch:

    tar -xf linux-3.14.51.tar
    cd linux-3.14.21/
    patch -p1 < ../grsecurity-3.0-3.14.21-201410131959.patch

Start with the VPS's existing kernel configuration, and configure stuff:

    cp /boot/config-3.16.0-4-amd64 .config
    make menuconfig

Under security options, enable grsecurity, set configuration method to automatic, set usage type to server, set virtualization type to guest (xen), save. Now build it:

    make-kpkg --rootcmd fakeroot --initrd kernel_image

In the parent directory, you now have the kernel .package `linux-image-3.14.51-grsec_3.14.51-grsec-10.00.Custom_amd64.deb`. copy it to the target machine and install with `dpkg -i`

`apt-get install paxtest paxctl`

Set the new kernel to boot by default, and reboot:

    grep menuentry /boot/grub/grub.cfg | cut -d "'" -f2 | grep "grsec$"
    sed -i "s/^GRUB_DEFAULT=.*$/GRUB_DEFAULT=\"Debian GNU\/Linux, with Linux 3.14.51-grsec\"/" /etc/default/grub
    update-grub
    shutdown -r now

Set these sysctl variables:

    kernel.grsecurity.rwxmap_logging = 0
    kernel.grsecurity.grsec_lock = 1

Run this stuff:

    paxctl -Cpm /usr/sbin/grub-probe
    paxctl -Cpm /usr/sbin/grub-mkdevicemap
    paxctl -Cpm /usr/sbin/grub-setup
    paxctl -Cpm /usr/bin/grub-script-check
    paxctl -Cpm /usr/bin/grub-mount

Run `paxtest blackhat` and check the output.
