def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# https://aquasecurity.github.io/starboard/v0.13.2/operator/installation/helm/
	shutit_session.send('git clone --depth 1 --branch v0.13.2 https://github.com/aquasecurity/starboard.git')
	shutit_session.send('cd starboard')
	shutit_session.send('helm repo add aqua https://aquasecurity.github.io/helm-charts/')
	shutit_session.send('helm repo update')
	shutit_session.send('helm install starboard-operator ./deploy/helm --namespace starboard-system --create-namespace --set="targetNamespaces=default" --set="trivy.ignoreUnfixed=true"')

