package org.acme.startchoice;

import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;

import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

@RegisterRestClient(configKey = "firstChoiceClient")
@Path("firstChoice")
public interface FirstChoiceClient {

    @POST
    void pass();

}