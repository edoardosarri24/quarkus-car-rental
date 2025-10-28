package org.acme.startchoice;

import jakarta.inject.Inject;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;

import java.math.BigDecimal;
import java.util.Random;

import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.oristool.simulator.samplers.*;

@Path("/startChoice")
public class EntryPoint {

    @Inject
    @RestClient
    private FirstChoiceClient firstChoice;

    @Inject
    @RestClient
    private SecondChoiceClient secondChoice;

    @Inject
    @RestClient
    private ThirdChoiceClient thirdChoice;

    @POST
    public void pass() {
        BigDecimal busywaitTime = new ExponentialSampler(new BigDecimal(1)).getSample();
        long startTime = System.currentTimeMillis();
        while (System.currentTimeMillis() - startTime < busywaitTime.doubleValue()) {
            // Busy wait
        }
        double nextService = new Random().nextDouble();
        double firstThreshold = 0.2;
        double secondThreshold = firstThreshold + 0.5;
        if (nextService < firstThreshold) {
            firstChoice.pass();
        } else if (nextService < secondThreshold) {
            secondChoice.pass();
        } else {
            thirdChoice.pass();
        }
    }

}