# Quarkus Car Rental
This project is a car rental system built with a microservices architecture using Quarkus and based on the one released with the book [Quarkus in Action](https://github.com/xstefank/quarkus-in-action).

### Requirements
To get started with this project, you will need to have the following installed:
- Java 21
- Maven
- Docker
- Minikube
- Kubectl
- Quarkus CLI

### Getting Started
For deplyment the whole application, execute the command below from the root directory:
```bash
./deployment.sh
```

### Microservices
The project is composed of the following microservices:
- billing-service: Handles billing and payments. It uses Kafka, RabbitMQ, and MongoDB.
- car-statistics: Provides statistics about the cars. It uses Funqy and a GraphQL client.
- inventory-service: Manages the car inventory. It uses gRPC, Hibernate, MySQL, and GraphQL.
- rental-service: Handles the car rental process. It uses Kafka, MongoDB, and a REST client.
- reservation-service: Manages reservations. It uses RabbitMQ, Hibernate Reactive with PostgreSQL, and a GraphQL client.
- users-service: Manages user accounts. It uses Qute for templating and a REST client.


### Technologies
The technologie used are:
- [Kafka](https://kafka.apache.org/)
- [RabbitMQ](https://www.rabbitmq.com/)
- [MongoDB](https://www.mongodb.com/)
- [MySQL](https://www.mysql.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [GraphQL](https://graphql.org/)
- [gRPC](https://grpc.io/)