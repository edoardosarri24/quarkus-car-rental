helm install rabbitmq-reservation oci://registry-1.docker.io/bitnamicharts/rabbitmq \
    --set auth.username=user \
    --set auth.password=pass \
    --set image.repository=bitnamilegacy/rabbitmq \
    --set image.tag=4.1.3-debian-12-r1 \
    --set global.security.allowInsecureImages=true