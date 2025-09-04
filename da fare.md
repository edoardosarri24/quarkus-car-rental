# da fare
- prometheus
- grafana
- studiare istio
- qaurkus nella doc

- mettere un successo per 3 volte in res?
# prom
Tuttavia, c'è un ultimo passo fondamentale. L'installazione di default non sa che deve monitorare i tuoi microservizi. Dobbiamo creare un "ponte" tra Prometheus e i tuoi servizi.

  In Kubernetes, questo ponte si chiama ServiceMonitor. È una risorsa che dice a Prometheus: "Ehi, vai a raccogliere le metriche da questo servizio".


  La buona notizia è che Quarkus può creare questo ServiceMonitor per noi. Dobbiamo solo aggiungere una configurazione specifica nel file application.properties di ogni servizio che vogliamo monitorare.

  Aggiungiamo la configurazione per `users-service`


  Dobbiamo aggiungere una label al ServiceMonitor generato da Quarkus, in modo che il nostro Prometheus (installato con il nome prometheus) lo riconosca. La configurazione da aggiungere è:
  quarkus.kubernetes.labels."release"="prometheus"


  Procedo a leggere il file application.properties di users-service per poi aggiungere questa riga.
 ╭────────────────────────────────────────────────────────╮
 │ ✔  ReadFile ...vices/resources/application.properties  │
 ╰────────────────────────────────────────────────────────╯
✦ Ho trovato un'impostazione importante nel file.

  La riga:
  quarkus.kubernetes.prometheus.generate-service-monitor=false

  sta esplicitamente dicendo a Quarkus di non creare il ServiceMonitor di cui abbiamo bisogno.


  Modifico il file per:
   1. Cambiare quella riga in true.
   2. Aggiungere la label release: prometheus che serve a Prometheus per trovare il servizio.