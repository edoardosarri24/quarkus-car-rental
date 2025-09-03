# Add Jaeger Helm repository
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update

# Install Jaeger
helm uninstall jaeger > /dev/null 2>&1 || true
helm install jaeger jaegertracing/jaeger \
    --set allInOne.enabled=true \
    --set agent.enabled=false \
    --set collector.enabled=false \
    --set query.enabled=false \
    --set provisionDataStore.cassandra=false \
    --set storage.type=memory

# port forward
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/instance=jaeger --timeout=120s
kubectl port-forward svc/jaeger-query 16686:16686 &
open http://localhost:16686