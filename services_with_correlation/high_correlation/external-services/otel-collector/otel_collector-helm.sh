helm upgrade --install otel-collector open-telemetry/opentelemetry-collector \
  --values otel-collector/values.yaml \
  --wait