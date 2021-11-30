# Generated by shutit skeleton
import random
import datetime
import logging
import string
import os
import inspect
import time
from shutit_module import ShutItModule

class shutit_k3s_istio(ShutItModule):


	def build(self, shutit):
		vagrant_image = shutit.cfg[self.module_id]['vagrant_image']
		vagrant_provider = shutit.cfg[self.module_id]['vagrant_provider']
		gui = shutit.cfg[self.module_id]['gui']
		memory = shutit.cfg[self.module_id]['memory']
		shutit.build['vagrant_run_dir'] = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0))) + '/vagrant_run'
		shutit.build['module_name'] = 'shutit_k3s_istio_' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
		shutit.build['this_vagrant_run_dir'] = shutit.build['vagrant_run_dir'] + '/' + shutit.build['module_name']
		shutit.send(' command rm -rf ' + shutit.build['this_vagrant_run_dir'] + ' && command mkdir -p ' + shutit.build['this_vagrant_run_dir'] + ' && command cd ' + shutit.build['this_vagrant_run_dir'])
		shutit.send('command rm -rf ' + shutit.build['this_vagrant_run_dir'] + ' && command mkdir -p ' + shutit.build['this_vagrant_run_dir'] + ' && command cd ' + shutit.build['this_vagrant_run_dir'])
		if shutit.send_and_get_output('vagrant plugin list | grep landrush') == '':
			shutit.send('vagrant plugin install landrush')
		shutit.send('vagrant init ' + vagrant_image)
		shutit.send_file(shutit.build['this_vagrant_run_dir'] + '/Vagrantfile','''Vagrant.configure("2") do |config|
  config.landrush.enabled = true
  config.vm.provider "virtualbox" do |vb|
    vb.gui = ''' + gui + '''
    vb.memory = "''' + memory + '''"
  end

  config.vm.define "machine1" do |machine1|
    machine1.vm.box = ''' + '"' + vagrant_image + '"' + '''
    machine1.vm.hostname = "machine1.vagrant.test"
    machine1.vm.disk :disk, name: "rook", size: "1024"
    machine1.vm.provider :virtualbox do |vb|
      vb.name = "shutit_k3s_istio_1"
      vb.memory = 4096
      # https://github.com/hashicorp/vagrant/issues/9794
      file_to_disk = "disk2_1.vdi"
      unless File.exist?(file_to_disk)
        vb.customize ['createhd', '--size', 10 * 1024, '--filename', file_to_disk]
      end
      vb.customize ['storageattach', :id, '--storagectl', 'SCSI', '--port', 2, '--device', 0, '--type', 'hdd', '--medium', file_to_disk]
    end
  end
  config.vm.define "machine2" do |machine2|
    machine2.vm.box = ''' + '"' + vagrant_image + '"' + '''
    machine2.vm.hostname = "machine2.vagrant.test"
    machine2.vm.disk :disk, name: "rook", size: "1024"
    machine2.vm.provider :virtualbox do |vb|
      vb.name = "shutit_k3s_istio_2"
      vb.memory = 4096
      # https://github.com/hashicorp/vagrant/issues/9794
      file_to_disk = "disk2_2.vdi"
      unless File.exist?(file_to_disk)
        vb.customize ['createhd', '--size', 10 * 1024, '--filename', file_to_disk]
      end
      vb.customize ['storageattach', :id, '--storagectl', 'SCSI', '--port', 2, '--device', 0, '--type', 'hdd', '--medium', file_to_disk]
    end
  end
  config.vm.define "machine3" do |machine3|
    machine3.vm.box = ''' + '"' + vagrant_image + '"' + '''
    machine3.vm.hostname = "machine3.vagrant.test"
    machine3.vm.disk :disk, name: "rook", size: "1024"
    machine3.vm.provider :virtualbox do |vb|
      vb.name = "shutit_k3s_istio_3"
      vb.memory = 4096
      # https://github.com/hashicorp/vagrant/issues/9794
      file_to_disk = "disk2_3.vdi"
      unless File.exist?(file_to_disk)
        vb.customize ['createhd', '--size', 10 * 1024, '--filename', file_to_disk]
      end
      vb.customize ['storageattach', :id, '--storagectl', 'SCSI', '--port', 2, '--device', 0, '--type', 'hdd', '--medium', file_to_disk]
    end
  end
  config.vm.define "machine4" do |machine4|
    machine4.vm.box = ''' + '"' + vagrant_image + '"' + '''
    machine4.vm.hostname = "machine4.vagrant.test"
    machine4.vm.disk :disk, name: "rook", size: "1024"
    machine4.vm.provider :virtualbox do |vb|
      # https://github.com/hashicorp/vagrant/issues/9794
      file_to_disk = "disk2_4.vdi"
      unless File.exist?(file_to_disk)
        vb.customize ['createhd', '--size', 10 * 1024, '--filename', file_to_disk]
      end
      vb.customize ['storageattach', :id, '--storagectl', 'SCSI', '--port', 2, '--device', 0, '--type', 'hdd', '--medium', file_to_disk]
      vb.name = "shutit_k3s_istio_4"
      vb.memory = 16384
    end
  end
  config.vm.define "machine5" do |machine5|
    machine5.vm.box = ''' + '"' + vagrant_image + '"' + '''
    machine5.vm.hostname = "machine5.vagrant.test"
    machine5.vm.disk :disk, name: "rook", size: "1024"
    machine5.vm.provider :virtualbox do |vb|
      vb.name = "shutit_k3s_istio_5"
      vb.memory = 4096
      # https://github.com/hashicorp/vagrant/issues/9794
      file_to_disk = "disk2_5.vdi"
      unless File.exist?(file_to_disk)
        vb.customize ['createhd', '--size', 10 * 1024, '--filename', file_to_disk]
      end
      vb.customize ['storageattach', :id, '--storagectl', 'SCSI', '--port', 2, '--device', 0, '--type', 'hdd', '--medium', file_to_disk]
    end
  end
  config.vm.define "machine6" do |machine6|
    machine6.vm.box = ''' + '"' + vagrant_image + '"' + '''
    machine6.vm.hostname = "machine6.vagrant.test"
    machine6.vm.disk :disk, name: "rook", size: "1024"
    machine6.vm.provider :virtualbox do |vb|
      vb.name = "shutit_k3s_istio_6"
      vb.memory = 8192
      # https://github.com/hashicorp/vagrant/issues/9794
      file_to_disk = "disk2_6.vdi"
      unless File.exist?(file_to_disk)
        vb.customize ['createhd', '--size', 10 * 1024, '--filename', file_to_disk]
      end
      vb.customize ['storageattach', :id, '--storagectl', 'SCSI', '--port', 2, '--device', 0, '--type', 'hdd', '--medium', file_to_disk]
    end
  end
end''')

		# machines is a dict of dicts containing information about each machine for you to use.
		machines = {}
		machines.update({'machine1':{'fqdn':'machine1.vagrant.test'}})
		machines.update({'machine2':{'fqdn':'machine2.vagrant.test'}})
		machines.update({'machine3':{'fqdn':'machine3.vagrant.test'}})
		machines.update({'machine4':{'fqdn':'machine4.vagrant.test'}})
		machines.update({'machine5':{'fqdn':'machine5.vagrant.test'}})
		machines.update({'machine6':{'fqdn':'machine6.vagrant.test'}})

		try:
			pw = open('secret').read().strip()
		except IOError:
			pw = ''
		if pw == '':
			shutit.log("""You can get round this manual step by creating a 'secret' with your password: 'touch secret && chmod 700 secret'""",level=logging.CRITICAL)
			pw = shutit.get_env_pass()
			time.sleep(10)

		# Set up the sessions
		shutit_sessions = {}
		for machine in sorted(machines.keys()):
			shutit_sessions.update({machine:shutit.create_session('bash', loglevel='DEBUG')})
		# Set up and validate landrush
		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			shutit_session.send('cd ' + shutit.build['this_vagrant_run_dir'])
			# Remove any existing landrush entry.
			shutit_session.send('vagrant landrush rm ' + machines[machine]['fqdn'])
			# Needs to be done serially for stability reasons.
			try:
				shutit_session.multisend('vagrant up --provider ' + shutit.cfg['shutit-library.virtualization.virtualization.virtualization']['virt_method'] + ' ' + machine,{'assword for':pw,'assword:':pw})
			except NameError:
				shutit.multisend('vagrant up ' + machine,{'assword for':pw,'assword:':pw},timeout=99999)
			if shutit.send_and_get_output("vagrant status 2> /dev/null | grep -w ^" + machine + " | awk '{print $2}'") != 'running':
				shutit.pause_point("machine: " + machine + " appears not to have come up cleanly")
			ip = shutit.send_and_get_output('''vagrant landrush ls 2> /dev/null | grep -w ^''' + machines[machine]['fqdn'] + ''' | awk '{print $2}' ''')
			machines.get(machine).update({'ip':ip})
			shutit_session.login(command='vagrant ssh ' + machine)
			shutit_session.login(command='sudo su - ')
			shutit_session.send('sysctl -w net.ipv4.conf.all.route_localnet=1')
			# Correct /etc/hosts
			shutit_session.send(r'''cat <(echo $(ip -4 -o addr show scope global | grep -v 10.0.2.15 | head -1 | awk '{print $4}' | sed 's/\(.*\)\/.*/\1/') $(hostname)) <(cat /etc/hosts | grep -v $(hostname -s)) > /tmp/hosts && mv -f /tmp/hosts /etc/hosts''')
			# Correct any broken ip addresses.
			if shutit.send_and_get_output('''vagrant landrush ls | grep ''' + machine + ''' | grep 10.0.2.15 | wc -l''') != '0':
				shutit_session.log('A 10.0.2.15 landrush ip was detected for machine: ' + machine + ', correcting.',level=logging.WARNING)
				# This beaut gets all the eth0 addresses from the machine and picks the first one that it not 10.0.2.15.
				while True:
					ipaddr = shutit_session.send_and_get_output(r'''ip -4 -o addr show scope global | grep -v 10.0.2.15 | head -1 | awk '{print $4}' | sed 's/\(.*\)\/.*/\1/' ''')
					if ipaddr[0] not in ('1','2','3','4','5','6','7','8','9'):
						time.sleep(10)
					else:
						break
				# Send this on the host (shutit, not shutit_session)
				shutit.send('vagrant landrush set ' + machines[machine]['fqdn'] + ' ' + ipaddr)
			# Check that the landrush entry is there.
			shutit.send('vagrant landrush ls | grep -w ' + machines[machine]['fqdn'])
		# Gather landrush info
		for machine in sorted(machines.keys()):
			ip = shutit.send_and_get_output('''vagrant landrush ls 2> /dev/null | grep -w ^''' + machines[machine]['fqdn'] + ''' | awk '{print $2}' ''')
			machines.get(machine).update({'ip':ip})

		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			shutit_session.run_script(r'''#!/bin/sh
# See https://raw.githubusercontent.com/ianmiell/vagrant-swapfile/master/vagrant-swapfile.sh
fallocate -l ''' + shutit.cfg[self.module_id]['swapsize'] + r''' /swapfile
ls -lh /swapfile
chown root:root /swapfile
chmod 0600 /swapfile
ls -lh /swapfile
mkswap /swapfile
swapon /swapfile
swapon -s
grep -i --color swap /proc/meminfo
echo "
/swapfile none            swap    sw              0       0" >> /etc/fstab''')
			shutit_session.multisend('adduser person',{'password:':'person','Enter new UNIX password':'person','Retype new UNIX password:':'person','Full Name':'','Phone':'','Room':'','Other':'','Is the information correct':'Y'})

		import run
		run.run(shutit_sessions, machines)
		return True


	def get_config(self, shutit):
		shutit.get_config(self.module_id,'vagrant_image',default='ubuntu/focal64')
		shutit.get_config(self.module_id,'vagrant_provider',default='virtualbox')
		shutit.get_config(self.module_id,'gui',default='false')
		shutit.get_config(self.module_id,'memory',default='3072')
		shutit.get_config(self.module_id,'swapsize',default='2G')
		return True

	def test(self, shutit):
		return True

	def finalize(self, shutit):
		return True

	def is_installed(self, shutit):
		return False

	def start(self, shutit):
		return True

	def stop(self, shutit):
		return True

def module():
	return shutit_k3s_istio(
		'shutit-k3s.shutit_k3s_istio.shutit_k3s_istio', 1498611222.0001,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','shutit-library.virtualization.virtualization.virtualization','tk.shutit.vagrant.vagrant.vagrant']
	)
