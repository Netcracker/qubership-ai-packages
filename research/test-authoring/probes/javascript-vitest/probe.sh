#!/usr/bin/env bash
# Probes for references/javascript/vitest.md. Needs node and npm; .nvmrc names the Node release CI sets up.
# The contract with ../run.sh is in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
# The runner scrubs the environment (no CI, no colors, fixed width) before calling this script; a case that needs
# a variable set puts it on its own command line, so the variant is visible here and not inherited from the host.
set -euo pipefail
cd "$(dirname "$0")"

# case id, then the arguments of `vitest run`. Only the shuffle cases pass --sequence.shuffle: the other files
# would report their tests in a different order on every run.
cases() {
  cat <<'CASES'
report          tests/report.test.js
order-agent     tests/order.test.js
matchers        tests/matchers.test.js
each            tests/each.test.js
soft            tests/soft.test.js
assertions      tests/assertions.test.js
no-await        tests/no-await.test.js
order           tests/order.test.js
shuffle         --sequence.shuffle tests/shuffle.test.js
shuffle-seed    --sequence.shuffle --sequence.seed=42 tests/order.test.js
seed-only       --sequence.seed=42 tests/order.test.js
missing-matcher tests/missing-matcher.test.js
missing-import  tests/missing-import.test.js
CASES
}

# npm ci wipes node_modules, so it runs only when package-lock.json changed since the last install.
install() {
  local stamp=node_modules/.probe-lock-sha lock_sha log
  lock_sha=$(git hash-object package-lock.json)
  if [ "$(cat "$stamp" 2>/dev/null)" = "$lock_sha" ]; then
    return
  fi
  if ! log=$(npm ci --ignore-scripts --no-audit --no-fund 2>&1); then
    printf '%s\n' "$log" >&2
    exit 2
  fi
  echo "$lock_sha" > "$stamp"
}

# Strip what changes between machines and between releases without a change in behavior: the version in the RUN
# header, the per-file and per-test durations, the timing breakdown, and a seed Vitest drew from the clock. A seed
# the case passes (42) stays. ../normalize.py handles paths, clock times, and temp directories for every ecosystem.
normalize() {
  sed -E \
    -e 's/^( RUN  )v[0-9][^ ]*/\1v<version>/' \
    -e 's/ [0-9]+ms$/ <duration>/' \
    -e 's/^( +Duration  ).*$/\1<duration>/' \
    -e 's/(Running tests with seed )"[0-9]{6,}"/\1"<seed>"/'
}

# std-env, which Vitest reads, takes any of these for a coding agent and then Vitest picks the minimal reporter in
# place of the default one. The golden files show the default reporter, as a developer at a terminal sees it; the
# -agent case sets AI_AGENT on its own to show what an agent sees.
agent_vars=(-u AI_AGENT -u CLAUDECODE -u CLAUDE_CODE -u CODEX_SANDBOX -u CODEX_THREAD_ID -u GEMINI_CLI -u OPENCODE
  -u AUGMENT_AGENT -u GOOSE_PROVIDER -u JUNIE_DATA -u JUNIE_SHIM_PATH -u CURSOR_AGENT -u REPL_ID)

run_case() {
  local id=$1 args
  args=$(cases | awk -v id="$id" '$1 == id { $1 = ""; sub(/^ +/, ""); print }')
  [ -n "$args" ] || { echo "unknown case: $id" >&2; exit 2; }
  install
  local env_vars=()
  case $id in
    *-agent) env_vars=(AI_AGENT=claude-code) ;;
  esac
  local rc=0
  # shellcheck disable=SC2086 # the case's arguments are split into words on purpose
  env "${agent_vars[@]}" ${env_vars[@]+"${env_vars[@]}"} node_modules/.bin/vitest run $args 2>&1 | normalize || rc=${PIPESTATUS[0]}
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
