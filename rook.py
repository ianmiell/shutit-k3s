def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# TODO: implement: https://documentation.suse.com/sbp/all/html/SBP-rook-ceph-kubernetes/index.html#sec-limit-ceph-specifc-nodes
	# Set up rook https://rook.io/docs/rook/v1.7/quickstart.html
	shutit_session.send('git clone --single-branch --branch v1.7.8 https://github.com/rook/rook.git')
	shutit_session.send('cd rook/cluster/examples')
	shutit_session.send('helm repo add rook-release https://charts.rook.io/release')
	shutit_session.send('helm install --create-namespace --namespace rook-ceph rook-ceph rook-release/rook-ceph')
	shutit_session.send('''kubectl create -f <(cat << EOF
apiVersion: ceph.rook.io/v1
kind: CephCluster
metadata:
  name: rook-ceph
  namespace: rook-ceph # namespace:cluster
spec:
  cephVersion:
    image: quay.io/ceph/ceph:v16.2.6
    allowUnsupported: false
  dataDirHostPath: /var/lib/rook
  skipUpgradeChecks: false
  continueUpgradeAfterChecksEvenIfNotHealthy: false
  waitTimeoutForHealthyOSDInMinutes: 10
  mon:
    count: 3
    allowMultiplePerNode: false
  mgr:
    count: 1
    modules:
      - name: pg_autoscaler
        enabled: true
  dashboard:
    enabled: true
    ssl: true
  monitoring:
    enabled: false
    rulesNamespace: rook-ceph
  network:
  crashCollector:
    disable: false
  cleanupPolicy:
    confirmation: ""
    sanitizeDisks:
      method: quick
      dataSource: zero
      iteration: 1
    allowUninstallWithVolumes: false
#  placement:
#    all:
#      nodeAffinity:
#        requiredDuringSchedulingIgnoredDuringExecution:
#          nodeSelectorTerms:
#          - matchExpressions:
#            - key: storage-node
#              operator: In
#              values:
#              - "true"
  annotations:
  labels:
  resources:
  removeOSDsIfOutAndSafeToRemove: false
  storage: # cluster level storage configuration and selection
    useAllNodes: true
    useAllDevices: true
    config:
    onlyApplyOSDPlacement: false
  disruptionManagement:
    managePodBudgets: true
    osdMaintenanceTimeout: 30
    pgHealthCheckTimeout: 0
    manageMachineDisruptionBudgets: false
    machineDisruptionBudgetNamespace: openshift-machine-api
  healthCheck:
    daemonHealth:
      mon:
        disabled: false
        interval: 45s
      osd:
        disabled: false
        interval: 60s
      status:
        disabled: false
        interval: 60s
    livenessProbe:
      mon:
        disabled: false
      mgr:
        disabled: false
      osd:
        disabled: false
EOF
)''')
	shutit_session.send_until("kubectl get cephcluster -n rook-ceph -o json | jq '.items[0].status.phase'", '"Ready"', cadence=30)
=======
   23  git clone --single-branch --branch v1.7.8 https://github.com/rook/rook.git
   24  cd rook/cluster/examples/kubernetes/ceph
   25  kubectl create -f crds.yaml -f common.yaml -f operator.yaml
   26  kubectl create -f cluster.yaml
>>>>>>> 8472f3e... helm
=======
	shutit_session.send('cd rook/cluster/examples/kubernetes/ceph')
	shutit_session.send('kubectl create -f crds.yaml -f common.yaml -f operator.yaml')
	shutit_session.send('kubectl create -f cluster.yaml')
