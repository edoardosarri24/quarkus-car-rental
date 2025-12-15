helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
    --set grafana.service.type=NodePort \
    --set grafana.adminUser=admin \
    --set grafana.adminPassword=admin \
    --set grafana.fullnameOverride=grafana \
    --wait