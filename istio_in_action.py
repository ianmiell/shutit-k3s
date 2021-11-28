def run(shutit_sessions, machines):
	machine1_ip = machines['machine1']['ip']
	machine2_ip = machines['machine2']['ip']
	machine3_ip = machines['machine3']['ip']
	machine4_ip = machines['machine4']['ip']
	machine5_ip = machines['machine5']['ip']

	# Set up istio
	shutit_session.send('curl -sL https://istio.io/downloadIstioctl | sh -')
	shutit_session.add_to_bashrc('export PATH=$PATH:$HOME/.istioctl/bin')
	shutit_session.add_to_bashrc('export KUBECONFIG=~/.kube/config')
	shutit_session.send('export PATH=$PATH:$HOME/.istioctl/bin')
	shutit_session.send('export KUBECONFIG=~/.kube/config')
	# Set up Istio operator
	shutit_session.send('istioctl operator init')
	# Set up Istio control plane
	shutit_session.send(('cat <<EOF | kubectl apply -f -\n'
	                     'apiVersion: install.istio.io/v1alpha1\n'
	                     'kind: IstioOperator\n'
	                     'metadata:\n'
	                     '  namespace: istio-system\n'
	                     '  name: example-istiocontrolplane\n'
	                     'spec:\n'
	                     '  profile: demo\n'
	                     'EOF'))
	# Label the default namespace for istio injection
	shutit_session.send('kubectl label namespace default istio-injection=enabled')
	# Get source
	shutit_session.send('git clone https://github.com/istioinaction/book-source-code')
	shutit_session.send('cd book-source-code')
	# TODO: determine when everything is ready rather than just wait
	shutit_session.send('sleep 120')
	# Create simple deployment
	shutit_session.send('kubectl apply -f https://raw.githubusercontent.com/ContainerSolutions/kubernetes-examples/master/Deployment/webserver.yaml')
	# Create Gateway and VirtualService
	shutit_session.send(('cat <<EOF | kubectl apply -f -\n'
	                     'apiVersion: networking.istio.io/v1beta1\n'
	                     'kind: Gateway\n'
	                     'metadata:\n'
	                     '  name: webserver-simple-service-gateway\n'
	                     '  namespace: default\n'
	                     'spec:\n'
	                     '  selector:\n'
	                     '    istio: ingressgateway\n'
	                     '  servers:\n'
	                     '  - hosts:\n'
	                     '    - webserver-simple-service.com\n'
	                     '    port:\n'
	                     '      name: http\n'
	                     '      number: 80\n'
	                     '      protocol: HTTP\n'
                         'EOF'))
	shutit_session.send(('cat <<EOF | kubectl apply -f -\n'
	                     'apiVersion: networking.istio.io/v1beta1\n'
	                     'kind: VirtualService\n'
	                     'metadata:\n'
	                     '  name: webserver-simple-service-virtual-service\n'
	                     '  namespace: default\n'
	                     'spec:\n'
	                     '  gateways:\n'
	                     '  - webserver-simple-service-gateway  # Matches the gateway defined above\n'
	                     '  hosts:\n'
	                     '  - webserver-simple-service.com  # Matches the host defined above\n'
	                     '  http:\n'
	                     '  - match:\n'
	                     '    - uri:\n'
	                     '        prefix: /\n'
	                     '    route:\n'
	                     '    - destination:\n'
	                     '        host: webserver-simple-service\n'
	                     '        port:\n'
	                     '          number: 80  # Matches the port of the service\n'
                         'EOF'))
	shutit_session.send('curl -HHost:webserver-simple-service.com "http://$INGRESS_HOST:$INGRESS_PORT/"')
	shutit_session.send(('cat <<EOF | kubectl apply -f -\n'
	                     'apiVersion: networking.istio.io/v1alpha3\n'
	                     'kind: Gateway\n'
	                     'metadata:\n'
	                     '  name: coolstore-gateway\n'
	                     'spec:\n'
	                     '  selector:\n'
	                     '    istio: ingressgateway\n'
	                     '  servers:\n'
	                     '  - port:\n'
	                     '      number: 80\n'
	                     '      name: http\n'
	                     '      protocol: HTTP\n'
	                     '    hosts:\n'
	                     '    - "webapp.istioinaction.io"\n'
	                     'EOF'))
	shutit_session.send('istioctl -n istio-system proxy-config listener deploy/istio-ingressgateway  # see if it took effect')
	shutit_session.send('istioctl proxy-config route deploy/istio-ingressgateway -o json --name http.80  -n istio-system  # virtual services does not have any routes')
	shutit_session.send('''cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: webapp-vs-from-gw
spec:
  hosts:
  - "webapp.istioinaction.io"
  gateways:
  - coolstore-gateway
  http:
  - route:
    - destination:
        host: webapp
        port:
          number: 8080
EOF''')
	shutit_session.send('istioctl proxy-config route deploy/istio-ingressgateway -o json --name http.80  -n istio-system  # virtual services has added route')
	shutit_session.send('kubectl config set-context $(kubectl config current-context) --namespace=istioinaction')
	shutit_session.send('kubectl apply -f services/catalog/kubernetes/catalog.yaml')
	shutit_session.send('kubectl apply -f services/webapp/kubernetes/webapp.yaml')
	# TODO: check all are running
	shutit_session.send('kubectl get pod')
	shutit_session.send('kubectl get gateway')
	shutit_session.send('kubectl get virtualservice')
	shutit_session.send("URL=$(kubectl -n istio-system get svc istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')")
	shutit_session.send('curl http://localhost/api/catalog -H "Host: webapp.istioinaction.io"')
	# Create a secure ingress
	# In this step, we create the secret in the istio-system namespace. At the time of writing (Istio 1.11.2), the secret that’s used for TLS in the gateway can only be retrieved if it’s in the same namespace as the Istio ingress gateway. The default gateway is run in the istio-system namespace, so that’s where we put the secret. We could run the ingress gateway in a different namespace, but the secret would still have to be in that namespace. In fact, for production, you should run the ingress gateway component in its own namespace, separate from istio-system.
	shutit_session.send('kubectl create -n istio-system secret tls webapp-credential --key ch4/certs/3_application/private/webapp.istioinaction.io.key.pem --cert ch4/certs/3_application/certs/webapp.istioinaction.io.cert.pem')
	# As we can see in our Gateway resource in listing XX, we’ve opened port 443 on our ingress gateway, and we’ve specified its protocol to be HTTPS. Additionally, we’ve added a tls section to our gateway configuration where we’ve specified the locations to find the certificates and keys to use for TLS. Note, these are the same locations that were mounted into the istio-ingressgateway that we saw earlier.
	shutit_session.send('''cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: coolstore-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "webapp.istioinaction.io"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: webapp-credential
    hosts:
    - "webapp.istioinaction.io"
EOF''')
	# Let’s replace our gateway with this new Gateway resource. From the root of the source code:
	shutit_session.send('kubectl apply -f ch4/coolstore-gw-tls.yaml')

	# This means the Certificate presented by the server cannot be verified using the default CA certificate chains. Let’s pass in the proper CA certificate chain to our curl client:
	#shutit_session.send('curl -v -H "Host: webapp.istioinaction.io" https://localhost/api/catalog')
	#shutit_session.send('curl -v -H "Host: webapp.istioinaction.io" https://localhost/api/catalog --cacert ch4/certs/2_intermediate/certs/ca-chain.cert.pem')
	#The client still cannot verify the certificate! This is because the server certificate is issued for webapp.istioinaction.io and we’re calling the Docker for Desktop host (localhost in this case). We can use a curl parameter called --resolve that lets us call the service as though it was at webapp.istioinaction.io but then tell curl to use localhost:
	shutit_session.send('curl -H "Host: webapp.istioinaction.io" https://webapp.istioinaction.io:443/api/catalog --cacert ch4/certs/2_intermediate/certs/ca-chain.cert.pem --resolve webapp.istioinaction.io:443:127.0.0.1')
	# Update http to redirect to https:
	shutit_session.send('kubectl apply -f ch4/coolstore-gw-tls-redirect.yaml gateway.networking.istio.io/coolstore-gateway replaced')
	shutit_session.pause_point('4.3.3 HTTP traffic with mutual TLS https://livebook.manning.com/book/istio-in-action/chapter-4/v-15/131')
