package main.java.org.acme.startparallel;

import com.google.protobuf.Empty;
import io.quarkus.grpc.GrpcClient;
import io.smallrye.mutiny.Uni;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import org.acme.firstparallel.grpc.FirstParallelService;
import org.acme.secondparallel.grpc.SecondParallelService;

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
        Uni<Empty> firstCall = firstParallel.pass(EMPTY);
        Uni<Empty> secondCall = secondParallel.pass(EMPTY);
        Uni.combine().all()
            .unis(firstCall, secondCall)
            .asTuple()
            .await().atMost(Duration.ofSeconds(5));
    }

}
