#!/bin/sh

export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk use java 24.0.2-tem
cd E2E-analysis/eulero/
mvn clean
mvn install:install-file -Dfile=libs/eulero-queueing-1.0-SNAPSHOT-jar-with-dependencies.jar -DgroupId=org.oris-tool -DartifactId=eulero-queueing -Dversion=1.0-SNAPSHOT -Dpackaging=jar -DgeneratePom=true
mvn compile
mvn exec:java
cd ../..