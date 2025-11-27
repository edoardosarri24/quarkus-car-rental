# Quarkus Car Rental
This project presents a Quarkus-based car rental application with a microservices architecture. A key focus is the E2E performance analysis of the reservation workflow to ensure service level agreements. This is achieved using a data-driven approach, where system traces are collected (with Open-Telemetry) and analyzed to model the CDF/PDF of the response time distribution.

### My documentation
The report of the whole project is in [report.pdf](https://github.com/edoardosarri24/quarkus-car-rental/report.pdf) file. The slides is in [slides.pdf](https://github.com/edoardosarri24/quarkus-car-rental/slides.pdf) file.

### Requirements
To get started with this project, you will need to have the following installed:
- Java 21
- Java 24
- Maven
- Docker, Minikube, kubectl
- Quarkus CLI
- [Eulero](https://github.com/oris-tool/eulero_2.0)
- Conda
- [UV](https://docs.astral.sh/uv/) Python package manager.

### Structure
Above the strucure of the main directories of the project.
```
quarkus-car-rental
├── E2E-analysis - An analysis of E2E execution time distribution.
├── README.md
├── exec - the script for the main operation.
    ├── app-UI.sh - show the UI of the application.
    ├── data_analysis.sh - Extract stastics from the traces.
    ├── deployment.sh - Application deployment on Minikube. Require docker engine running.
    ├── eulero_analysis.sh - Compute the CDF/PDF of the E2E execution time.
    ├── grafana-UI.sh show the UI of the Grafana.
    ├── jaeger-UI.sh - show the UI of the Jaeger.
    └── k6.sh - execute the k6 load generator.
├── report - the latex report directory.
├── report.pdf - the report file.
├── services - the application microservices and the utility services (e.g., k6, OTel-collector, ...).
├── slides - the latex slides directory.
└── slides.pdf - the slides file.
```