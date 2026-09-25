#!/usr/bin/env bash
# Probes for references/javascript/jest.md and the Jest sentences of SKILL.md. Needs node and npm; CI installs the
# Node version in .nvmrc. The contract with ../run.sh is in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
# The runner scrubs the environment (no CI, no colors, fixed width) before calling this script; a case that needs
# a variable set puts it on its own command line, so the variant is visible here and not inherited from the host.
set -euo pipefail
cd "$(dirname "$0")"

# case id, then the jest arguments. Every case passes --ci so that a missing snapshot fails instead of being written.
cases() {
  cat <<'CASES'
report                tests/report.test.js
report-agent          tests/report.test.js
matchers              tests/matchers.test.js
message               tests/message.test.js
each                  tests/each.test.js
grouping              tests/grouping.test.js
soft                  tests/soft.test.js
assertions            tests/assertions.test.js
forgotten-await       tests/forgotten-await.test.js
missing-at-collection tests/missing-at-collection.test.js
order                 --verbose tests/order.test.js
randomize             --randomize --verbose=false tests/order.test.js
randomize-agent       --randomize --verbose=false tests/order.test.js
randomize-seed        --randomize --seed=1234 --verbose tests/order.test.js
seed-alone            --seed=1234 --verbose tests/order.test.js
CASES
}

# Jest 30 swaps its default reporter for one that prints only the failures when any of these is set, and every
# coding agent sets one of them. The -agent cases set AI_AGENT on purpose; the others unset them all, so that a probe run
# from inside an agent writes the same golden file as CI.
agent_vars=(AI_AGENT AUGMENT_AGENT CLAUDE_CODE CLAUDECODE CODEX_SANDBOX CODEX_THREAD_ID CURSOR_AGENT GEMINI_CLI
  GOOSE_PROVIDER OPENCODE REPL_ID)

# npm ci wipes node_modules, so run it only when the lock file changed since the last install.
install() {
  local stamp=node_modules/.probe-package-lock.json
  if ! cmp -s package-lock.json "$stamp" 2>/dev/null; then
    npm ci --no-audit --no-fund --loglevel=error >&2
    cp package-lock.json "$stamp"
  fi
}

# Strip what changes between machines and between releases without a change in behavior: per-test durations and
# the duration estimate from Jest's cache, a random seed, the Node version, and line numbers inside Jest and Node.
# ../normalize.py handles paths, durations, and temp directories for every ecosystem.
normalize() {
  local seed_rule='s/^Seed: +-?[0-9]+$/Seed:        <seed>/'
  [ "${1:-}" = keep-seed ] && seed_rule='s/^$//'
  sed -E \
    -e 's/ \([0-9]+ m?s\)$//' \
    -e 's/, estimated [0-9]+ m?s$//' \
    -e "$seed_rule" \
    -e 's/^Node\.js v[0-9.]+$/Node.js <version>/' \
    -e '/^ +at .*node:internal\//d' \
    -e 's/(node_modules\/[^:)]+):[0-9]+:[0-9]+/\1:<line>:<column>/g'
}

run_case() {
  local id=$1 args
  args=$(cases | awk -v id="$id" '$1 == id { $1 = ""; sub(/^ +/, ""); print }')
  [ -n "$args" ] || { echo "unknown case: $id" >&2; exit 2; }
  local env_args=()
  for var in "${agent_vars[@]}"; do env_args+=(-u "$var"); done
  case $id in
    *-agent) env_args+=(AI_AGENT=1) ;;
  esac
  local seed=
  case $args in
    *--seed=*) seed=keep-seed ;;
  esac
  install
  local rc=0
  # shellcheck disable=SC2086 # $args is a list of arguments from the table above
  env "${env_args[@]}" node node_modules/jest/bin/jest.js --ci $args 2>&1 | normalize "$seed" || rc=${PIPESTATUS[0]}
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
