# ensure build directory is present
ubuntu_git_dir = '/home/vagrant/ubuntu-trusty'
required_build_directories = [
  ubuntu_git_dir,
  '/tmp/build',
  '/home/vagrant/ubuntu-package',
]
required_build_directories.each do |required_build_directory|
  describe file(required_build_directory) do
    it { should be_directory }
  end
end

# check for presence of git dir for ubuntu source
describe file(ubuntu_git_dir) do
  it { should be_directory }
end

# declare base command to re-use over several checks
git_base_command = "git --git-dir #{ubuntu_dir_dir}/.git --work-tree #{ubuntu_git_dir}"

# ensure git checkout completed successfully
describe command("#{git_base_command} fsck") do
  its(:exit_status) { should eq 0 }
end

# ensure git tag is valid
describe command("#{git_base_command} tag --verify $(#{git_base_command} describe)") do
  its(:exit_status) { should eq 0 }
end
