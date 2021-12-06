def run(shutit_sessions, machines):
	machine1_ip = machines['machine1']['ip']
	machine2_ip = machines['machine2']['ip']
	machine3_ip = machines['machine3']['ip']
	machine4_ip = machines['machine4']['ip']
	machine5_ip = machines['machine5']['ip']
	machine6_ip = machines['machine6']['ip']

	# Set up /etc/hosts and other pre-requisties
	for machine in sorted(machines.keys()):
		shutit_session = shutit_sessions[machine]
		shutit_session.send('apt update -y && apt install -y ntp jq')
		for machine_k in sorted(machines.keys()):
			shutit_session.send('echo ' + machines[machine_k]['ip'] + ' ' + machine_k + ' ' + machines[machine_k]['fqdn'] + ' >> /etc/hosts')

	# Set up first master
	shutit_session = shutit_sessions['machine1']
	# no traefik because we are using istio ingress, flannel iface and the other ip references to make it go to the right ip address
	shutit_session.send('''curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--cluster-init --flannel-iface enp0s8 --no-deploy traefik --tls-san $(hostname) --advertise-address ''' + machine1_ip + ''' --bind-address ''' + machine1_ip + ''' --node-ip ''' + machine1_ip + ''' --write-kubeconfig-mode 644" sh -''')
	k3s_token = shutit_session.send_and_get_output('cat /var/lib/rancher/k3s/server/node-token')
	shutit_session.send('mkdir -p ~/.kube')
	shutit_session.send('cp /etc/rancher/k3s/k3s.yaml ~/.kube/config')

	for machine in ('machine2','machine3'):
		shutit_session = shutit_sessions[machine]
		machine_ip = machines[machine]['ip']
		# Full list of plugins
		#enable-admission-plugins=NamespaceLifecycle,LimitRanger,ServiceAccount,DefaultStorageClass,DefaultTolerationSeconds,MutatingAdmissionWebhook,ValidatingAdmissionWebhook,Priority,ResourceQuota,PodSecurityPolicy,NodeRestriction
		# Took PodSecurityPolicy out at it inhibited other things from running, we might want to re-enable later.
		shutit_session.send('''curl -sfL http://get.k3s.io | INSTALL_K3S_EXEC="server --kube-apiserver-arg enable-admission-plugins=NamespaceLifecycle,LimitRanger,ServiceAccount,DefaultStorageClass,DefaultTolerationSeconds,MutatingAdmissionWebhook,ValidatingAdmissionWebhook,Priority,ResourceQuota,NodeRestriction --flannel-iface enp0s8 --no-deploy traefik --server https://machine1:6443 --token ''' + k3s_token + ''' --tls-san $(hostname) --bind-address ''' + machine_ip + ''' --advertise-address ''' + machine_ip + ''' --node-ip ''' + machine_ip + ''' --write-kubeconfig-mode 644" sh -''')

	for machine in ('machine4','machine5','machine6'):
		shutit_session = shutit_sessions[machine]
		machine_ip = machines[machine]['ip']
		shutit_session.send('curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent --flannel-iface enp0s8 --server https://machine1:6443 --token ' + k3s_token + ' --node-ip ' + machine_ip + '" sh -')

	# Set up k9s
	shutit_session = shutit_sessions['machine1']
	shutit_session.send('cd /tmp')
	shutit_session.send('wget https://github.com/derailed/k9s/releases/download/v0.24.15/k9s_Linux_x86_64.tar.gz')
	shutit_session.send('tar -zxvf k9s_Linux_x86_64.tar.gz')
	shutit_session.send('mv k9s /usr/bin/k9s')
	shutit_session.send('cd -')
	# Set up kustomize
	shutit_session.send('curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash')
	shutit_session.send('mv /root/kustomize /usr/bin')
	# Set up helm
	shutit_session.send('wget https://get.helm.sh/helm-v3.7.1-linux-amd64.tar.gz')
	shutit_session.send('tar -zxvf helm-v3.7.1-linux-amd64.tar.gz')
	shutit_session.send('mv ./linux-amd64/helm /usr/bin')
	shutit_session.send('rm helm-*gz')

	# Install krew
	shutit_session.send('''(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
  KREW="krew-${OS}_${ARCH}" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
  tar zxvf "${KREW}.tar.gz" &&
  ./"${KREW}" install krew
)''')
	shutit_session.send('export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"')
	shutit_session.send("""echo 'export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"' >> ~/.bashrc'""")

	import istio_in_action
	import crossplane
	import ingress
	import istio_in_action
	import kube_monkey
	import kubevirt
	import mutating_webhook
	import rook
	import shell_operator
	crossplane.run(shutit_sessions, machines)
	#istio_in_action.run(shutit_sessions, machines)
	#crossplane.run(shutit_sessions, machines)
	#ingress.run(shutit_sessions, machines)
	#kube_monkey.run(shutit_sessions, machines)
	kubevirt.run(shutit_sessions, machines)
	#mutating_webhook.run(shutit_sessions, machines)
	#rook.run(shutit_sessions, machines)
	#shell_operator.run(shutit_sessions, machines)
	shutit_session.pause_point('END OF ALL MODULES')
