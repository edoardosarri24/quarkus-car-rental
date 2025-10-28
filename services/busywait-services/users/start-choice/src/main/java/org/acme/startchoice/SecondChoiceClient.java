package org.acme.startchoice;

import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;

import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

@RegisterRestClient(configKey = "secondChoiceClient")
@Path("secondChoice")
public interface SecondChoiceClient {

    @POST
    void pass();

}