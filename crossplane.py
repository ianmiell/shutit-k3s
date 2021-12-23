def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# Set up crossplane
	shutit_session.send('gcp.json','SERVICE_ACCOUNT_KEY_DOWNLOADED.json')
	shutit_session.pause_point('gcp file?')
	shutit_session.send('kubectl create namespace crossplane-system')
	shutit_session.send('helm repo add crossplane-stable https://charts.crossplane.io/stable')
	shutit_session.send('helm repo update')
	shutit_session.send('helm install crossplane --namespace crossplane-system crossplane-stable/crossplane')
	shutit_session.send('curl -sL https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh | sh')
	shutit_session.send('mv kubectl-crossplane /usr/local/bin')
	aws_access_key_id = shutit_session.get_input('input aws_access_key_id: ')
	aws_secret_access_key = shutit_session.get_input('input aws_secret_access_key: ')
	shutit_session.send('kubectl rollout -n crossplane-system status deployment/crossplane')
	shutit_session.send('kubectl rollout -n crossplane-system status deployment/crossplane-rbac-manager')
	shutit_session.send('kubectl crossplane install provider crossplane/provider-aws:v0.19.1')
	shutit_session.send('sleep 60')
    # TODO: $ watch kubectl get all -n crossplane-system
	shutit_session.send(r'export BASE64ENCODED_AWS_ACCOUNT_CREDS=$(echo -e "[default]\naws_access_key_id = ' + aws_access_key_id + r'\naws_secret_access_key = ' + aws_secret_access_key + '" | base64  | tr -d "\n")')
	shutit_session.send('''cat > provider-config.yaml <<EOF
---
apiVersion: v1
kind: Secret
metadata:
  name: aws-account-creds
  namespace: crossplane-system
type: Opaque
data:
  credentials: ${BASE64ENCODED_AWS_ACCOUNT_CREDS}
---
apiVersion: aws.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: aws-provider-config
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: aws-account-creds
      key: credentials
EOF''')
	shutit_session.send('kubectl apply -f provider-config.yaml')
	shutit_session.send('''cat > s3-example.yaml <<EOF
---
apiVersion: s3.aws.crossplane.io/v1beta1
kind: Bucket
metadata:
  name: s3-example-0242ac130002x # try a new unique name
  annotations:
    crossplane.io/external-name: s3-example-0242ac130002x
  labels:
    name: s3-example-0242ac130002
spec:
  forProvider:
    acl: public-read
    locationConstraint: us-east-2
    tagging:
      tagSet:
      - key: Name
        value: s3-example-12312312a
      - key: Environment
        value: example
      - key: Owner
        value: SomeOwner
  providerConfigRef:
    name: aws-provider-config  # we need to reference the config that we created before
EOF''')
	shutit_session.send('kubectl apply -f s3-example.yaml')
	shutit_session.send_until('kubectl get bucket --no-headers','.*True.*')
	shutit_session.send('kubectl delete -f s3-example.yaml')
	# Part 1.2
	shutit_session.send('kubectl crossplane install provider crossplane/provider-gcp:v0.19.0')
	shutit_session.send('export BASE64ENCODED_GCP_PROVIDER_CREDS=$(base64 ~/SERVICE_ACCOUNT_KEY_DOWNLOADED.json | tr -d "\n")')
	shutit_session.pause_point('kubectl get all -n crossplane-system')
