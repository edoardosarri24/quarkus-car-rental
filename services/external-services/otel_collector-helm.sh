helm upgrade --install otel-collector open-telemetry/opentelemetry-collector \
  --values yaml/otel-collector-values.yaml \
  --wait