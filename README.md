# Quarkus Car Rental
This project is based on a car rental system that starts from the one released with the book [Quarkus in Action](https://github.com/xstefank/quarkus-in-action). The goal is focus on the Kubernetes technologies and Quarkus framework.

### My documentation
The report of the whole project is in [report.pdf](https://github.com/edoardosarri24/quarkus-car-rental/report.pdf) file. The slides of the application part is in [slides.pdf](https://github.com/edoardosarri24/quarkus-car-rental/slides.pdf) file.

### Requirements
To get started with this project, you will need to have the following installed:
- Java 21
- Maven
- Docker, Minikube, kubectl
- Quarkus CLI

### Running
To deployment the whole application, execute the command below from the root directory whit Docker demon running:
```sh
./exec/deployment.sh
```

To visualize the app UI executes the following command from the root directory:
```sh
./exec/app-UI.sh
```

To start Jaeger Tracing UI executes che command below from the root directory:
```sh
./exec/jaeger-UI.sh
```

To start Grafana UI executes che command below from the root directory:
```sh
./exec/grafana-UI.sh
```

### Technologies studired
The technologies used are:
- [Kafka](https://kafka.apache.org/), [RabbitMQ](https://www.rabbitmq.com/)
- [gRPC](https://grpc.io/), [GraphQL](https://graphql.org/)
- [MongoDB](https://www.mongodb.com/), [MySQL](https://www.mysql.com/), [PostgreSQL](https://www.postgresql.org/)
- [OpenTelemetry](https://opentelemetry.io), [Jaeger](https://www.jaegertracing.io)