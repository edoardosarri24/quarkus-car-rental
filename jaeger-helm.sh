#!/bin/bash

# Add Jaeger Helm repository
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update

# Install Jaeger
helm install jaeger jaegertracing/jaeger \
    --set provisionDataStore.cassandra=false \
    --set allInOne.enabled=true \
    --set storage.type=memory \
    --set query.service.type=NodePort