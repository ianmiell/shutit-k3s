def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	## Install shell operator - imiell/monitor-pods created separately based on README: https://github.com/flant/shell-operator
	## Script is:
	##!/usr/bin/env bash
	#
	#if [[ $1 == "--config" ]] ; then
	#  cat <<EOF
	#configVersion: v1
	#kubernetes:
	#- apiVersion: v1
	#  kind: Pod
	#  executeHookOnEvent: ["Added"]
	#EOF
	#else
	#  podName=$(jq -r .[0].object.metadata.name $BINDING_CONTEXT_PATH)
	#  echo "Pod '${podName}' added"
	#fi
	#
	## And the dockerfile is:
	# FROM flant/shell-operator:latest
	# ADD pods-hook.sh /hooks
	#
	# Shell operator docs:
	# https://github.com/flant/shell-operator/blob/master/RUNNING.md        - env vars and flags
	# https://github.com/flant/shell-operator/blob/master/HOOKS.md          - how it works
	# https://github.com/flant/shell-operator/blob/master/HOOKS.md#syntax-1 - syntax
	shutit_session.send('''cat > shell-operator-pod.yaml << EOF
apiVersion: v1
kind: Pod
metadata:
  name: shell-operator
spec:
  containers:
  - name: shell-operator
    image: imiell/monitor-pods
    imagePullPolicy: Always
  serviceAccountName: monitor-pods-acc
EOF''')
	shutit_session.send('kubectl create namespace example-monitor-pods')
	shutit_session.send('kubectl create serviceaccount monitor-pods-acc --namespace example-monitor-pods')
	shutit_session.send('kubectl create clusterrole monitor-pods --verb=get,watch,list --resource=pods')
	shutit_session.send('kubectl create clusterrolebinding monitor-pods --clusterrole=monitor-pods --serviceaccount=example-monitor-pods:monitor-pods-acc')
	shutit_session.send('kubectl -n example-monitor-pods apply -f shell-operator-pod.yaml')
	# Trigger the operator:
	shutit_session.send('kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/aio/deploy/recommended.yaml')
	# Now run kubectl -n example-monitor-pods logs po/shell-operator and observe that the hook will print dashboard pod name:
	shutit_session.send('sleep 10 && kubectl -n example-monitor-pods logs po/shell-operator')
