#!/usr/bin/env bash
# Runs the java-junit6 probes on JUnit 5. The cases, the tests, and the normalization are in ../java-junit6, and only
# pom.xml differs. The contract with ../run.sh is in ../README.md.
# shellcheck disable=SC2034 # read by the sourced script
probe_src=../java-junit6/src
# shellcheck disable=SC1091 # ../java-junit6/probe.sh is checked on its own
source "$(dirname "$0")/../java-junit6/probe.sh"
