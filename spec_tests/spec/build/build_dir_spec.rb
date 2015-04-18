# ensure build directory is present
describe file('/tmp/build') do
  it { should be_directory }
end
