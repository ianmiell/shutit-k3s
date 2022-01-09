def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# Set up env
	shutit_session.send_host_file('SERVICE_ACCOUNT_KEY_DOWNLOADED.json','gcp.json')
	shutit_session.send_host_file('aws.sh','aws.sh')
	shutit_session.send(r'export BASE64ENCODED_AWS_ACCOUNT_CREDS=$(cat aws.sh | base64  | tr -d "\n")')
	#shutit_session.send('cat aws.sh >> ~/.bashrc')
	# Set up crossplane
	shutit_session.send('kubectl create namespace crossplane-system')
	shutit_session.send('helm repo add crossplane-stable https://charts.crossplane.io/stable')
	shutit_session.send('helm repo update')
	shutit_session.send('helm install crossplane --namespace crossplane-system crossplane-stable/crossplane')
	shutit_session.send('curl -sL https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh | sh')
	shutit_session.send('mv kubectl-crossplane /usr/local/bin')
	shutit_session.send('kubectl rollout -n crossplane-system status deployment/crossplane')
	shutit_session.send('kubectl rollout -n crossplane-system status deployment/crossplane-rbac-manager')
	shutit_session.send('kubectl crossplane install provider crossplane/provider-aws:v0.19.1')
	shutit_session.send('kubectl crossplane install provider crossplane/provider-gcp:v0.19.0')
	shutit_session.send('sleep 60')
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
#	shutit_session.send('kubectl apply -f s3-example.yaml')
#	shutit_session.send_until('kubectl get bucket.s3.aws.crossplane.io --no-headers','.*True.*')
#	shutit_session.send('kubectl delete -f s3-example.yaml')
#	# Part 1.2
	shutit_session.send('export BASE64ENCODED_GCP_PROVIDER_CREDS=$(base64 ~/SERVICE_ACCOUNT_KEY_DOWNLOADED.json | tr -d "\n")')
	shutit_session.send('''cat > provider-config-gcp.yaml <<EOF
---
apiVersion: v1
kind: Secret
metadata:
  name: gcp-account-creds
  namespace: crossplane-system
type: Opaque
data:
  credentials: ${BASE64ENCODED_GCP_PROVIDER_CREDS}
---
apiVersion: gcp.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: gcp-provider-config
spec:
  projectID: crossplane-336411
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: gcp-account-creds
      key: credentials
EOF''')
	shutit_session.send('kubectl apply -f provider-config-gcp.yaml')
#	shutit_session.send('''cat > gcs-example.yaml <<EOF
#---
#apiVersion: storage.gcp.crossplane.io/v1alpha3
#kind: Bucket
#metadata:
#  name: gcs-example-0242ac130002x # try a new unique name
#  annotations:
#    crossplane.io/external-name: gcs-example-0242ac130002
#  labels:
#    name: gcs-example-0242ac130002x
#spec:
#  labels:
#    name: gcs-example-12312312ax    # need to be lowercase for gcp
#    environment: example
#    owner: someowner
#  providerConfigRef:
#    name: gcp-provider-config  # we need to reference the config that we created before
#EOF''')
#	shutit_session.send('kubectl apply -f gcs-example.yaml')
#	shutit_session.send_until('kubectl get buckets.storage.gcp.crossplane.io --no-headers','.*True.*')
#	shutit_session.send('kubectl delete -f gcs-example.yaml')
	# 1.3
	shutit_session.pause_point('Go from here')
	shutit_session.send('''cat > generic-storage-xrd.yml <<EOF
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: clusterstorages.example.org
spec:
  group: example.org
  names:
    kind: ClusterStorage
    plural: clusterstorages
  claimNames:
    kind: Storage
    plural: storages
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              parameters:
                type: object
                properties:
                  name:
                    type: string
                required:
                  - name
            required:
              - parameters
EOF''')
	shutit_session.send('kubectl apply -f generic-storage-xrd.yml')
	if shutit_session.send_and_get_output('kubectl get crds | grep "storages.example" | wc -l') != '2':
		shutit_session.pause_point('Wrong number of storages.examples')
	shutit_session.send('''cat > clustergenericstorages-composition-gcp.yaml <<EOF
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: clusterstorages.gcp.example.org
  labels:
    provider: gcp
    environment: dev
spec:
  compositeTypeRef:
    apiVersion: example.org/v1alpha1
    kind: ClusterStorage
  resources:
    - name: bucket
      base:
        apiVersion: storage.gcp.crossplane.io/v1alpha3
        kind: Bucket
        spec:
          bucketPolicyOnly:
            enabled: true
          defaultEventBasedHold: false
          deletionPolicy: "Delete"
          labels:
            environment: example
            owner: someowner
          providerConfigRef:
            name: gcp-provider-config
      patches:
        - fromFieldPath: "spec.parameters.name"
          toFieldPath: "metadata.name"
        - fromFieldPath: "spec.parameters.name"
          toFieldPath: "spec.labels.name"
EOF''')
	shutit_session.send('kubectl apply -f clustergenericstorages-composition-gcp.yaml')
	shutit_session.send('''cat > generic-storage.yaml <<EOF
apiVersion: example.org/v1alpha1
kind: Storage
metadata:
  name: my-bucket-13jk123j
  namespace: default
spec:
  parameters:
    name: my-bucket-13jk123j
  compositionSelector:
    matchLabels:
      environment: dev
EOF''')
	shutit_session.send('kubectl apply -f generic-storage.yaml')
	shutit_session.send_until('kubectl get buckets.storage.gcp.crossplane.io --no-headers','.*True.*')
	shutit_session.pause_point('point2')
	shutit_session.send('''cat > clustergenericstorages-composition-aws.yaml <<EOF
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: clusterstorages.aws.example.org
  labels:
    provider: aws
    environment: dev
spec:
  compositeTypeRef:
    apiVersion: example.org/v1alpha1
    kind: ClusterStorage
  resources:
    - name: bucket
      base:
        apiVersion: s3.aws.crossplane.io/v1beta1
        kind: Bucket
        spec:
          forProvider:
            acl: public-read
            locationConstraint: us-east-2
            tagging:
              tagSet:
              - key: Environment
                value: example
              - key: Owner
                value: SomeOwner
          providerConfigRef:
            name: aws-provider-config
      patches:
        - fromFieldPath: "spec.parameters.name"
          toFieldPath: "metadata.name"
        - fromFieldPath: "spec.parameters.name"
          toFieldPath: "spec.labels.Name"
EOF''')
	shutit_session.send('kubectl apply -f clustergenericstorages-composition-gcp.yaml')
	shutit_session.send('kubectl delete -f generic-storage.yaml')
	shutit_session.send('sed -i "s|provider: [^ ]*|provider: aws|g" generic-storage.yaml')
	shutit_session.send('cat generic-storage.yaml # you can check the file to see if it is really changed to aws')
	shutit_session.send('kubectl apply -f generic-storage.yaml')
	shutit_session.send_until('kubectl get buckets.s3.aws.crossplane.io --no-headers','.*True.*')
	shutit_session.send('kubectl delete -f generic-storage.yaml')
	shutit_session.send('sed -i "s|provider: [^ ]*|environment: dev|g" generic-storage.yaml')
	shutit_session.send('cat generic-storage.yaml # you can check the file to see if it is really changed to aws')
	shutit_session.send('kubectl apply -f generic-storage.yaml')
	shutit_session.pause_point('1.3 DONE check there is only one bucket')
