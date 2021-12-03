def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	shutit_session.send('git clone https://github.com/stackrox/admission-controller-webhook-demo')
	shutit_session.pause_point('')
