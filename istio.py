def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# Set up istio - https://istio.io/latest/docs/setup/getting-started/
	shutit_session.send('curl -sL https://istio.io/downloadIstioctl | sh -')
	shutit_session.send('export PATH=$PATH:~/istio-1.14.1/bin')
	shutit_session.send('istioctl x precheck')
	shutit_session.send('istioctl install --set profile=demo -y')
	shutit_session.send('kubectl label namespace default istio-injection=enabled')
	shutit_session.send('kubectl apply -f ./istio-1.14/samples/bookinfo/platform/kube/bookinfo.yaml')
	shutit_session.send('kubectl apply -f ./istio-1.14/samples/bookinfo/networking/bookinfo-gateway.yaml')  # Create gateway
	shutit_session.send('istioctl analyze')  # all ok?
	shutit_session.send('kubectl get svc istio-ingressgateway -n istio-system')  # Get the external IP(s)
	# Get the HOSTS and PORTS into vars
	shutit_session.send('''export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')''')
	shutit_session.send('''export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}''')
	shutit_session.send('''export SECURE_INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="https")].port}''')
	shutit_session.send('export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT')
	shutit_session.send('curl http://$GATEWAY_URL/productpage"')
	shutit_session.pause_point('')


