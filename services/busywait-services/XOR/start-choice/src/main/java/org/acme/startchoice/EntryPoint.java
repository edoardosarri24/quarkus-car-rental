package org.acme.startchoice;

import jakarta.inject.Inject;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;

import java.util.Random;

import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.eclipse.microprofile.rest.client.inject.RestClient;

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

    @ConfigProperty(name = "probability.firstThreshold")
    double firstThreshold;
    @ConfigProperty(name = "probability.secondThreshold")
    double secondThreshold;

    @POST
    public void pass() {
        double nextService = new Random().nextDouble();
        if (nextService < firstThreshold) {
            firstChoice.pass();
        } else if (nextService < firstThreshold + secondThreshold) {
            secondChoice.pass();
        } else {
            thirdChoice.pass();
        }
    }

}