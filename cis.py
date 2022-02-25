def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# https://github.com/aquasecurity/kube-bench
	shutit_session.send('git clone --single-branch https://github.com/aquasecurity/kube-bench')
	shutit_session.send('cd kube-bench')
	shutit_session.send('kubectl apply -f job.yaml')
	shutit_session.send('sleep 5')
	shutit_session.send('kubectl wait --for condition=Ready $(kubectl get pod -o custom-columns=CONTAINER:.metadata.name | grep kube-bench)')
	shutit_session.send('kubectl logs $(kubectl get pod -o custom-columns=CONTAINER:.metadata.name | grep kube-bench)')
