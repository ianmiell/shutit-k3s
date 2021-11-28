def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# Set up rook https://rook.io/docs/rook/v1.7/quickstart.html
#   23  git clone --single-branch --branch v1.7.8 https://github.com/rook/rook.git
#   24  cd rook/cluster/examples/kubernetes/ceph
#   25  kubectl create -f crds.yaml -f common.yaml -f operator.yaml
#   26  kubectl create -f cluster.yaml
#	# Create the toolbox
#	shutit_session.send('''kubectl create -f <(cat << EOF
#apiVersion: apps/v1
#kind: Deployment
#metadata:
#  name: rook-ceph-tools
#  namespace: rook-ceph
#  labels:
#    app: rook-ceph-tools
#spec:
#  replicas: 1
#  selector:
#    matchLabels:
#      app: rook-ceph-tools
#  template:
#    metadata:
#      labels:
#        app: rook-ceph-tools
#    spec:
#      dnsPolicy: ClusterFirstWithHostNet
#      containers:
#      - name: rook-ceph-tools
#        image: rook/ceph:v1.7.8
#        command: ["/tini"]
#        args: ["-g", "--", "/usr/local/bin/toolbox.sh"]
#        imagePullPolicy: IfNotPresent
#        env:
#          - name: ROOK_CEPH_USERNAME
#            valueFrom:
#              secretKeyRef:
#                name: rook-ceph-mon
#                key: ceph-username
#          - name: ROOK_CEPH_SECRET
#            valueFrom:
#              secretKeyRef:
#                name: rook-ceph-mon
#                key: ceph-secret
#        volumeMounts:
#          - mountPath: /etc/ceph
#            name: ceph-config
#          - name: mon-endpoint-volume
#            mountPath: /etc/rook
#      volumes:
#        - name: mon-endpoint-volume
#          configMap:
#            name: rook-ceph-mon-endpoints
#            items:
#            - key: data
#              path: mon-endpoints
#        - name: ceph-config
#          emptyDir: {}
#      tolerations:
#        - key: "node.kubernetes.io/unreachable"
#          operator: "Exists"
#          effect: "NoExecute"
#          tolerationSeconds: 5
#EOF
#)'''
#kubectl -n rook-ceph rollout status deploy/rook-ceph-tools | grep successfully.rolled.out | wc -l
#
#kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- bash
#wait a long time
	shutit_session.pause_point('ROOK END')
