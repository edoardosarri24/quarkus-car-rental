il progetto è un insieme di micro servizi, che realizzano un sistema per il noleggio delle auto.

# struttura
la root directory è strutturata in sotto cartelle. ogni sotto cartella è un micro servizio.

# framework
- ogni microservizio è sviluppando utilizzando Quarkus come framwork.
- usiamo docker come runner di container e kubernetes come orchestatore. solo questi due.

# comandi
quando devi eseguire dei comandi (e.g., building, test) utilizza il Quarkus CLI invece di quelli maven.