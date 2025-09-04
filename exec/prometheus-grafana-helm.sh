# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus and Grafana
helm uninstall prometheus > /dev/null 2>&1 || true
helm install prometheus prometheus-community/kube-prometheus-stack \
    --set grafana.service.type=NodePort \
    --set grafana.adminUser=admin \
    --set grafana.adminPassword=admin \
    --wait

# Start Grafana UI
minikube service prometheus-grafana