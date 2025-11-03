package main.java.org.acme.firstparallel;

import java.math.BigDecimal;

import org.acme.firstparallel.grpc.FirstParallelService;
import org.oristool.simulator.samplers.*;
import com.google.protobuf.Empty;

import io.quarkus.grpc.GrpcService;
import io.smallrye.mutiny.Uni;

@GrpcService
public class EntryPoint implements FirstParallelService {

    @Override
    public Uni<Empty> pass(Empty request) {
        System.out.println("first-parallel executed");
        BigDecimal busywaitTime = new ExponentialSampler(new BigDecimal(1)).getSample();
        long startTime = System.currentTimeMillis();
        while (System.currentTimeMillis() - startTime < busywaitTime.doubleValue()) {
            // Busy wait
        }
        return Uni.createFrom().item(com.google.protobuf.Empty.getDefaultInstance());
    }

}