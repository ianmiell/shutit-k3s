def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# TODO: implement: https://documentation.suse.com/sbp/all/html/SBP-rook-ceph-kubernetes/index.html#sec-limit-ceph-specifc-nodes
	# Set up rook https://rook.io/docs/rook/v1.7/quickstart.html

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
cat > values.yaml << EOF
controller:
  service:
    type: NodePort
    nodePorts:
      http: 32080
      https: 32443
      tcp:
        8080: 32808
EOF
helm install ingress-nginx/ingress-nginx  --generate-name --values values.yaml
