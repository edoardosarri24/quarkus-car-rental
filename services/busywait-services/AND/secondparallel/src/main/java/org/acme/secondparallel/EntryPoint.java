package org.acme.secondparallel;

import java.math.BigDecimal;

import org.acme.secondparallel.grpc.SecondParallelService;
import org.oristool.simulator.samplers.*;
import com.google.protobuf.Empty;

import io.quarkus.grpc.GrpcService;
import io.smallrye.mutiny.Uni;

@GrpcService
public class EntryPoint implements SecondParallelService {

    @Override
    public Uni<Empty> pass(Empty request) {
        System.out.println("second-parallel executed");
        BigDecimal busywaitTime = new ExponentialSampler(new BigDecimal(1)).getSample();
        long startTime = System.currentTimeMillis();
        while (System.currentTimeMillis() - startTime < busywaitTime.doubleValue()) {
            // Busy wait
        }
        return Uni.createFrom().item(Empty.getDefaultInstance());
    }

}