def run(shutit_sessions, machines):
	# https://sdk.operatorframework.io/docs/building-operators/ansible/tutorial/
	shutit_session = shutit_sessions['machine1']
	shutit_session.send('curl -LO https://go.dev/dl/go1.18beta1.linux-amd64.tar.gz')
	shutit_session.send('tar -C /usr/local -xzf go1.18beta1.linux-amd64.tar.gz')
	shutit_session.send('export GOROOT=/usr/local/go > ~/.bashrc')
	shutit_session.send('export GOPATH=$HOME/go > ~/.bashrc')
	shutit_session.send('export PATH=$GOPATH/bin:$GOROOT/bin:$PATH > ~/.bashrc')
	shutit_session.send('export GOROOT=/usr/local/go')
	shutit_session.send('export GOPATH=$HOME/go')
	shutit_session.send('export PATH=$GOPATH/bin:$GOROOT/bin:$PATH')
	shutit_session.send('apt install -y docker.io ansible python3-pip')
	shutit_session.send('pip install ansible-runner')
	shutit_session.send('pip install openshift')
	shutit_session.send('git clone https://github.com/operator-framework/operator-sdk')
	shutit_session.send('cd operator-sdk')
	shutit_session.send('git checkout master')
	shutit_session.send('make install')
	# https://sdk.operatorframework.io/docs/building-operators/ansible/quickstart/
	shutit_session.send('mkdir memcached-operator')
	shutit_session.send('cd memcached-operator')
	shutit_session.send('operator-sdk init --domain example.com --plugins ansible')
	shutit_session.send('docker login -u imiell -p dockeristhelord')
	# Create a simple memcached API
	shutit_session.send('operator-sdk create api --group cache --version v1alpha1 --kind Memcached --generate-role')
	# Build and push operator image
	shutit_session.send('make docker-build docker-push IMG="imiell/memcached-operator:v0.0.1"')
	# OLM deployment (operator lifecycle manager)
	shutit_session.send('operator-sdk olm install') # Didn't work...
	shutit_session.pause_point('')
