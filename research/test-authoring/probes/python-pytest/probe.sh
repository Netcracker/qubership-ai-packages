#!/usr/bin/env bash
# Probes for references/python/pytest.md. Needs uv; the contract with ../run.sh is in ../README.md:
#   probe.sh list        prints one case id per line
#   probe.sh run <case>  prints the case's output, stdout and stderr merged, then "exit code: N"
# The runner scrubs the environment (no CI, no colors, fixed width) before calling this script; a case that needs
# a variable set puts it on its own command line, so the variant is visible here and not inherited from the host.
set -euo pipefail
cd "$(dirname "$0")"

# case id, then the pytest arguments. Every case gets -p no:randomly unless it is about pytest-randomly, because
# the plugin shuffles the tests and the golden file would never settle.
cases() {
  cat <<'CASES'
report            -p no:randomly tests/test_stream.py
assert-forms      -p no:randomly tests/test_assert_forms.py
diffs             -p no:randomly tests/test_diffs.py
diffs-ci          -p no:randomly tests/test_diffs.py
diffs-v           -p no:randomly -v tests/test_diffs.py
helper-rewrite    -p no:randomly tests/test_helpers.py
parametrize       -p no:randomly tests/test_parametrize.py
parametrize-k     -p no:randomly tests/test_parametrize.py -k "minus and one"
grouping          -p no:randomly tests/test_grouping.py
raises            -p no:randomly tests/test_raises.py
randomly          tests/test_one.py
randomly-off      -p no:randomly tests/test_one.py
missing-call      -p no:randomly tests/test_missing_call.py
missing-at-import -p no:randomly tests/test_missing_at_import.py
CASES
}

# Strip what changes between machines and between releases without a change in behavior: the header's platform,
# version numbers, and the interpreter path that -v appends, the rootdir, and pytest-randomly's seed.
# ../normalize.py handles paths, durations, and temp directories for every ecosystem.
normalize() {
  local header='^platform .* -- Python [0-9.]+[^,]*, pytest-[0-9.]+, pluggy-[0-9.]+'
  local stable='platform <platform> -- Python <version>, pytest-<version>, pluggy-<version>'
  sed -E \
    -e "s|$header -- .+\$|$stable -- <python>|" \
    -e "s|$header\$|$stable|" \
    -e '/^plugins: /s/-[0-9]+(\.[0-9]+)+/-<version>/g' \
    -e 's/^rootdir: .*$/rootdir: <probe>/' \
    -e 's/--randomly-seed=[0-9]+/--randomly-seed=<seed>/g'
}

run_case() {
  local id=$1 args
  args=$(cases | awk -v id="$id" '$1 == id { $1 = ""; sub(/^ +/, ""); print }')
  [ -n "$args" ] || { echo "unknown case: $id" >&2; exit 2; }
  local env_vars=()
  case $id in
    *-ci) env_vars=(CI=true) ;;
  esac
  # The interpreter is the uv-managed CPython that .python-version pins, never one found on the host: the source
  # range pytest underlines with ^^^ comes from the compiler, and CPython 3.12.6 changed it for a `with` statement,
  # so Ubuntu 24.04's 3.12.3 prints no underline where 3.12.14 does.
  uv sync --quiet --managed-python --frozen
  local rc=0
  # -p no:cacheprovider keeps .pytest_cache out of the tree and the cachedir line out of the header.
  eval "env ${env_vars[*]:-} uv run --quiet --managed-python --frozen -- pytest -p no:cacheprovider $args" 2>&1 | normalize || rc=${PIPESTATUS[0]}
  echo "exit code: $rc"
}

case ${1:-} in
  list) cases | awk '{ print $1 }' ;;
  run) run_case "${2:?case id}" ;;
  *) echo "usage: $0 list | run <case>" >&2; exit 2 ;;
esac
