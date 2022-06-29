def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# From: https://kubernetes.io/blog/2019/03/21/a-guide-to-kubernetes-admission-controllers/
	shutit_session.send('git clone https://github.com/stackrox/admission-controller-webhook-demo')
	shutit_session.send('apt -qq -y install make golang docker.io')
	shutit_session.send('cd admission-controller-webhook-demo')
	#shutit_session.send_file('/root/.dockerpass', 'dockerpass')
	#shutit_session.send('docker login -u imiell -p $(cat /root/.dockerpass)')
	#shutit_session.send('IMAGE_NAME=imiell/admission-controller-webhook-demo')
	#shutit_session.send(r'''sed -i 's/\(.*image: \).*/\1 imiell\/admission-controller-webhook-demo/' deployment/deployment.yaml.template''')
	#shutit_session.send('IMAGE=$IMAGE_NAME make push-image')
	shutit_session.send('./deploy.sh && sleep 120')
	shutit_session.send('kubectl create -f examples/pod-with-defaults.yaml')
	shutit_session.pause_point('check for security context')
