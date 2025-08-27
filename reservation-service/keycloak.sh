#!/bin/bash
helm install keycloak-reservation bitnami/keycloak \
  --set auth.adminUser=admin \
  --set auth.adminPassword=admin \
  --set service.type=NodePort