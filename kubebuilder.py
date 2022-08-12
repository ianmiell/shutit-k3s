def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# https://book.kubebuilder.io/quick-start.html#installation
	shutit_session.send('curl -L -o kubebuilder https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH)')
	shutit_session.send('chmod +x kubebuilder && mv kubebuilder /usr/local/bin/')
	# https://book.kubebuilder.io/cronjob-tutorial/cronjob-tutorial.html
	shutit_session.send('mkdir project && cd project')
	shutit_session.send('kubebuilder init --domain tutorial.kubebuilder.io --repo tutorial.kubebuilder.io/project')
#oc new-project keepalived-operator
#helm repo add keepalived-operator https://redhat-cop.github.io/keepalived-operator
#helm repo update
#helm install keepalived-operator keepalived-operator/keepalived-operator
