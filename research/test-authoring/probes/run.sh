#!/usr/bin/env bash
# Run the framework probes and compare their output with the golden files.
#   run.sh [--update] [<ecosystem>...]
# With no ecosystem every directory holding a probe.sh runs. Exit 1 on a difference; --update rewrites the golden
# files instead. The contract each probe.sh follows is in README.md.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
root=$(git -C "$here" rev-parse --show-toplevel)
update=0; ecosystems=()
for arg in "$@"; do
  case $arg in
    --update) update=1 ;;
    -*) echo "usage: $0 [--update] [<ecosystem>...]" >&2; exit 2 ;;
    *) ecosystems+=("${arg%/}") ;;
  esac
done
if [ ${#ecosystems[@]} -eq 0 ]; then
  for probe in "$here"/*/probe.sh; do ecosystems+=("$(basename "$(dirname "$probe")")"); done
fi

# A probe runs in the same environment on every machine: no color, a fixed terminal width, one locale and time zone,
# and none of the variables a runner reads to detect CI. A case about the CI behavior sets the variable itself.
# GitHub Actions sets dozens of GITHUB_* and RUNNER_* variables, and a tool may key off any of them (cargo-mutants
# emits annotations when it sees GITHUB_ACTIONS), so both families are unset whole. The JVM on macOS takes its
# default locale from the system settings and ignores LC_ALL, so JAVA_TOOL_OPTIONS pins it for every JVM a probe
# starts, the forks of Surefire and PIT included; ../normalize.py drops the line the JVM prints about it.
scrub=(env -u CI -u BUILD_NUMBER -u TEAMCITY_VERSION -u JENKINS_URL
  -u FORCE_COLOR -u CLICOLOR_FORCE -u PY_COLORS -u PYTEST_ADDOPTS
  -u AI_AGENT -u AUGMENT_AGENT -u CLAUDE_CODE -u CLAUDECODE -u CODEX_SANDBOX -u CODEX_THREAD_ID
  -u CURSOR_AGENT -u GEMINI_CLI -u GOOSE_PROVIDER -u OPENCODE -u REPL_ID)
while IFS= read -r name; do
  case $name in GITHUB_*|RUNNER_*) scrub+=(-u "$name") ;; esac
done < <(compgen -e)
scrub+=(NO_COLOR=1 TERM=dumb COLUMNS=80 LINES=24 LC_ALL=C.UTF-8 LANG=C.UTF-8 TZ=UTC PYTHONHASHSEED=0
  "JAVA_TOOL_OPTIONS=-Duser.language=en -Duser.country=US")

failed=0
for eco in "${ecosystems[@]}"; do
  dir=$here/$eco
  [ -x "$dir/probe.sh" ] || { echo "no probe.sh in $dir" >&2; exit 2; }
  mkdir -p "$dir/expected"
  while IFS= read -r case_id; do
    golden=$dir/expected/$case_id.txt
    # </dev/null keeps a tool that reads stdin from consuming the case ids this loop reads.
    actual=$("${scrub[@]}" "$dir/probe.sh" run "$case_id" </dev/null \
      | uv run --quiet --python 3.12 --no-project python "$here/normalize.py" "$dir=<probe>" "$root=<repo>" "$HOME=<home>")
    if [ "$update" -eq 1 ]; then
      printf '%s\n' "$actual" > "$golden"
      echo "updated $eco/$case_id"
    elif [ ! -f "$golden" ]; then
      echo "missing golden $golden (run with --update)"; failed=1
    elif diff -u "$golden" <(printf '%s\n' "$actual"); then
      echo "ok $eco/$case_id"
    else
      echo "DIFF $eco/$case_id"; failed=1
    fi
  done < <("$dir/probe.sh" list)
done
exit $failed
