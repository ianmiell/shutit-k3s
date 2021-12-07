def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# Set up istio
	shutit_session.send('curl -sL https://istio.io/downloadIstioctl | sh -')
	shutit_session.add_to_bashrc('export PATH=$PATH:$HOME/.istioctl/bin')
	shutit_session.add_to_bashrc('export KUBECONFIG=~/.kube/config')
	shutit_session.send('export PATH=$PATH:$HOME/.istioctl/bin')
	shutit_session.send('export KUBECONFIG=~/.kube/config')
	# Set up Istio operator
	shutit_session.send('istioctl operator init')
	# https://istio.io/latest/docs/tasks/traffic-management/egress/egress-gateway/
	# Set up Istio control plane
	# Block by default (meshConfig)
	# Set up egress gateway
	shutit_session.send(('cat <<EOF | kubectl apply -f -\n'
	                     'apiVersion: install.istio.io/v1alpha1\n'
	                     'kind: IstioOperator\n'
	                     'metadata:\n'
	                     '  namespace: istio-system\n'
	                     '  name: example-istiocontrolplane\n'
	                     'spec:\n'
	                     '  profile: demo\n'
	                     '  components:\n'
	                     '    egressGateways:\n'
	                     '    - name: istio-egressgateway\n'
	                     '      enabled: true\n'
	                     '  meshConfig:\n'
	                     '    outboundTrafficPolicy:\n'
	                     '      mode: REGISTRY_ONLY\n'
	                     'EOF'))
	# Label the default namespace for istio injection
	shutit_session.send("kubectl get istiooperator example-istiocontrolplane -n istio-system -o jsonpath='{.spec.meshConfig.outboundTrafficPolicy.mode}'  # get the outbound traffic policy")
	shutit_session.send('kubectl label namespace default istio-injection=enabled')
	shutit_session.send('kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.12/samples/sleep/sleep.yaml')
	shutit_session.send('export SOURCE_POD=$(kubectl get pod -l app=sleep -o jsonpath={.items..metadata.name})')
	# Check that we can't go out
	shutit_session.send_and_expect('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSI https://www.google.com 2>&1', 'exit code 35')
	shutit_session.send('''kubectl create -f <(cat << EOF
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: se_example
spec:
  hosts:
  - www.google.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  resolution: DNS
  location: MESH_EXTERNAL
EOF
)''')
	# Check that we can go out to google and not to bbc
	shutit_session.send('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSI https://www.google.com')
	shutit_session.send_and_expect('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSI https://www.bbc.co.uk 2>&1', 'exit code 35')
	# Use wildcard. Note that resolution needs to be NONE for wildcard
	shutit_session.send('''kubectl apply -f <(cat << EOF
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: se_example
spec:
  hosts:
  - "*"
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  resolution: NONE
  location: MESH_EXTERNAL
EOF
)''')
	# Check that we can go out to google and to bbc
	shutit_session.send('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSI https://www.google.com')
	shutit_session.send('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSI https://www.bbc.co.uk')
	shutit_session.send('')
