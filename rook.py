def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# Set up rook https://rook.io/docs/rook/v1.7/quickstart.html
	shutit_session.send('git clone --single-branch --branch v1.7.8 https://github.com/rook/rook.git')
	shutit_session.send('cd rook/cluster/examples/kubernetes/ceph')
	shutit_session.send('kubectl create -f crds.yaml -f common.yaml -f operator.yaml')
	shutit_session.send('kubectl create -f cluster.yaml')
	# Override security problem
	shutit_session.send('''kubectl apply -f <(cat << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: rook-config-override
  namespace: rook-ceph
data:
  config: |
    [mon]
    mon_warn_on_insecure_global_id_reclaim_allowed = false
EOF
)''')
	shutit_session.send_until("kubectl get cephcluster -n rook-ceph -o json | jq '.items[0].status.phase' | wc -l", '"Ready"', cadence=30)
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
)''')
	shutit_session.send_until('kubectl -n rook-ceph rollout status deploy/rook-ceph-tools | grep successfully.rolled.out | wc -l', '1')
	shutit_session.login(command='kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- bash')
	shutit_session.send('ceph status')
	shutit_session.logout()
	shutit_session.send('kubectl get cephcluster -A')
	shutit_session.pause_point('ROOK END')
