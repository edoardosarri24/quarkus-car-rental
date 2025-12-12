package org.acme.secondchoice;

import jakarta.inject.Inject;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;

import java.math.BigDecimal;

import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.oristool.simulator.samplers.*;

@Path("/secondChoice")
public class EntryPoint {

    @POST
    public void pass() {
        BigDecimal busywaitTime = new ExponentialSampler(new BigDecimal(1).divide(new BigDecimal(12))).getSample();
        long busyWaitTimeNs = (long) (busywaitTime.doubleValue() * (10^6));
        long startTime = System.nanoTime();
        while (System.nanoTime() - startTime < busyWaitTimeNs) {
            // Busy wait
        }
    }

}