# helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update

#minikube
minikube delete || true
minikube start --memory=7837 --cpus=2
eval $(minikube -p minikube docker-env)

# Prometheus and Grafana
echo "--- PROMETHEUS AND GRAFANA ---"
helm install prometheus prometheus-community/kube-prometheus-stack \
    --set grafana.service.type=NodePort \
    --set grafana.adminUser=admin \
    --set grafana.adminPassword=admin \
    --set grafana.fullnameOverride=grafana \
    --wait

# jaeger
echo "--- JAEGER ---"
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
./mysql-helm.sh

# billing-service
echo "--- BILLING SERVICE ---"
cd ../billing-service
kubectl apply -f mongodb-manifest.yaml
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# car-statistics
echo "--- CAR STATISTICS ---"
cd ../car-statistics
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# inventory-service
echo "--- INVENTORY SERVICE ---"
cd ../inventory-service
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# rental-service
echo "--- RENTAL SERVICE ---"
cd ../rental-service
kubectl apply -f mongodb-manifest.yaml
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# reservation-service
echo "--- RESERVATION SERVICE ---"
cd ../reservation-service
./postgresql-helm.sh
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# users-service
echo "--- USERS SERVICE ---"
cd ../users-service
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# workflow services
echo "--- WORKFLOW SERVICES ---"
cd ../busywait-services/XOR
cd start-choice
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml
cd ../first-choice
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml
cd ../second-choice
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml
cd ../third-choice
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml
cd ../../AND/start-parallel
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml
cd ../first-parallel
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml
cd ../second-parallel
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml
cd ../../..

# complete
sleep 120
kubectl get pods
cd ..