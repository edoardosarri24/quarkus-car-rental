package org.acme.firstchoice;

import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;

import java.math.BigDecimal;

import org.oristool.simulator.samplers.*;

@Path("/firstChoice")
public class EntryPoint {

    @POST
    public void pass() {
        BigDecimal busywaitTime = new ExponentialSampler(new BigDecimal(1)).getSample();
        long startTime = System.currentTimeMillis();
        while (System.currentTimeMillis() - startTime < busywaitTime.doubleValue()) {
            // Busy wait
        }
    }

}