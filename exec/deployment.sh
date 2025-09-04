# helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

#minikube
minikube delete || true
minikube start --memory=7837 --cpus=2
eval $(minikube -p minikube docker-env)
cd services

#external services
cd external-services
./kafka-helm.sh
./rabbitmq-helm.sh
cd ..

# billing-service
echo "billing-service"
cd billing-service
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
sleep 30
kubectl get pods
cd ..