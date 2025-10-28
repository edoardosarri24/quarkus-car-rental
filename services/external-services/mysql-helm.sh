helm install mysql-inventory bitnami/mysql \
    --set image.repository=bitnamilegacy/mysql \
    --set auth.rootPassword=root-pass \
    --set auth.database=mysql-inventory \
    --set auth.username=user \
    --set auth.password=pass