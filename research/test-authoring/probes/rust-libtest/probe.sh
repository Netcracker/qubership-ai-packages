#!/usr/bin/env bash
# Probes for references/rust/libtest.md. Needs rustup: the toolchain is the one rust-toolchain.toml pins.
# The contract with ../run.sh is in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
set -euo pipefail
cd "$(dirname "$0")"

# case id, then the cargo test arguments. Every case gets --test-threads=1 unless it is about the threads: on
# several threads the "test ... FAILED" lines come in the order the tests finish, and the golden file would never
# settle. The threads case uses --quiet for the same reason; its tests pass, so it prints dots.
cases() {
  cat <<'CASES'
report         --lib -- --test-threads=1
assert-forms   --test assert_forms -- --test-threads=1
should-panic   --test should_panic -- --test-threads=1
errors         --test errors -- --test-threads=1
loop-cases     --test loop_cases -- --test-threads=1
macro-cases    --test macro_cases -- --test-threads=1
rstest-cases   --test rstest_cases -- --test-threads=1
grouping       --test grouping -- --test-threads=1
threads        --test threads -- --quiet
threads-one    --test threads -- --test-threads=1
shuffle        --test threads -- --shuffle
missing-call   --test missing_call -- --test-threads=1
non-exhaustive --test non_exhaustive -- --test-threads=1
CASES
}

# Strip what changes between machines and between releases without a change in behavior: cargo's build progress,
# the hash in a test binary's name, and the thread id libtest prints after the thread name. ../normalize.py handles
# paths and durations for every ecosystem.
normalize() {
  sed -E \
    -e '/^ *(Updating|Locking|Downloading|Downloaded|Compiling|Finished|Blocking|Adding) /d' \
    -e 's#(target/debug/deps/[A-Za-z0-9_]+)-[0-9a-f]{16}#\1-<hash>#g' \
    -e "s/^(thread '[^']*') \\([0-9]+\\) panicked/\\1 (<tid>) panicked/"
}

# A case about a compile error keeps the error lines only. The snippet, notes, and suggestions under them are
# rustc's to reword in any release, and are not what the reference claims.
compile_errors_only() {
  case $1 in
    missing-call | non-exhaustive) grep -E '^error' || true ;;
    *) cat ;;
  esac
}

run_case() {
  local id=$1 args
  args=$(cases | awk -v id="$id" '$1 == id { $1 = ""; sub(/^ +/, ""); print }')
  [ -n "$args" ] || { echo "unknown case: $id" >&2; exit 2; }
  local cargo=(cargo)
  if command -v rustup >/dev/null; then
    # A cargo on PATH ahead of rustup's proxy (Homebrew's, say) ignores rust-toolchain.toml.
    cargo=(rustup run "$(sed -nE 's/^channel = "(.*)"$/\1/p' rust-toolchain.toml)" cargo)
  fi
  # Build first, so that the case's output does not depend on whether the crates were already compiled.
  # A case whose test does not compile shows the error in its own run below.
  read -ra argv <<<"$args"
  local build=()
  for arg in "${argv[@]}"; do [ "$arg" = "--" ] && break; build+=("$arg"); done
  env -u RUSTFLAGS "${cargo[@]}" test --locked --quiet --no-run "${build[@]}" >/dev/null 2>&1 || true
  local rc=0
  env -u RUST_BACKTRACE -u RUST_TEST_THREADS -u RUST_TEST_SHUFFLE -u RUSTFLAGS \
    CARGO_TERM_COLOR=never CARGO_TERM_PROGRESS_WHEN=never \
    "${cargo[@]}" test --locked "${argv[@]}" 2>&1 | normalize | compile_errors_only "$id" || rc=${PIPESTATUS[0]}
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
