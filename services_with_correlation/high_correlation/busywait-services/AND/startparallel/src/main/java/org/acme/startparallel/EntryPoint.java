package org.acme.startparallel;

import com.google.protobuf.Empty;
import io.quarkus.grpc.GrpcClient;
import io.smallrye.mutiny.Uni;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import org.acme.firstparallel.grpc.FirstParallelService;
import org.acme.secondparallel.grpc.SecondParallelService;
import org.oristool.simulator.samplers.*;

import java.math.BigDecimal;
import java.time.Duration;

@Path("/startParallel")
@Produces(MediaType.APPLICATION_JSON)
public class EntryPoint {

    private static final Empty EMPTY = Empty.newBuilder().build();

    @GrpcClient("first-parallel")
    FirstParallelService firstParallel;

    @GrpcClient("second-parallel")
    SecondParallelService secondParallel;

    @POST
    public void pass() {
        BigDecimal busyWaitTime = new ExponentialSampler(new BigDecimal(1).divide(new BigDecimal(5), java.math.MathContext.DECIMAL128)).getSample();
        long busyWaitTimeNs = (long) (busyWaitTime.doubleValue() * 1.0E+6);
        long startTime = System.nanoTime();
        while (System.nanoTime() - startTime < busyWaitTimeNs) {
            // Busy wait
        }
        Uni<org.acme.firstparallel.grpc.PassResponse> firstCall = firstParallel.pass(EMPTY);
        Uni<org.acme.secondparallel.grpc.PassResponse> secondCall = secondParallel.pass(EMPTY);
        var result = Uni.combine().all()
            .unis(firstCall, secondCall)
            .asTuple()
            .await().atMost(Duration.ofSeconds(5));
        double busyWait = result.getItem1().getBusywaitTime() + result.getItem2().getBusywaitTime();
        long busyWaitNs = (long) (busyWait * 1.0E+6);
        long start = System.nanoTime();
        while (System.nanoTime() - start < busyWaitNs) {
            // Busy wait
        }
        return;
    }

}
