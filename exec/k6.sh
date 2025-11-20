kubectl delete job k6-reserve --ignore-not-found=true
helm upgrade --install k6-reserve services/external-services/k6