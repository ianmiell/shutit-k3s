def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	shutit_session.send('git clone https://github.com/open-policy-agent/gatekeeper')
	shutit_session.send('apt -qq install -y pv')
	#shutit_session.send('kubectl create ns cattle-gatekeeper-system')
	#shutit_session.send('helm install rancher-charts/rancher-gatekeeper-crd --generate-name -n default')
	#shutit_session.send('helm install rancher-charts/rancher-gatekeeper --generate-name -n default')
	shutit_session.send('helm install rancher-charts/rancher-gatekeeper-crd --generate-name')
	shutit_session.send('helm install rancher-charts/rancher-gatekeeper --generate-name')
