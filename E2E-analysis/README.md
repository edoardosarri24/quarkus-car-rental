# E2E-analysis
In questo folder ci sono gli strumenti per estrarre i dati e visualizzare i risultati relativi all'analisi del tempo di esecuzione E2E.

### requirements
- [uv](https://docs.astral.sh/uv/)

### pipeline
- la cartella [input\_file](/Users/edoardosarri/Documents/quarkus-car-rental/E2E-analysis/extract_data/input_file) deve contenere il file traces.json.
- Dalla root directory del progetto eseguire [extract_data.sh](/Users/edoardosarri/Documents/quarkus-car-rental/exec/extract_data.sh).
- Spostare il file generato [real_e2e_execution_time.csv](/Users/edoardosarri/Documents/quarkus-car-rental/E2E-analysis/extract_data/results/real_e2e_execution_time.csv) nella cartella di [input](/Users/edoardosarri/Documents/quarkus-car-rental/E2E-analysis/visualize_data/E2E/input_file) della visualizzazione.
- Usare il file [trace_analysis_stats.json](/Users/edoardosarri/Documents/quarkus-car-rental/E2E-analysis/extract_data/results/trace_analysis_stats.json) per generare il [main](/Users/edoardosarri/Documents/quarkus-car-rental/E2E-analysis/eulero/src/main/java/org/oristool/eulero/main.java) di Eulero.
- Dalla root directory del progetto eseguire [eurlero\_analysis.sh](/Users/edoardosarri/Documents/quarkus-car-rental/exec/eulero_analysis.sh).
- Spostare il file generato [eulero_CSV.csv](/Users/edoardosarri/Documents/quarkus-car-rental/E2E-analysis/visualize_data/E2E/input_file/eulero_CDF.csv) nella cartella di [input](/Users/edoardosarri/Documents/quarkus-car-rental/E2E-analysis/visualize_data/E2E/input_file) della visualizzazione.
- Dalla root directory del progetto eseguire [visualize_data.sh](/Users/edoardosarri/Documents/quarkus-car-rental/exec/visualize_data.sh).
- Il plot sarà chiamato compare\_e2e\_distribution.pdf e si troverà nella cartella [results](/Users/edoardosarri/Documents/quarkus-car-rental/E2E-analysis/visualize_data/E2E/results).