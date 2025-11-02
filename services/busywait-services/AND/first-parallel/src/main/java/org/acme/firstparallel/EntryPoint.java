package org.acme.firstparallel;

import java.math.BigDecimal;

import org.acme.firstparallel.grpc.FirstParallelService;
import org.oristool.simulator.samplers.*;

@GrpcService
public class EntryPoint implements FirstParallelService {

    @Override
    public Uni<com.google.protobuf.Empty> pass() {
        BigDecimal busywaitTime = new ExponentialSampler(new BigDecimal(1)).getSample();
        long startTime = System.currentTimeMillis();
        while (System.currentTimeMillis() - startTime < busywaitTime.doubleValue()) {
            // Busy wait
        }
        return Uni.createFrom().item(com.google.protobuf.Empty.getDefaultInstance());
    }

}