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
	                     'EOF'))
	# Label the default namespace for istio injection
	shutit_session.send('kubectl label namespace default istio-injection=enabled')
	shutit_session.send('kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.12/samples/sleep/sleep.yaml')
	shutit_session.send('export SOURCE_POD=$(kubectl get pod -l app=sleep -o jsonpath={.items..metadata.name})')
	shutit_session.send('')
