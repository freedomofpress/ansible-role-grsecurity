## Building the metapackage

Use the Vagrant build VM. `vagrant up` will create the VM 
and run the Ansible playbook, which will build the `.deb`
package and store it in the top level of this repository. 
You can re-build the package quickly by re-running the 
playbook with `vagrant provision`.
