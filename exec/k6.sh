kubectl delete job k6-job --ignore-not-found=true
helm upgrade --install k6 services/external-services/k6