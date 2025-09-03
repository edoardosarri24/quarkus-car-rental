- devo desrivere all'interno della relazione (e poi della presentazione kubernetes, minikube e quarkus)?

- istio
    Usa sidecar.
    - tracing di rete
      - cascate di chiamate
      - latenza di una chiamata
      - throughtput
    - routing avanzato
    - sicurezza
    - non metriche custum
    - senza prometheus si perde
      - salvare metriche numeriche storiche
      - visualizzare
      - allert automatici
- jaeger
  - per visualizzare metriche.
  - nel mio progetto raccolte da opentelemetry senza collector

- domanda: ci servono le metriche custum? potremmo raccogliere solo metriche di rete con istio e lasciar stare quelle di micro meter (opentelemetry per le metriche custum non è stabile)?