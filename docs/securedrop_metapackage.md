# Building kernel packages for SecureDrop

This document is an abridged version of the full `build.md` document,
and is relevant only for building kernels hosted by Freedom of the Press
Foundation for use in SecureDrop.

## Building the metapackage
The build role defaults to use "test" patches for grsecurity,
and the example playbook doesn't build the `securedrop-grsec`
metapackage. To use these playbooks to build for SecureDrop:

1. Update the `ansible.playbook` line in the `Vagrantfile` to
   point to `examples/build-grsecurity-kernel-stable.yml`.

2. Run `vagrant provision grsec-build`.

3. Type in the auth credentials for the grsecurity stable patches.

The Ansible run will first build the metapackage, which merely
declares dependencies on the real kernel packages, then bootstrap
the build host for a manual compilation. Ansible will stop
immediately before configuring and compiling the kernel package.

## Configuring the kernel

Log in to build host and configure the kernel:

```
vagrant up grsec-build
vagrant ssh
cd linux/linux-<version>
make menuconfig
```

Since SecureDrop runs on bare metal, not virtualization, configure
the grsecurity settings to remove all virtualization types:

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

Configuration complete.

## Building the kernel image and headers

Now that the kernel if configured, proceed with compiling:

```
export CONCURRENCY_LEVEL="$(nproc)"
fakeroot make-kpkg clean
fakeroot make-kpkg --initrd --overlay-dir=../ubuntu-package kernel_image kernel_headers
```

When the compilation finishes, you'll have two .deb packages:

```
linux-headers-3.14.21-grsec_3.2.61-grsec-10.00.Custom_amd64.deb
linux-image-3.14.21-grsec_3.2.61-grsec-10.00.Custom_amd64.deb
```

Naturally, the version numbers will be different. Capture the SHA256 checksums
for those packages, then copy them off the build host and you're ready to rock.
