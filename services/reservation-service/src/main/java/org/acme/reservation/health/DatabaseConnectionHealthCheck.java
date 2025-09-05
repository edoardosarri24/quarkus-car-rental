package org.acme.reservation.health;

import io.agroal.api.AgroalDataSource;
import org.eclipse.microprofile.health.HealthCheck;
import org.eclipse.microprofile.health.HealthCheckResponse;
import org.eclipse.microprofile.health.Startup;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;

@Startup
@ApplicationScoped
public class DatabaseConnectionHealthCheck implements HealthCheck {

    @Inject
    AgroalDataSource defaultDataSource;

    @Override
    public HealthCheckResponse call() {
        System.out.println("check");
        try (Connection connection = defaultDataSource.getConnection();
                Statement statement = connection.createStatement()) {
            statement.execute("SELECT 1");
            return HealthCheckResponse.up("Database connection health check");
        } catch (SQLException e) {
            return HealthCheckResponse.named("Database connection health check")
                    .down()
                    .withData("exception", e.getMessage())
                    .build();
        }
    }
}