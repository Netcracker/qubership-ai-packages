#!/usr/bin/env bash
# Builds discount-engine.jar from src/ into the directory given, for run-case.sh. The class file targets Java 17, so
# any JDK from 17 up runs the jar.
set -euo pipefail
out=${1:?usage: build.sh <output directory>}
src=$(cd "$(dirname "$0")/src" && pwd)
classes=$(mktemp -d)
trap 'rm -rf "$classes"' EXIT
javac --release 17 -d "$classes" "$src"/*.java
printf 'Main-Class: DiscountEngine\n' > "$classes/manifest.txt"
jar --create --file "$out/discount-engine.jar" --manifest "$classes/manifest.txt" -C "$classes" .
