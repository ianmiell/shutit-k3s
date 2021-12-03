def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	shutit_session.send('helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx')
	shutit_session.send('helm repo update')
	shutit_session.send('''cat > values.yaml << EOF
controller:
  service:
    type: NodePort
    nodePorts:
      http: 32080
      https: 32443
      tcp:
        8080: 32808
EOF''')
	shutit_session.send('helm install ingress-nginx/ingress-nginx --generate-name --values values.yaml')
