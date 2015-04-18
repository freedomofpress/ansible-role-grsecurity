# ensure gpg keys are present
describe command('gpg --list-keys') do
  its(:exit_status) { should eq 0 }
  expected_output_spender = <<-eos
pub   4096R/2525FE49 2013-11-10
uid                  Bradley Spengler (spender) <spender@grsecurity.net>
sub   4096R/3F57788A 2013-11-10
eos
  expected_output_kroah_hartman = <<-eos
pub   4096R/6092693E 2011-09-23
uid                  Greg Kroah-Hartman (Linux kernel stable release signing key) <greg@kroah.com>
sub   4096R/76D54749 2011-09-23
eos
  its(:stdout) { should contain(expected_output_spender) }
  its(:stdout) { should contain(expected_output_kroah_hartman) }
end
