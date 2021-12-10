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
	shutit_session.send('sleep 60  # wait for things to settle down')
	shutit_session.send('export SOURCE_POD=$(kubectl get pod -l app=sleep -o jsonpath={.items..metadata.name})')
	shutit_session.send('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSI https://www.google.com 2>&1', 'exit code 35', note='Check that we cannot go out to google')
	shutit_session.send('''kubectl create -f <(cat << EOF
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: se-example
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
)''', note='Create a serviceentry that goes out through the sidecar direct to the outside world to google only')
	# Check that we can go out to google and not to bbc
	shutit_session.send('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSI https://www.google.com', note='Now go to google')
	shutit_session.send('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSI https://www.bbc.co.uk 2>&1', 'exit code 35', note='But we still cannot go to the bbc')
	# Use wildcard. Note that resolution needs to be NONE for wildcard
	shutit_session.send('''kubectl apply -f <(cat << EOF
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: se-example
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
)''', note='Do a wildcard serviceentry, which requires resolution: NONE')
	# Check that we can go out to google and to bbc
	shutit_session.send('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSI https://www.google.com', note='Check we can go to google')
	shutit_session.send('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSI https://www.bbc.co.uk', note='Check we can go to bbc too')
	# Delete service entry
	shutit_session.send('kubectl delete serviceentry se-example', note='Delete service entry')
	# Create service entry for just cnn
	shutit_session.send('''kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: cnn
spec:
  hosts:
  - edition.cnn.com
  ports:
  - number: 80
    name: http-port
    protocol: HTTP
  - number: 443
    name: https
    protocol: HTTPS
  resolution: DNS
EOF''', note='Create service entry for edition.cnn.com')
	shutit_session.send('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSL -o /dev/null -D - http://edition.cnn.com/politics', note='We should be able to go there')
	shutit_session.send('''kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: istio-egressgateway
spec:
  selector:
    istio: egressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - edition.cnn.com
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: egressgateway-for-cnn
spec:
  host: istio-egressgateway.istio-system.svc.cluster.local
  subsets:
  - name: cnn
EOF''', note='Set up egress gateway for port 80 edition.cnn.com, and a destinationrule to go the egress gateway.')
	shutit_session.send('''kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: direct-cnn-through-egress-gateway
spec:
  hosts:
  - edition.cnn.com
  gateways:
  - istio-egressgateway
  - mesh
  http:
  - match:
    - gateways:
      - mesh
      port: 80
    route:
    - destination:
        host: istio-egressgateway.istio-system.svc.cluster.local
        subset: cnn
        port:
          number: 80
      weight: 100
  - match:
    - gateways:
      - istio-egressgateway
      port: 80
    route:
    - destination:
        host: edition.cnn.com
        port:
          number: 80
      weight: 100
EOF''', note='Set up VirtualService to direct traffic from the sidecars to the egress gateway to the external service')
	# Should still work
	shutit_session.send('kubectl exec "$SOURCE_POD" -c sleep -- curl -sSL -o /dev/null -D - http://edition.cnn.com/politics', note='This should still work')
	# Should show up in logs
	shutit_session.send('kubectl logs -l istio=egressgateway -c istio-proxy -n istio-system | tail', note='We should see politics in the egress logs, showing it has gone through the egress')
	# Should show up in logs
	shutit_session.send('kubectl logs -l istio=egressgateway -c istio-proxy -n istio-system | grep politics')
	shutit_session.pause_point('')
