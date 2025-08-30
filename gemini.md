il progetto è un insieme di micro servizi, che realizzano un sistema per il noleggio delle auto.

# struttura
la root directory è strutturata in sotto cartelle. ogni sotto cartella è un micro servizio.

# framework
- ogni microservizio è sviluppando utilizzando Quarkus come framework.
- usiamo docker come runner di container.
- usiamo kubernetes come orchestatore.

# comandi
quando devi eseguire dei comandi (e.g., building, test) utilizza il Quarkus CLI e non quelli maven.