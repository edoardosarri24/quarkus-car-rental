#!/bin/bash
helm install keycloak bitnami/keycloak \
  --set auth.adminUser=admin \
  --set auth.adminPassword=admin \
  --set service.type=NodePort