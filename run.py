def run(shutit_sessions, machines):
	machine1_ip = machines['machine1']['ip']
	machine2_ip = machines['machine2']['ip']
	machine3_ip = machines['machine3']['ip']
	machine4_ip = machines['machine4']['ip']
	machine5_ip = machines['machine5']['ip']

	# Set up /etc/hosts
	for machine in sorted(machines.keys()):
		for machine_k in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			shutit_session.send('echo ' + machines[machine_k]['ip'] + ' ' + machine_k + ' ' + machines[machine_k]['fqdn'] + ' >> /etc/hosts')

	# Set up first master
	shutit_session = shutit_sessions['machine1']
	# no traefik because we are using istio ingress, flannel iface and the other ip references to make it go to the right ip address
	shutit_session.send('''curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--cluster-init --flannel-iface enp0s8 --no-deploy traefik --tls-san $(hostname) --advertise-address ''' + machine1_ip + ''' --bind-address ''' + machine1_ip + ''' --node-ip ''' + machine1_ip + '''" sh -''')
	k3s_token = shutit_session.send_and_get_output('cat /var/lib/rancher/k3s/server/node-token')
	shutit_session.send('mkdir -p ~/.kube')
	shutit_session.send('cp /etc/rancher/k3s/k3s.yaml ~/.kube/config')

	for machine in ('machine2','machine3'):
		shutit_session = shutit_sessions[machine]
		machine_ip = machines[machine]['ip']
		shutit_session.send('''curl -sfL http://get.k3s.io | INSTALL_K3S_EXEC="server --flannel-iface enp0s8 --no-deploy traefik --server https://machine1:6443 --token ''' + k3s_token + ''' --tls-san $(hostname) --bind-address ''' + machine_ip + ''' --advertise-address ''' + machine_ip + ''' --node-ip ''' + machine_ip + '''" sh -''')

	for machine in ('machine4','machine5'):
		shutit_session = shutit_sessions[machine]
		machine_ip = machines[machine]['ip']
		shutit_session.send('curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent --flannel-iface enp0s8 --server https://machine1:6443 --token ' + k3s_token + ' --node-ip ' + machine_ip + '" sh -')

	# Set up k9s
	shutit_session = shutit_sessions['machine1']
	shutit_session.send('cd /tmp')
	shutit_session.send('wget https://github.com/derailed/k9s/releases/download/v0.24.15/k9s_Linux_x86_64.tar.gz')
	shutit_session.send('tar -zxvf k9s_Linux_x86_64.tar.gz')
	shutit_session.send('mv k9s /usr/bin/k9s')
	shutit_session.send('cd -')
	# Set up istio
	shutit_session.send('curl -sL https://istio.io/downloadIstioctl | sh -')
	shutit_session.add_to_bashrc('export PATH=$PATH:$HOME/.istioctl/bin')
	shutit_session.add_to_bashrc('export KUBECONFIG=~/.kube/config')
	shutit_session.send('export PATH=$PATH:$HOME/.istioctl/bin')
	shutit_session.send('export KUBECONFIG=~/.kube/config')
	# Set up Istio operator
	shutit_session.send('istioctl operator init')
	# Set up Istio control plane
	shutit_session.send(('kubectl apply -f - <<EOF\n'
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
	# TODO: determine when everything is ready rather than just wait
	shutit_session.send('sleep 120')
	# Set up httpbin application
	shutit_session.send('kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.11/samples/httpbin/httpbin.yaml')
	# Configure ingress gateway
	shutit_session.send(('kubectl apply -f - <<EOF\n'
	                     'apiVersion: networking.istio.io/v1alpha3\n'
	                     'kind: Gateway\n'
	                     'metadata:\n'
	                     '  name: httpbin-gateway\n'
	                     'spec:\n'
	                     '  selector:\n'
	                     '    istio: ingressgateway # use Istio default gateway implementation\n'
	                     '  servers:\n'
	                     '  - port:\n'
	                     '      number: 80\n'
	                     '      name: http\n'
	                     '      protocol: HTTP\n'
	                     '    hosts:\n'
	                     '    - "httpbin.example.com"\n'
	                     'EOF'))
	# Configure Istio service
	shutit_session.send(('kubectl apply -f - <<EOF\n'
	                     'apiVersion: networking.istio.io/v1alpha3\n'
	                     'kind: VirtualService\n'
	                     'metadata:\n'
	                     '  name: httpbin\n'
	                     'spec:\n'
	                     '  hosts:\n'
	                     '  - "httpbin.example.com"\n'
	                     '  gateways:\n'
	                     '  - httpbin-gateway\n'
	                     '  http:\n'
	                     '  - match:\n'
	                     '    - uri:\n'
	                     '        prefix: /status\n'
	                     '    - uri:\n'
	                     '        prefix: /delay\n'
	                     '    route:\n'
	                     '    - destination:\n'
	                     '        port:\n'
	                     '          number: 8000\n'
	                     '        host: httpbin\n'
	                     'EOF'))
	shutit_session.send("""export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')""")
	shutit_session.send("""export SECURE_INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="https")].nodePort}')""")
	shutit_session.send("""export TCP_INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="tcp")].nodePort}')""")
	shutit_session.send("""export INGRESS_HOST=$(kubectl get po -l istio=ingressgateway -n istio-system -o jsonpath='{.items[0].status.hostIP}')""")
	shutit_session.send('curl -s -I -HHost:httpbin.example.com "http://$INGRESS_HOST:$INGRESS_PORT/status/200"')

	# Create simple deployment
	shutit_session.send('kubectl apply -f https://raw.githubusercontent.com/ContainerSolutions/kubernetes-examples/master/Deployment/webserver.yaml')
	# Create Gateway and VirtualService
	shutit_session.send(('kubectl apply -f - <<EOF\n'
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
	                     '---\n'
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
	                     '          number: 80  # Matches the port of the service'))
	shutit_session.send('curl -HHost:webserver-simple-service.com "http://$INGRESS_HOST:$INGRESS_PORT/"')
	shutit_session.pause_point('END')
