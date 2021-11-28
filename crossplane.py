def run(shutit_sessions, machines):
	machine1_ip = machines['machine1']['ip']
	machine2_ip = machines['machine2']['ip']
	machine3_ip = machines['machine3']['ip']
	machine4_ip = machines['machine4']['ip']
	machine5_ip = machines['machine5']['ip']

	# Set up crossplane
	shutit_session.send('kubectl create namespace crossplane-system')
	shutit_session.send('helm repo add crossplane-stable https://charts.crossplane.io/stable')
	shutit_session.send('helm repo update')
	shutit_session.send('helm install crossplane --namespace crossplane-system crossplane-stable/crossplane')
	shutit_session.send('curl -sL https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh | sh')
	shutit_session.send('mv kubectl-crossplane /usr/local/bin')
	shutit_session.pause_point('kubectl get all -n crossplane-system')
