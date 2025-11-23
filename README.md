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

### Structure
Above the strucure of the main directories of the project.
```
quarkus-car-rental
├── E2E-analysis - An analysis of E2E execution time distribution.
├── README.md
├── exec - the script for the main operation.
├── report - the latex report directory.
├── report.pdf - the report file.
├── services - the application microservices and the utility services (e.g., k6, OTel-collector, ...).
├── slides - the latex slides directory.
└── slides.pdf - the slides file.
```