def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	shutit_session.send('export RELEASE=v0.35.0')
	shutit_session.send('kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/${RELEASE}/kubevirt-operator.yaml   # Deploy the KubeVirt operator')
	shutit_session.send('kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/${RELEASE}/kubevirt-cr.yaml # Create the KubeVirt CR (instance deployment request) which triggers the actual installation')
	shutit_session.send('kubectl -n kubevirt wait kv kubevirt --for condition=Available  # wait until all KubeVirt components are up')
	shutit_session.send('kubectl krew install virt')
	shutit_session.send('''kubectl create -f <(cat << EOF
apiVersion: kubevirt.io/v1alpha3
kind: VirtualMachineInstance
metadata:
  name: testvmi-nocloud
spec:
  terminationGracePeriodSeconds: 30
  domain:
    resources:
      requests:
        memory: 1024M
    devices:
      disks:
      - name: containerdisk
        disk:
          bus: virtio
      - name: emptydisk
        disk:
          bus: virtio
      - disk:
          bus: virtio
        name: cloudinitdisk
  volumes:
  - name: containerdisk
    containerDisk:
      image: kubevirt/fedora-cloud-container-disk-demo:latest
  - name: emptydisk
    emptyDisk:
      capacity: "2Gi"
  - name: cloudinitdisk
    cloudInitNoCloud:
      userData: |-
        #cloud-config
        password: fedora
        chpasswd: { expire: False }
EOF
)''')

