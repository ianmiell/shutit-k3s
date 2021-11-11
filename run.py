def run(shutit_sessions, machines):
	machine1_ip = machines['machine1']['ip']
	machine2_ip = machines['machine2']['ip']
	machine3_ip = machines['machine3']['ip']
	machine4_ip = machines['machine4']['ip']
	machine5_ip = machines['machine5']['ip']

	# Set up /etc/hosts
	for machine in sorted(machines.keys()):
		for machine_k in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			shutit_session.send('echo ' + machines[machine_k]['ip'] + ' ' + machine_k + ' ' + machines[machine_k]['fqdn'] + ' >> /etc/hosts')

	# Set up first master
	shutit_session = shutit_sessions['machine1']
	# no traefik because we are using istio ingress, flannel iface and the other ip references to make it go to the right ip address
	shutit_session.send('''curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--cluster-init --flannel-iface enp0s8 --no-deploy traefik --tls-san $(hostname) --advertise-address ''' + machine1_ip + ''' --bind-address ''' + machine1_ip + ''' --node-ip ''' + machine1_ip + '''" sh -''')
	k3s_token = shutit_session.send_and_get_output('cat /var/lib/rancher/k3s/server/node-token')
	shutit_session.send('mkdir -p ~/.kube')
	shutit_session.send('cp /etc/rancher/k3s/k3s.yaml ~/.kube/config')

	for machine in ('machine2','machine3'):
		shutit_session = shutit_sessions[machine]
		machine_ip = machines[machine]['ip']
		shutit_session.send('''curl -sfL http://get.k3s.io | INSTALL_K3S_EXEC="server --flannel-iface enp0s8 --no-deploy traefik --server https://machine1:6443 --token ''' + k3s_token + ''' --tls-san $(hostname) --bind-address ''' + machine_ip + ''' --advertise-address ''' + machine_ip + ''' --node-ip ''' + machine_ip + '''" sh -''')

	for machine in ('machine4','machine5'):
		shutit_session = shutit_sessions[machine]
		machine_ip = machines[machine]['ip']
		shutit_session.send('curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent --flannel-iface enp0s8 --server https://machine1:6443 --token ' + k3s_token + ' --node-ip ' + machine_ip + '" sh -')

	################################################################################
	# Go to main host
	shutit_session = shutit_sessions['machine1']
	################################################################################
	# Set up kubeconfig
	shutit_session.add_to_bashrc('export KUBECONFIG=~/.kube/config')
	shutit_session.send('export KUBECONFIG=~/.kube/config')
	################################################################################
	# Set up k9s
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

	# install rancher istio
	shutit_session.send('helm repo add rancher-charts https://raw.githubusercontent.com/rancher/charts/release-v2.5/')
	shutit_session.send('helm repo update')
	shutit_session.send('helm pull rancher-charts/rancher-istio')
	shutit_session.send('helm pull rancher-charts/rancher-kiali-server-crd')
	shutit_session.send('helm pull rancher-charts/rancher-kiali-server-crd')
	shutit_session.send('helm pull rancher-charts/rancher-monitoring')
	shutit_session.send('helm pull rancher-charts/rancher-monitoring-crd')
	shutit_session.send('kubectl create ns cattle-monitoring-system')
	shutit_session.send('helm install rancher-monitoring-crd-16.6.0.tgz  --generate-name --namespace cattle-monitoring-system')
	shutit_session.send('helm install rancher-monitoring-16.6.0.tgz  --generate-name --namespace cattle-monitoring-system')
	shutit_session.send('helm install rancher-kiali-server-crd-1.32.100.tgz  --generate-name')
	shutit_session.send('kubectl create ns istio-system')
	shutit_session.send('helm install rancher-istio-1.9.800.tgz  --generate-name --namespace istio-system')
	shutit_session.pause_point('END')
