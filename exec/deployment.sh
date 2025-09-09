# helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update

#minikube
open -a Docker
sleep 15
minikube delete || true
minikube start --memory=7837 --cpus=2
eval $(minikube -p minikube docker-env)

# Prometheus and Grafana
echo "prometheus and grafana"
helm install prometheus prometheus-community/kube-prometheus-stack \
    --set grafana.service.type=NodePort \
    --set grafana.adminUser=admin \
    --set grafana.adminPassword=admin \
    --set grafana.fullnameOverride=grafana \
    --wait

# jaeger
echo "jaeger"
helm install jaeger jaegertracing/jaeger \
    --set allInOne.enabled=true \
    --set agent.enabled=false \
    --set collector.enabled=false \
    --set query.enabled=false \
    --set provisionDataStore.cassandra=false \
    --set storage.type=memory \
    --wait

#external services
cd services/external-services
./kafka-helm.sh
./rabbitmq-helm.sh

# billing-service
echo "billing-service"
cd ../billing-service
kubectl apply -f mongodb-manifest.yaml
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# car-statistics
echo "car-statistics"
cd ../car-statistics
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# inventory-service
echo "inventory-service"
cd ../inventory-service
./mysql-helm.sh
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# rental-service
echo "rental-service"
cd ../rental-service
kubectl apply -f mongodb-manifest.yaml
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# reservation-service
echo "reservation-service"
cd ../reservation-service
./postgresql-helm.sh
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# users-service
echo "users-service"
cd ../users-service
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# complete
sleep 120
kubectl get pods
cd ..