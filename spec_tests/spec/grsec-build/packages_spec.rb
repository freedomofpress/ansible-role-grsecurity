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

# ensure safe-upgrade has been performed
describe command('aptitude --simulate safe-upgrade -y') do
  its(:exit_status) { should eq 0 }
  expected_output = <<-eos
No packages will be installed, upgraded, or removed.
0 packages upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
Need to get 0 B of archives. After unpacking 0 B will be used.
Would download/install/remove packages.
eos
  its(:stdout) { should contain(expected_output) }
end

# make sure a reboot is not required
describe command("/bin/bash -c '[[ ! -e /var/run/reboot-required ]]'") do
  its(:exit_status) { should eq 0 }
end
