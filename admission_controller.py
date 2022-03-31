def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# First, let's see if we have admissionregistration set up
	shutit_session.send('kubectl api-versions | grep admissionregistration')
	# kyverno
	shutit_session.send('kubectl api-versions | grep admissionregistration')
	shutit_session.send('helm repo add kyverno https://kyverno.github.io/kyverno')
	shutit_session.send('helm install kyverno kyverno/kyverno -n kyverno --create-namespace')
	shutit_session.send('''kubectl create -f- << EOF
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: enforce
  rules:
  - name: check-for-labels
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "label 'app.kubernetes.io/name' is required"
      pattern:
        metadata:
          labels:
            app.kubernetes.io/name: "?*"
EOF''')
	# Should see an error
	shutit_session.send('kubectl create deployment nginx --image=nginx')
	shutit_session.send('kubectl run nginx --image nginx --labels app.kubernetes.io/name=nginx')
	# Create validation rule for namespaces
	shutit_session.send('''kubectl create -f- << EOF
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: automountserviceaccounttoken
spec:
  rules:
    - name: check-for-labels
      match:
        any:
          - resources:
              kinds:
                - ServiceAccount
              name: default
              namespaces:
                - blah*
      mutate:
        patchStrategicMerge:
          automountServiceAccountToken: false
EOF''')
	shutit_session.send('kubectl create ns blahse')
	shutit_session.send('kubectl get sa -o yaml blahse | grep automount')
	shutit_session.send('kubectl create ns b2')
	shutit_session.send('kubectl get sa -o yaml b2 | grep automount')



	## This has been suggested:
	##https://github.com/viveksinghggits/valkontroller/
	#shutit_session.send('git clone https://github.com/viveksinghggits/valkontroller/')
	#shutit_session.send('cd valkontroller')



	# Do we really need to go into all that trouble to modify Kubernetes objects as they are created? Not really, there are generic tools to do so like the KubeMod operator
	# https://github.com/kubemod/kubemod




### UNFINISHED
# https://trstringer.com/kubernetes-mutating-webhook/
#shutit_session.send('git clone https://github.com/trstringer/kubernetes-mutating-webhook')
#shutit_session.send('cd kubernetes-mutating-webhook')

### OUTDATED github 404s
#https://slack.engineering/simple-kubernetes-webhook/

### OUTDATED
#https://medium.com/ovni/writing-a-very-basic-kubernetes-mutating-admission-webhook-398dbbcb63ec
#shutit_session.send('git clone https://github.com/alex-leonhardt/k8s-mutate-webhook')
#ca_bundle = shutit_session.send_and_get_output("kubectl config view --raw --minify --flatten -o jsonpath='{.clusters[].cluster.certificate-authority-data}'")

### OUTDATED
# From: https://docs.giantswarm.io/advanced/custom-admission-controller/
#	shutit_session.send('git clone https://github.com/giantswarm/grumpy')
#	shutit_session.send('cd grumpy')
#	shutit_session.pause_point('ready')

##Load this in:
#apiVersion: admissionregistration.k8s.io/v1beta1
#kind: ValidatingWebhookConfiguration
#metadata:
#  name: grumpy
#webhooks:
#  - name: grumpy
#    clientConfig:
#      service:
#        name: grumpy
#        namespace: default
#        path: "/validate"
#      caBundle: "${CA_BUNDLE}"
#    rules:
#      - operations: ["CREATE"]
#        apiGroups: [""]
#        apiVersions: ["v1"]
#        resources: ["pods"]
#
##From this repo:
#git clone https://github.com/giantswarm/grumpy
#
##run:
#https://github.com/giantswarm/grumpy/blob/instance_migration/gen_certs.sh
#
## Store as secret
#kubectl create secret generic grumpy -n default --from-file=key.pem=certs/grumpy-key.pem --from-file=cert.pem=certs/grumpy-crt.pem
#
## Apply manifest
#https://github.com/giantswarm/grumpy/blob/instance_migration/manifest.yaml
#
## Run the pod
#smooth-app.yml


