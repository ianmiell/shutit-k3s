def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# https://www.opcito.com/blogs/implementing-kubernetes-operators-with-python
	shutit_session.send('mkdir python_operator && cd python_operator')
	shutit_session.send('''cat > custom_resource_definition.yml << EOF
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: grafana.opcito.org
spec:
  scope: Namespaced
  group: opcito.org
  versions:
    - name: v1
      served: true
      storage: true
  names:
    kind: Grafana
    plural: grafana
    singular: grafana
    shortNames:
      - gf
      - gfn
EOF''')
	shutit_session.send('kubectl apply -f custom_resource_definition.yml')
	shutit_session.send('''cat > operator_handler.py << EOF
import kopf
import kubernetes
import yaml
@kopf.on.create('opcito.org', 'v1', 'grafana')
def create_fn(body, spec, **kwargs):
    # Get info from grafana object
    name = body['metadata']['name']
    namespace = body['metadata']['namespace']
    nodeport = spec['nodeport']
    image = 'grafana/grafana'
    port = 3000
    if not nodeport:
        raise kopf.HandlerFatalError(f"Nodeport must be set. Got {nodeport}.")
    # Pod template
    pod = {'apiVersion': 'v1', 'metadata': {'name' : name, 'labels': {'app': 'grafana'}},'spec': {'containers': [ { 'image': image, 'name': name }]}}
    # Service template
    svc = {'apiVersion': 'v1', 'metadata': {'name' : name}, 'spec': { 'selector': {'app': 'grafana'}, 'type': 'NodePort', 'ports': [{ 'port': port, 'targetPort': port,  'nodePort': nodeport }]}}
    # Make the Pod and Service the children of the grafana object
    kopf.adopt(pod, owner=body)
    kopf.adopt(svc, owner=body)
    # Object used to communicate with the API Server
    api = kubernetes.client.CoreV1Api()
    # Create Pod
    obj = api.create_namespaced_pod(namespace, pod)
    print(f"Pod {obj.metadata.name} created")
    # Create Service
    obj = api.create_namespaced_service(namespace, svc)
    print(f"NodePort Service {obj.metadata.name} created, exposing on port {obj.spec.ports[0].node_port}")
    # Update status
    msg = f"Pod and Service created for grafana object {name}"
    return {'message': msg}
@kopf.on.delete('opcito.org', 'v1', 'grafana')
def delete(body, **kwargs):
    msg = f"Grafana {body['metadata']['name']} and its Pod / Service children deleted"
    return {'message': msg}
EOF''')
	# DONE OUTSIDE
#	shutit_session.send('''cat > Dockerfile << EOF
#FROM python:3.7
#RUN pip install kopf && pip install kubernetes
#COPY operator_handler.py /operator_handler.py
#CMD kopf run --standalone /operator_handler.py
#EOF''')
	# docker image build -t imiell/operator-grafana:latest .
	# docker image push imiell/operator-grafana:latest
	shutit_session.send('''cat > service_account.yml << EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: grafana-operator
EOF''')
	shutit_session.send('kubectl apply -f service_account.yml')
	shutit_session.send('''cat > service_account_binding.yml << EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: grafana-operator
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: grafana-operator
    namespace: default
EOF''')
	shutit_session.send('kubectl apply -f service_account_binding.yml')
	shutit_session.send('''cat > grafana_operator.yml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana-operator
spec:
  selector:
    matchLabels:
      app: grafana-operator
  template:
    metadata:
      labels:
        app: grafana-operator
    spec:
      serviceAccountName: grafana-operator
      containers:
        - image: sanket07/operator-grafana
          name: grafana-operator
EOF''')
	shutit_session.send('kubectl apply -f grafana_operator.yml')

	shutit_session.pause_point('continue with https://www.opcito.com/blogs/implementing-kubernetes-operators-with-python')

