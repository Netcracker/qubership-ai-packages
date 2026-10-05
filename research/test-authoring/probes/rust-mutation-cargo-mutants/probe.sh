#!/usr/bin/env bash
# Probes for the cargo-mutants row of references/mutation-tools.md. Needs rustup: the toolchain is the one
# rust-toolchain.toml pins. The contract with ../run.sh is in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
# cargo-mutants is a binary, not a dependency of the crate, so its version is pinned here. When the cargo-mutants on
# PATH is another release, the pinned one is installed under .tools/ and takes precedence.
set -euo pipefail
cd "$(dirname "$0")"

# renovate: datasource=crate depName=cargo-mutants
CARGO_MUTANTS_VERSION=27.1.0

# case id, then the cargo-mutants arguments. --no-shuffle and -j1 fix the order of the mutants, --no-times drops
# the build and test durations, and --timeout 3 keeps the two mutants that never leave their loop from waiting for
# the automatic timeout, which is derived from the baseline's duration and so differs between machines.
cases() {
  cat <<'CASES'
verdicts          --no-shuffle -j1 --no-times --timeout 3 --caught --unviable
in-diff           --no-shuffle -j1 --no-times --timeout 3 --caught --unviable --in-diff changed.diff
file              --no-shuffle -j1 --no-times --timeout 3 --caught --unviable --file src/other.rs
CASES
}

cargo=(cargo)
if command -v rustup >/dev/null; then
  # A cargo on PATH ahead of rustup's proxy (Homebrew's, say) ignores rust-toolchain.toml.
  cargo=(rustup run "$(sed -nE 's/^channel = "(.*)"$/\1/p' rust-toolchain.toml)" cargo)
fi

# cargo finds the cargo-mutants in .tools/bin as a subcommand, so the mutants build under the pinned toolchain too.
cargo_mutants() {
  export PATH=$PWD/.tools/bin:$PATH
  if [ "$("${cargo[@]}" mutants --version 2>/dev/null)" != "cargo-mutants $CARGO_MUTANTS_VERSION" ]; then
    "${cargo[@]}" install --quiet --locked --root .tools cargo-mutants --version "$CARGO_MUTANTS_VERSION" >&2
  fi
  "${cargo[@]}" mutants "$@"
}

run_case() {
  local id=$1 args
  args=$(cases | awk -v id="$id" '$1 == id { $1 = ""; sub(/^ +/, ""); print }')
  [ -n "$args" ] || { echo "unknown case: $id" >&2; exit 2; }
  local out rc=0
  out=$(mktemp -d)
  # --annotations none: on GitHub Actions cargo-mutants would add a ::warning line for every missed mutant. run.sh
  # already unsets GITHUB_ACTIONS; the flag keeps a direct run of this script, on a runner, from printing them too.
  # shellcheck disable=SC2086 # the case's arguments are split on purpose
  cargo_mutants --colors never --annotations none --output "$out" $args 2>&1 || rc=$?
  rm -rf "$out"
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
