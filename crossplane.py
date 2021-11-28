def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# Set up crossplane
	shutit_session.send('kubectl create namespace crossplane-system')
	shutit_session.send('helm repo add crossplane-stable https://charts.crossplane.io/stable')
	shutit_session.send('helm repo update')
	shutit_session.send('helm install crossplane --namespace crossplane-system crossplane-stable/crossplane')
	shutit_session.send('curl -sL https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh | sh')
	shutit_session.send('mv kubectl-crossplane /usr/local/bin')
	shutit_session.pause_point('kubectl get all -n crossplane-system')
