#!/usr/bin/env sh
# The case asks for a test plan, not for tests, and its harness needs a kind
# cluster, so there is nothing to build: prints what the session changed, which
# is expected to be nothing.
set -eu
repo=${1:?usage: build.sh <qubership-authz-agent checkout>}
git -C "$repo" status --short
