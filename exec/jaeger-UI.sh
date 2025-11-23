#!/bin/sh

kubectl port-forward svc/jaeger-query 16686:16686 &
open http://localhost:16686