#!/bin/sh

kubectl delete job k6-reserve --ignore-not-found=true
helm upgrade --install k6-reserve services_with_correlation/high_correlation/external-services/k6