package org.acme.reservation.rest;

import io.quarkus.hibernate.reactive.panache.common.WithTransaction;
import io.quarkus.logging.Log;
import io.smallrye.graphql.client.GraphQLClient;
import io.smallrye.mutiny.Uni;
import io.smallrye.reactive.messaging.MutinyEmitter;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import org.acme.reservation.billing.Invoice;
import org.acme.reservation.entity.Reservation;
import org.acme.reservation.inventory.Car;
import org.acme.reservation.inventory.GraphQLInventoryClient;
import org.acme.reservation.inventory.InventoryClient;
import org.acme.reservation.rental.RentalClient;
import org.eclipse.microprofile.faulttolerance.Fallback;
import org.eclipse.microprofile.faulttolerance.Retry;
import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.jboss.resteasy.reactive.RestQuery;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


@Path("reservation")
@Produces(MediaType.APPLICATION_JSON)
public class ReservationResource {

    public static final double STANDARD_RATE_PER_DAY = 19.99;

    private final InventoryClient inventoryClient;
    private final RentalClient rentalClient;

    @Inject
    @Channel("invoices")
    MutinyEmitter<Invoice> invoiceEmitter;

    public ReservationResource(@GraphQLClient("inventory") GraphQLInventoryClient inventoryClient,
                                @RestClient RentalClient rentalClient) {
        this.inventoryClient = inventoryClient;
        this.rentalClient = rentalClient;
    }

    @Consumes(MediaType.APPLICATION_JSON)
    @POST
    @WithTransaction
    public Uni<Reservation> make(Reservation reservation) {
        reservation.userId = "guest";
        return reservation.<Reservation>persist().onItem()
            .call(persistedReservation -> {
                Log.info("Successfully reserved reservation "
                    + persistedReservation);

                Uni<Void> invoiceUni = invoiceEmitter.send(
                    new Invoice(reservation, computePrice(reservation)))
                    .onFailure().invoke(throwable ->
                        Log.errorf("Couldn't create invoice for %s. %s%n",
                        persistedReservation, throwable.getMessage()));

                if (persistedReservation.startDay.equals(LocalDate.now())) {
                    return invoiceUni.chain(() ->
                        rentalClient.start(persistedReservation.userId,
                            persistedReservation.id)
                        .onItem().invoke(rental ->
                            Log.info("Successfully started rental " + rental))
                        .replaceWith(persistedReservation));
                }
                return invoiceUni
                    .replaceWith(persistedReservation);
            });
    }

    private double computePrice(Reservation reservation) {
        return (ChronoUnit.DAYS.between(reservation.startDay,
            reservation.endDay) + 1) * STANDARD_RATE_PER_DAY;
    }

    @Retry(maxRetries = 25, delay = 1000)
    @Fallback(fallbackMethod = "availabilityFallback")
    @GET
    @Path("availability")
    public Uni<Collection<Car>> availability(@RestQuery LocalDate startDate,
                                            @RestQuery LocalDate endDate) {
        Log.info("Entering availability method with startDate: " + startDate + ", endDate: " + endDate);
        // obtain all cars from inventory
        Uni<List<Car>> availableCarsUni = inventoryClient.allCars();
        // get all current reservations
        Uni<List<Reservation>> reservationsUni = Reservation.listAll();

        return Uni.combine().all().unis(availableCarsUni, reservationsUni).with((availableCars, reservations) -> {
            Log.info("Received " + availableCars.size() + " cars from inventory service.");
            // create a map from id to car
            Map<Long, Car> carsById = new HashMap<>();
            for (Car car : availableCars) {
                carsById.put(car.id, car);
            }

            // for each reservation, remove the car from the map
            for (Reservation reservation : reservations) {
                if (reservation.isReserved(startDate, endDate)) {
                    carsById.remove(reservation.carId);
                }
            }
            Log.info("Returning " + carsById.values().size() + " available cars after filtering reservations.");
            return carsById.values();
        });
    }

    public Uni<Collection<Car>> availabilityFallback(LocalDate startDate,
                                                    LocalDate endDate) {
        return Uni.createFrom().item(List.of());
    }

    @GET
    @Path("all")
    public Uni<List<Reservation>> allReservations() {
        return Reservation.<Reservation>listAll();
    }
}