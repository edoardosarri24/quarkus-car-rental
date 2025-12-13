helm install postgresql-reservation bitnami/postgresql \
  --set auth.username=user \
  --set auth.password=pass \
  --set auth.database=reservation