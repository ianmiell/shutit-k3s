def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
⍿···shutit_session.send('apt install -y make docker.io')
⍿···shutit_session.send('curl -LO https://go.dev/dl/go1.18beta1.linux-amd64.tar.gz')
⍿···shutit_session.send('tar -C /usr/local -xzf go1.18beta1.linux-amd64.tar.gz')
⍿···shutit_session.send('export GOROOT=/usr/local/go > ~/.bashrc')
⍿···shutit_session.send('export GOPATH=$HOME/go > ~/.bashrc')
⍿···shutit_session.send('export PATH=$GOPATH/bin:$GOROOT/bin:$PATH > ~/.bashrc')
⍿···shutit_session.send('export GOROOT=/usr/local/go')
⍿···shutit_session.send('export GOPATH=$HOME/go')
⍿···shutit_session.send('export PATH=$GOPATH/bin:$GOROOT/bin:$PATH')
	# https://book.kubebuilder.io/quick-start.html#installation
	shutit_session.send('curl -L -o kubebuilder https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH)')
	shutit_session.send('chmod +x kubebuilder && mv kubebuilder /usr/local/bin/')
	# https://book.kubebuilder.io/cronjob-tutorial/cronjob-tutorial.html
	shutit_session.send('git clone https://github.com/kubernetes-sigs/kubebuilder')
	shutit_session.send('cd kubebuilder/docs/book/src/cronjob-tutorial/testdata/project')
	# https://book.kubebuilder.io/cronjob-tutorial/running.html
	shutit_session.send('make manifests')
	shutit_session.send('make install')
	shutit_session.send('make run ENABLE_WEBHOOKS=false')
	shutit_session.send('sleep 120')
	shutit_session.send('''cat > batch_v1_cronjob.yaml << EOF
apiVersion: batch.tutorial.kubebuilder.io/v1
kind: CronJob
metadata:
  name: cronjob-sample
spec:
  schedule: "*/1 * * * *"
  startingDeadlineSeconds: 60
  concurrencyPolicy: Allow # explicitly specify, but Allow is also default.
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox
            args:
            - /bin/sh
            - -c
            - date; echo Hello from the Kubernetes cluster
          restartPolicy: OnFailure
EOF''')
	shutit_session.send('kubectl create -f batch_v1_cronjob.yaml')
	shutit_session.send('docker login -u imiell -p dockeristhelord')
	shutit_session.send('make docker-build docker-push IMG=imiell/project:latest')
	shutit_session.send('make deploy IMG=imiell/project:latest')   # FAILS
