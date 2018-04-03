# Building kernel packages for SecureDrop

This document is an abridged version of the full `build.md` document,
and is intended for two use cases:

  * FPF staff building kernels for use in SecureDrop
  * SecureDrop Admins recompiling a kernel from source

Users trying to recompile grsecurity-patched kernels for contexts other
than SecureDrop should look elsewhere. Make sure to review the requirements
in the README (such as 30GB free disk space) before continuing.

## Building the SecureDrop-specific packages for release
The automated build logic for preparing source directories will streamline most
of the build process described in detail in `docs/build.md`. Due to recent
access restrictions, in order to use the automated build logic, you'll need
to configure authentication credentials locally. Then make sure the relevant
build versions (step 2) are accurate.

1. Set the grsecurity auth credentials via env vars:
    * `GRSECURITY_USERNAME`
    * `GRSECURITY_PASSWORD`
2. Update the following vars in the securedrop-build playbook:
    * `grsecurity_build_revision`
    * `grsecurity_metapackage_kernel_version`
    * `grsecurity_metapackage_kernel_version_suffix`
3. Run `vagrant up grsec-build-securedrop` to run the build.

The Ansible run will fetch, configure, and compile the kernel source
into Debian packages packages. In a subsequent play, it will build the
`securedrop-grsec` metapackage (which merely declares dependencies
on the real kernel packages).

Due to broken fetching logic (#93), you'll have to copy the built packages
back to the host machine manually. Log in interactively and find the files:

```bash
vagrant ssh grsec-build-securedrop
find ~/linux -maxdepth 1 -type f -name '*.deb'
```

All files listed should be copied back to the host. Then proceed
with uploading to the apt server and performing the signing ceremony.

## Rebuilding the SecureDrop-specific packages from source

Administrators of SecureDrop may wish to compile the binary kernel image
package from the original source code. To do so, first request corresponding
source from FPF as described in the [SecureDrop source offer].
Make sure to include the exact kernel version you're requesting the source for,
to avoid confusion. Once you have obtained the source, follow
the instructions below.

[SecureDrop source offer]: https://github.com/freedomofpress/securedrop/blob/develop/SOURCE_OFFER

### 4.x kernel image
Recent versions of the SecureDrop kernels are based on the `4.x` kernel series.
FPF will provide a `linux-*.orig.tar.gz` tarball including the original source
and config.

There is convenient rebuild logic in the [grsecurity-build] repository.
Once you have received the source tarball, clone that repository,
and run `make securedrop-rebuild`.

[grsecurity-build]: https://github.com/freedomofpress/ansible-role-grsecurity-build

### 3.x kernel image
For the `3.x` kernel series, e.g. `3.14.79-grsec`, FPF will provide a
`linux-source-*.deb` package. Once you have received that package, then:

1. Place the deb package in the repo root.
2. Run `vagrant up grsec-rebuild-securedrop`.

The Ansible playbook will bootstrap the build environment, and pull down all
necessary dependencies, including the Ubuntu Trusty kernel overlay. You still
need to configure the source, then build.

#### Configuring the kernel (3.x)

Log in to build host and configure the kernel:

```
vagrant ssh grsec-rebuild-securedrop
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

#### Building the kernel image and headers (3.x)

Now that the kernel if configured, proceed with compiling:

```
fakeroot make-kpkg clean
fakeroot make-kpkg -j "$(nproc)" --initrd --overlay-dir=../ubuntu-package kernel_image kernel_headers kernel_source
```

When the compilation finishes, you'll have three .deb packages:

```
linux-headers-3.14.79-grsec_3.14.79-grsec-10.00.Custom_amd64.deb
linux-image-3.14.79-grsec_3.14.79-grsec-10.00.Custom_amd64.deb
linux-source-3.14.79-grsec_3.14.79-grsec-10.00.Custom_all.deb
```

Naturally, the version numbers may be different from those above. You should
test installing the `linux-image-*.deb` package in an Ubuntu Trusty VM,
such as the `grsec-install` VM.
