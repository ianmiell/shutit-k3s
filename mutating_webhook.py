def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# From: https://kubernetes.io/blog/2019/03/21/a-guide-to-kubernetes-admission-controllers/
	shutit_session.send('git clone https://github.com/stackrox/admission-controller-webhook-demo')
	shutit_session.send('''kubectl create -f <(cat << EOF
apiVersion: admissionregistration.k8s.io/v1beta1
kind: MutatingWebhookConfiguration
metadata:
  name: demo-webhook
webhooks:
  - name: webhook-server.webhook-demo.svc
    clientConfig:
      service:
        name: webhook-server
        namespace: webhook-demo
        path: "/mutate"
      caBundle: ${CA_PEM_B64}
    rules:
      - operations: [ "CREATE" ]
        apiGroups: [""]
        apiVersions: ["v1"]
        resources: ["pods"]
EOF
)''')
	shutit_session.send('apt -y install make golang docker.io')
	shutit_session.send('cd admission-controller-webhook-demo')
	shutit_session.get_file('/root/.dockerpass', 'dockerpass')
	shutit_session.send('docker login -u imiell -p <(cat /root/.dockerpass)')
	shutit_session.send('IMAGE=ianmiell/admission-controller-webhook-demo make')

	shutit_session.pause_point('')
