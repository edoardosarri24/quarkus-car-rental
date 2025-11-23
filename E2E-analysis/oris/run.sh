#!/bin/bash
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk use java 24.0.2-tem
INSTALL_DIR=$( cd "$( dirname "$0" )" && pwd )
(cd "$INSTALL_DIR" && java -jar oris-runner-*.jar)