>>>>>>> 7210fef... latest
	# Create the toolbox
	shutit_session.send('''kubectl create -f <(cat << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rook-ceph-tools
  namespace: rook-ceph
  labels:
    app: rook-ceph-tools
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rook-ceph-tools
  template:
    metadata:
      labels:
        app: rook-ceph-tools
    spec:
      dnsPolicy: ClusterFirstWithHostNet
      containers:
      - name: rook-ceph-tools
        image: rook/ceph:v1.7.8
        command: ["/tini"]
        args: ["-g", "--", "/usr/local/bin/toolbox.sh"]
        imagePullPolicy: IfNotPresent
        env:
          - name: ROOK_CEPH_USERNAME
            valueFrom:
              secretKeyRef:
                name: rook-ceph-mon
                key: ceph-username
          - name: ROOK_CEPH_SECRET
            valueFrom:
              secretKeyRef:
                name: rook-ceph-mon
                key: ceph-secret
        volumeMounts:
          - mountPath: /etc/ceph
            name: ceph-config
          - name: mon-endpoint-volume
            mountPath: /etc/rook
      volumes:
        - name: mon-endpoint-volume
          configMap:
            name: rook-ceph-mon-endpoints
            items:
            - key: data
              path: mon-endpoints
        - name: ceph-config
          emptyDir: {}
      tolerations:
        - key: "node.kubernetes.io/unreachable"
          operator: "Exists"
          effect: "NoExecute"
          tolerationSeconds: 5
EOF
<<<<<<< HEAD
<<<<<<< HEAD
)''')
	shutit_session.send_until('kubectl -n rook-ceph rollout status deploy/rook-ceph-tools | grep successfully.rolled.out | wc -l', '1')
	shutit_session.login(command='kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- bash')
	shutit_session.send_and_require('ceph status', '.*HEALTH_OK.*')
	shutit_session.logout()
	shutit_session.send('kubectl get cephcluster -A')

	# Block store: https://rook.io/docs/rook/v1.7/ceph-block.html
	shutit_session.send('kubectl create -f kubernetes/ceph/csi/rbd/storageclass.yaml')
	shutit_session.send('kubectl create -f kubernetes/mysql.yaml')
	shutit_session.send('kubectl create -f kubernetes/wordpress.yaml')
	shutit_session.send('kubectl get pvc')
	shutit_session.send('kubectl get svc wordpress')

	# Object store: https://rook.io/docs/rook/v1.7/ceph-object.html
	# The below sample will create a CephObjectStore that starts the RGW service in the cluster with an S3 API.  NOTE: This sample requires at least 3 bluestore OSDs, with each OSD located on a different node.  The OSDs must be located on different nodes, because the failureDomain is set to host and the erasureCoded chunk settings require at least 3 different OSDs (2 dataChunks + 1 codingChunks).  See the Object Store CRD, for more detail on the settings available for a CephObjectStore.
	shutit_session.send('kubectl create -f kubernetes/ceph/object.yaml')
	shutit_session.send_until('kubectl -n rook-ceph rollout status deploy/rook-ceph-rgw-my-store-a | grep successfully.rolled.out | wc -l', '1')
	# Now that the object store is configured, next we need to create a bucket where a client can read and write objects. A bucket can be created by defining a storage class, similar to the pattern used by block and file storage. First, define the storage class that will allow object clients to create a bucket. The storage class defines the object storage system, the bucket retention policy, and other properties required by the administrator. Save the following as storageclass-bucket-delete.yaml (the example is named as such due to the Delete reclaim policy).
	# Based on this storage class, an object client can now request a bucket by creating an Object Bucket Claim (OBC). When the OBC is created, the Rook-Ceph bucket provisioner will create a new bucket. Notice that the OBC references the storage class that was created above. Save the following as object-bucket-claim-delete.yaml (the example is named as such due to the Delete reclaim policy):
	shutit_session.send('kubectl apply -f kubernetes/ceph/storageclass-bucket-delete.yaml')
	# Now that the claim is created, the operator will create the bucket as well as generate other artifacts to enable access to the bucket. A secret and ConfigMap are created with the same name as the OBC and in the same namespace. The secret contains credentials used by the application pod to access the bucket. The ConfigMap contains bucket endpoint information and is also consumed by the pod. See the Object Bucket Claim Documentation for more details on the CephObjectBucketClaims.
	shutit_session.send('kubectl apply -f kubernetes/ceph/storageclass-bucket-delete.yaml')
	shutit_session.send('kubectl create -f kubernetes/ceph/object-bucket-claim-delete.yaml')
	# TODO: https://rook.io/docs/rook/v1.7/ceph-object.html#consume-the-object-storage
	# Doesn't work?
	#port = shutit_session.send_and_get_output("kubectl -n rook-ceph get svc rook-ceph-rgw-my-store -o json | jq '.spec.ports[0].port'")
	#ip = shutit_session.send_and_get_output("""kubectl -n rook-ceph get svc rook-ceph-rgw-my-store -o json | jq '.spec.clusterIP' | sed 's/"//g'""")
	#shutit_session.send("export AWS_HOST=$(kubectl -n default get cm ceph-delete-bucket -o jsonpath='{.data.BUCKET_HOST}')")
	#shutit_session.send("export AWS_ACCESS_KEY_ID=$(kubectl -n default get secret ceph-delete-bucket -o jsonpath='{.data.AWS_ACCESS_KEY_ID}' | base64 --decode)")
	#shutit_session.send("export AWS_SECRET_ACCESS_KEY=$(kubectl -n default get secret ceph-delete-bucket -o jsonpath='{.data.AWS_SECRET_ACCESS_KEY}' | base64 --decode)")
	## Endpoint: The endpoint where the rgw service is listening. Run kubectl -n rook-ceph get svc rook-ceph-rgw-my-store, then combine the clusterIP and the port.
	#shutit_session.send("export AWS_ENDPOINT=" + ip + ":" + port)
	#shutit_session.login(command='kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- bash')
	#shutit_session.send('yum -y install s3cmd')
	#shutit_session.send('echo "Hello Rook" > /tmp/rookObj')
	#shutit_session.send('s3cmd put /tmp/rookObj --no-ssl --host=${AWS_HOST} --host-bucket= s3://rookbucket')
	#shutit_session.send('s3cmd get s3://rookbucket/rookObj /tmp/rookObj-download --no-ssl --host=${AWS_HOST} --host-bucket=')
	#shutit_session.send('cat /tmp/rookObj-download')
	#shutit_session.logout()

	# Shared filesystem: https://rook.io/docs/rook/v1.7/ceph-filesystem.html
	# Create the filesystem by specifying the desired settings for the metadata pool, data pools, and metadata server in the CephFilesystem CRD. In this example we create the metadata pool with replication of three and a single data pool with replication of three. For more options, see the documentation on creating shared filesystems.
	shutit_session.send('kubectl create -f kubernetes/ceph/filesystem.yaml')
	shutit_session.send_until('kubectl -n rook-ceph rollout status deploy/rook-ceph-mds-myfs-a | grep successfully.rolled.out | wc -l', '1')
	shutit_session.send_until('kubectl -n rook-ceph rollout status deploy/rook-ceph-mds-myfs-b | grep successfully.rolled.out | wc -l', '1')
	# Before Rook can start provisioning storage, a StorageClass needs to be created based on the filesystem. This is needed for Kubernetes to interoperate with the CSI driver to create persistent volumes.
	shutit_session.send('kubectl create -f kubernetes/ceph/csi/cephfs/storageclass.yaml')
	# As an example, we will start the kube-registry pod with the shared filesystem as the backing store.
	# If you’ve deployed the Rook operator in a namespace other than 'rook-ceph' as is common change the prefix in the provisioner to match the namespace you used. For example, if the Rook operator is running in 'rook-op' the provisioner value should be “rook-op.rbd.csi.ceph.com”.
	shutit_session.send('kubectl create -f kubernetes/ceph/csi/cephfs/kube-registry.yaml')
	shutit_session.pause_point('ROOK END')
