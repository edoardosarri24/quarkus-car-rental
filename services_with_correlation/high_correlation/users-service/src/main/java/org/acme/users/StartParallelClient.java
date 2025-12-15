package org.acme.users;

import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;

@RegisterRestClient(configKey = "startparallel")
@Path("startParallel")
public interface StartParallelClient {

    @POST
    void pass();

}