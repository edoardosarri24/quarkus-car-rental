package org.acme.firstparallel;

import java.math.BigDecimal;

import org.acme.firstparallel.grpc.FirstParallelService;
import org.oristool.simulator.samplers.*;
import com.google.protobuf.Empty;
import org.acme.firstparallel.grpc.PassResponse;

import io.quarkus.grpc.GrpcService;
import io.smallrye.mutiny.Uni;

@GrpcService
public class EntryPoint implements FirstParallelService {

    @Override
    public Uni<PassResponse> pass(Empty request) {
        BigDecimal busywaitTime = new ExponentialSampler(new BigDecimal(1).divide(new BigDecimal(2),java.math.MathContext.DECIMAL128)).getSample();
        long busyWaitTimeNs = (long) (busywaitTime.doubleValue() * 1.0E+6);
        long startTime = System.nanoTime();
        while (System.nanoTime() - startTime < busyWaitTimeNs) {
            // Busy wait
        }
        return Uni.createFrom().item(
            PassResponse.newBuilder().setBusywaitTime(busywaitTime.doubleValue())
            .build());
    }

}