def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# https://linkerd.io/2.11/getting-started/
	shutit_session.send('''curl --proto '=https' --tlsv1.2 -sSfL https://run.linkerd.io/install | sh''')
	shutit_session.send('linkerd version')
	shutit_session.send('linkerd check --pre')
	shutit_session.send('linkerd install | kubectl apply -f -')
	shutit_session.send('linkerd check')
	# Install emotijovo demo app
	shutit_session.send('curl --proto '=https' --tlsv1.2 -sSfL https://run.linkerd.io/emojivoto.yml | kubectl apply -f -')
	shutit_session.send('kubectl -n emojivoto port-forward svc/web-svc 8080:80')
	shutit_session.send('curl localhost:8080')
	# Mesh the app
	shutit_session.send('kubectl get -n emojivoto deploy -o yaml | linkerd inject - | kubectl apply -f -')
	# Check data plane
	shutit_session.send('linkerd -n emojivoto check --proxy')
	# Install viz, on-cluster metric stack and dashboard
	shutit_session.send('linkerd viz install | kubectl apply -f - # install the on-cluster metrics stack')
	shutit_session.send('linkerd check')
	shutit_session.pause_point('linkerd viz dashboard &')


