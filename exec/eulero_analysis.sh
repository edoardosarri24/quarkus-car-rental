#!/bin/sh

export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk use java 24.0.2-tem
cd E2E-analysis/eulero/
mvn clean
mvn compile
mvn exec:java
cd ../..