#!/usr/bin/env bash
# Probes for references/javascript/node-test.md. The contract with ../run.sh is in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
# Toolchain: Node at the exact version in .nvmrc, which Renovate's nvm manager bumps. The runner and node:assert ship
# with Node, so there is no package.json. NODE=/path/to/node picks a binary other than the one on PATH.
set -euo pipefail
cd "$(dirname "$0")"

# case id, then the arguments after `node --test`. One test file per case, so that a failure in one does not hide
# the others. Every case but the random-order ones runs in source order, which is the default.
cases() {
  cat <<'CASES'
report            tests/report.test.mjs
assert-forms      tests/assert-forms.test.mjs
throws            tests/throws.test.mjs
parameterized     tests/parameterized.test.mjs
each              tests/each.test.mjs
grouping          tests/grouping.test.mjs
plan              tests/plan.test.mjs
order             tests/order.test.mjs
randomize         --test-randomize tests/one.test.mjs
random-seed       --test-randomize --test-random-seed=12345 tests/order.test.mjs
random-seed-only  --test-random-seed=12345 tests/order.test.mjs
missing-call      tests/missing-call.test.mjs
missing-at-import tests/missing-at-import.test.mjs
CASES
}

# Strip what changes between machines and between releases without a change in behavior: the Node version printed
# under an uncaught error, the total duration, and the stack frames inside Node itself, whose file names and line
# numbers move with every release. A run of such frames becomes one "at <node internals>" line, keeping the " {"
# that opens the error's properties when the last frame carries it. ../normalize.py handles paths and the
# per-test durations.
normalize() {
  sed -E \
    -e 's/^Node\.js v[0-9.]+$/Node.js v<version>/' \
    -e 's/^(ℹ duration_ms) [0-9.]+$/\1 <duration>/' \
    -e 's/\([0-9]+(\.[0-9]+)?ms\)$/(<duration>)/' \
  | awk '
      /^ +at / && !/file:\/\// {
        if (!internal) { indent = substr($0, 1, match($0, /[^ ]/) - 1) }
        internal = 1; brace = / \{$/ ? " {" : ""; next
      }
      internal { print indent "at <node internals>" brace; internal = 0 }
      { print }
      END { if (internal) print indent "at <node internals>" brace }'
}

run_case() {
  local id=$1 args
  args=$(cases | awk -v id="$id" '$1 == id { $1 = ""; sub(/^ +/, ""); print }')
  [ -n "$args" ] || { echo "unknown case: $id" >&2; exit 2; }
  local node=${NODE:-node} want have
  want=v$(tr -d '[:space:]' < .nvmrc)
  have=$("$node" --version) || { echo "no node binary: $node" >&2; exit 2; }
  [ "$have" = "$want" ] || { echo "node is $have, .nvmrc pins $want; set NODE=/path/to/node" >&2; exit 2; }
  local seed=(cat)
  # Only the case that lets Node pick the seed hides it; the replay cases keep the seed they pass.
  [ "$id" = randomize ] && seed=(sed -E 's/^(ℹ Randomized test order seed:) [0-9]+$/\1 <seed>/')
  local rc=0
  # shellcheck disable=SC2086 # $args is a list of arguments from the table above
  "$node" --test $args 2>&1 | normalize | "${seed[@]}" || rc=${PIPESTATUS[0]}
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
