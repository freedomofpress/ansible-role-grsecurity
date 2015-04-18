


# declare required packages for building kernel
required_packages = %w(
  build-essential
  gcc-4.8
  gcc-4.8-plugin-dev
  git-core
  kernel-package
  libncurses5-dev
  make
)
# ensure required packages are installed
required_packages.each do |required_package|
  describe package(required_package) do
    it { should be_installed }
  end
end
