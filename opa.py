def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# https://www.openpolicyagent.org/docs/v0.12.2/kubernetes-admission-control/
	TODO: annotate based on above page
	# 1. (Ignored, minikube)
	# 2. Create ns
	shutit_session.send('kubectl create ns opa')
	shutit_session.send('kubectl config set-context opa-tutorial --namespace opa')
	shutit_session.send('kubectl config use-context opa-tutorial')
	# 3. Deploy OPA on top of kubernetes
	# Communication between Kubernetes and OPA must be secured using TLS. To configure TLS, use openssl to create a certificate authority (CA) and certificate/key pair for OPA:
	shutit_session.send('openssl genrsa -out ca.key 2048')
	shutit_session.send('openssl req -x509 -new -nodes -key ca.key -days 100000 -out ca.crt -subj "/CN=admission_ca"')
	# Generate the TLS key and certificate for OPA:
	shutit_session.send('''cat >server.conf <<EOF
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
[req_distinguished_name]
[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth, serverAuth
EOF''')
	shutit_session.send('openssl genrsa -out server.key 2048')
	shutit_session.send('openssl req -new -key server.key -out server.csr -subj "/CN=opa.opa.svc" -config server.conf')
	shutit_session.send('openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 100000 -extensions v3_req -extfile server.conf')
	# Note: the Common Name value you give to openssl MUST match the name of the OPA service created below.
	# Create a Secret to store the TLS credentials for OPA:
	shutit_session.send('kubectl create secret tls opa-server --cert=server.crt --key=server.key')
	# Next, use the file below to deploy OPA as an admission controller.
	shutit_session.send('''cat > admission-controller.yaml << 'EOF'
# Grant OPA/kube-mgmt read-only access to resources. This lets kube-mgmt
# replicate resources into OPA so they can be used in policies.
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: opa-viewer
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: Group
  name: system:serviceaccounts:opa
  apiGroup: rbac.authorization.k8s.io
---
# Define role for OPA/kube-mgmt to update configmaps with policy status.
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: opa
  name: configmap-modifier
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["update", "patch"]
---
# Grant OPA/kube-mgmt role defined above.
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: opa
  name: opa-configmap-modifier
roleRef:
  kind: Role
  name: configmap-modifier
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: Group
  name: system:serviceaccounts:opa
  apiGroup: rbac.authorization.k8s.io
---
kind: Service
apiVersion: v1
metadata:
  name: opa
  namespace: opa
spec:
  selector:
    app: opa
  ports:
  - name: https
    protocol: TCP
    port: 443
    targetPort: 443
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  labels:
    app: opa
  namespace: opa
  name: opa
spec:
  replicas: 1
  selector:
    matchLabels:
      app: opa
  template:
    metadata:
      labels:
        app: opa
      name: opa
    spec:
      containers:
        # WARNING: OPA is NOT running with an authorization policy configured. This
        # means that clients can read and write policies in OPA. If you are
        # deploying OPA in an insecure environment, be sure to configure
        # authentication and authorization on the daemon. See the Security page for
        # details: https://www.openpolicyagent.org/docs/security.html.
        - name: opa
          image: openpolicyagent/opa:0.12.2
          args:
            - "run"
            - "--server"
            - "--tls-cert-file=/certs/tls.crt"
            - "--tls-private-key-file=/certs/tls.key"
            - "--addr=0.0.0.0:443"
            - "--addr=http://127.0.0.1:8181"
          volumeMounts:
            - readOnly: true
              mountPath: /certs
              name: opa-server
        - name: kube-mgmt
          image: openpolicyagent/kube-mgmt:0.8
          args:
            - "--replicate-cluster=v1/namespaces"
            - "--replicate=extensions/v1beta1/ingresses"
      volumes:
        - name: opa-server
          secret:
            secretName: opa-server
---
kind: ConfigMap
apiVersion: v1
metadata:
  name: opa-default-system-main
  namespace: opa
data:
  main: |
    package system

    import data.kubernetes.admission

    main = {
      "apiVersion": "admission.k8s.io/v1beta1",
      "kind": "AdmissionReview",
      "response": response,
    }

    default response = {"allowed": true}

    response = {
        "allowed": false,
        "status": {
            "reason": reason,
        },
    } {
        reason = concat(", ", admission.deny)
        reason != ""
    }
EOF''')
	shutit_session.send('kubectl apply -f admission-controller.yaml')
	# Next label kube-system and the opa namespace so that OPA does not control the resources in those namespaces.
	shutit_session.send('kubectl label ns kube-system openpolicyagent.org/webhook=ignore')
	shutit_session.send('kubectl label ns opa openpolicyagent.org/webhook=ignore')
	# When OPA starts, the kube-mgmt container will load Kubernetes Namespace and Ingress objects into OPA. You can configure the sidecar to load any kind of Kubernetes object into OPA. The sidecar establishes watches on the Kubernetes API server so that OPA has access to an eventually consistent cache of Kubernetes objects.
	#Next, generate the manifest that will be used to register OPA as an admission controller. This webhook will ignore any namespace with the label openpolicyagent.org/webhook=ignore.
	# The generated configuration file includes a base64 encoded representation of the CA certificate so that TLS connections can be established between the Kubernetes API server and OPA.
	shutit_session.send('''cat > webhook-configuration.yaml <<EOF
kind: ValidatingWebhookConfiguration
apiVersion: admissionregistration.k8s.io/v1beta1
metadata:
  name: opa-validating-webhook
webhooks:
  - name: validating-webhook.openpolicyagent.org
    namespaceSelector:
      matchExpressions:
      - key: openpolicyagent.org/webhook
        operator: NotIn
        values:
        - ignore
    rules:
      - operations: ["CREATE", "UPDATE"]
        apiGroups: ["*"]
        apiVersions: ["*"]
        resources: ["*"]
    clientConfig:
      caBundle: $(cat ca.crt | base64 | tr -d '\n')
      service:
        namespace: opa
        name: opa
EOF''')
	# Finally, register OPA as an admission controller:
	shutit_session.send('kubectl apply -f webhook-configuration.yaml')
	# You can follow the OPA logs to see the webhook requests being issued by the Kubernetes API server:
	shutit_session.pause_point('kubectl logs -l app=opa -c opa')
