# helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update

#minikube
minikube delete || true
minikube start --memory=7837 --cpus=2
eval $(minikube -p minikube docker-env)

#external services
cd services/external-services
echo "------------ EXTERNAL SERVICES ------------"
./kafka-helm.sh
./rabbitmq-helm.sh
./mysql-helm.sh
./prometheus_grafana-helm.sh
./jaeger-helm.sh
./otel_collector-helm.sh
cd ../..

# billing-service
echo "------------ BILLING SERVICE ------------"
cd services/billing-service
kubectl apply -f mongodb-manifest.yaml
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# car-statistics
echo "------------ CAR STATISTICS ------------"
cd ../car-statistics
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# inventory-service
echo "------------ INVENTORY SERVICE ------------"
cd ../inventory-service
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# rental-service
echo "------------ RENTAL SERVICE ------------"
cd ../rental-service
kubectl apply -f mongodb-manifest.yaml
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# reservation-service
echo "------------ RESERVATION SERVICE ------------"
cd ../reservation-service
./postgresql-helm.sh
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# users-service
echo "------------ USERS SERVICE ------------"
cd ../users-service
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml

# xor services
echo "------------ XOR SERVICES ------------"
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

# and services
echo "------------ AND SERVICES ------------"
cd ../../AND/startparallel
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml
cd ../firstparallel
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml
cd ../secondparallel
quarkus build
kubectl apply -f target/kubernetes/kubernetes.yml
cd ../../..

# complete
kubectl get pods
cd ..