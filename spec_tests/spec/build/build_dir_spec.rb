# ensure build directory is present
describe file('/home/vagrant/grsec') do
  it { should be_directory }
end

# check for presence of git dir for ubuntu source
ubuntu_git_dir = '/home/vagrant/ubuntu-trusty'
describe file(ubuntu_git_dir) do
  it { should be_directory }
end

# ensure git checkout completed successfully
describe command("git fsck --git-dir #{ubuntu_git_dir}/.git --work-tree #{ubuntu_git_dir}") do
  its(:exit_status) { should eq 0 }
end
