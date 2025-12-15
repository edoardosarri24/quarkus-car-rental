package org.acme.users;

import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;

@RegisterRestClient(configKey = "startchoice")
@Path("startChoice")
public interface StartChoiceClient {

    @POST
    void pass();

}