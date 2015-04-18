# declare required kernel files to be downloaded
required_kernel_files = [
  {
    :filename => 'linux-3.14.21.tar.xz',
    :url => 'https://www.kernel.org/pub/linux/kernel/v3.14/linux-3.14.21.tar.xz',
    :sha256 => 'fb12f6972e115cb7ea1bfff359ca2d7cb7210a28030b8516c79ceb86009d2e26',
  },
  {
    :filename => 'linux-3.14.21.tar.sign',
    :url => 'https://www.kernel.org/pub/linux/kernel/v3.14/linux-3.14.21.tar.sign',
    :sha256 => '73e23328fac00de1fe60153e15399244b8f71996c5b9d5b087a41f01d6eb8e3d',
  },
  {
    :filename => 'grsecurity-3.1-3.14.38-201504142259.patch',
    :url => 'https://grsecurity.net/stable/grsecurity-3.1-3.14.38-201504142259.patch',
    :sha256 => '1abe9f4209d3af9b5dc6d63685502cb1af30097927c756cea3b42e25d677637e',
  },
  {
    :filename => 'grsecurity-3.1-3.14.38-201504142259.patch.sig',
    :url => 'https://grsecurity.net/stable/grsecurity-3.1-3.14.38-201504142259.patch.sig',
    :sha256 => 'fc7cb30b0f603c698a1485077f7b6868931d0fc79c32ef26379d50f261443d48',
  },
]
# ensure kernel files have been downloaded
required_kernel_files.each do |required_kernel_file|
  describe file(required_kernel_file[:filename]) do
    it { should be_file }
    its(:sha256sum) { should eq required_kernel_file[:sha256sum] }
  end
end



