# declare required kernel files to be downloaded
required_kernel_files = [
  {
    :filename => 'linux-3.14.21.tar.xz',
    :url => 'https://www.kernel.org/pub/linux/kernel/v3.14/linux-3.14.21.tar.xz',
    :sha256 => '',
  },
  {
    :filename => 'linux-3.14.21.tar.sign',
    :url => 'https://www.kernel.org/pub/linux/kernel/v3.14/linux-3.14.21.tar.sign',
    :sha256 => '',
  },
  {
    :filename => 'grsecurity-3.0-3.14.21-201410131959.patch',
    :url => 'https://grsecurity.net/stable/grsecurity-3.0-3.14.21-201410131959.patch',
    :sha256 => '',
  },
  {
    :filename => 'grsecurity-3.0-3.14.21-201410131959.patch.sig',
    :url => 'https://grsecurity.net/stable/grsecurity-3.0-3.14.21-201410131959.patch.sig',
    :sha256 => '',
  },
]
# ensure kernel files have been downloaded



