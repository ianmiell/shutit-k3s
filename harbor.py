def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	shutit_session.pause_point('''
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.9.1/cert-manager.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.3.1/deploy/static/provider/cloud/deploy.yaml
kubectl apply -f https://raw.githubusercontent.com/goharbor/harbor-operator/master/manifests/cluster/deployment.yaml''')

#https://github.com/goharbor/harbor-operator/blob/master/docs/installation/kustomization-all-in-one.md
#kubectl apply -f https://raw.githubusercontent.com/goharbor/harbor-operator/release-1.3.0/manifests/cluster/deployment.yaml
