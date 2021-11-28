def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# Set up kube-monkey
	shutit_session.send('helm repo add kubemonkey https://asobti.github.io/kube-monkey/charts/repo && helm repo update')
	shutit_session.send('helm install my-release kubemonkey/kube-monkey --version 1.4.0')
	shutit_session.send(r'''kubectl apply -f <(cat << EOF
apiVersion: v1
data:
  config.toml: "[kubemonkey]\ndry_run = false\nrun_hour = 8 \nstart_hour = 10\nend_hour
    = 23\nblacklisted_namespaces = [ \"kube-system\", ]\nwhitelisted_namespaces =
    [ \"argo\" ]\ntime_zone = \"Europe/London\"\n[debug]\nenabled= true\nschedule_immediate_kill=true\n"
kind: ConfigMap
metadata:
  name: my-release-kube-monkey
  namespace: default
EOF
)''')
	shutit_session.send('helm repo add bitnami https://charts.bitnami.com/bitnami')
	shutit_session.send('kubectl create ns argo')
	shutit_session.send('helm install my-argo-cd bitnami/argo-cd --version 2.0.12 --namespace argo')
	shutit_session.send('''kubectl apply -f <(cat << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    kube-monkey/enabled: enabled
    kube-monkey/identifier: monkey-victim
    kube-monkey/kill-mode: fixed
    kube-monkey/kill-value: "1"
    kube-monkey/mtbf: "2"
  name: my-argo-cd-server
  namespace: argo
EOF
)''')
	shutit_session.send('kubectl rollout restart deployment my-release-kube-monkey')
	shutit_session.pause_point('END')
