#!/usr/bin/env sh
# Runs every test file the session added or changed in the qubership-authz-agent
# checkout given as the argument, and prints how many ran and which failed.
# The repository has no test of a Makefile target, so the session decides the
# form: a Bats file runs with bats, a shell script under test/ whose name starts
# with test with bash, and a Go test file with go test on its package. A helper
# such as a fake kubectl is not run. Each file gets 10 minutes, so a
# test that sleeps through the loop for real still finishes.
set -eu
repo=${1:?usage: build.sh <qubership-authz-agent checkout>}
case_dir=$(cd "$(dirname "$0")" && pwd)
base=$(cat "$case_dir/base")

files=$( {
  git -C "$repo" diff --name-only "$base"
  git -C "$repo" ls-files --others --exclude-standard
} | grep -vxF -f "$case_dir/production-paths" | grep -E '\.bats$|^test/(.*/)?test[^/]*\.sh$|_test\.go$' | sort -u) || true

if [ -z "$files" ]; then
  echo 'no test file was added or changed'
  exit 1
fi

ran=0
failed=
for f in $files; do
  [ -f "$repo/$f" ] || continue
  ran=$((ran + 1))
  case $f in
    *.bats) cmd="bats $f" ;;
    *_test.go) cmd="go test ./$(dirname "$f")" ;;
    *) cmd="bash $f" ;;
  esac
  status=0
  # $cmd is split on purpose: the runner and the path.
  # shellcheck disable=SC2086
  out=$(cd "$repo" && timeout 600 $cmd 2>&1) || status=$?
  if [ "$status" -ne 0 ]; then
    failed="$failed
  $f (exit $status)
$(printf '%s\n' "$out" | tail -n 8 | sed 's/^/    /')"
  fi
done

n=$(printf '%s' "$failed" | grep -c '(exit ' || true)
printf '%s test files ran, %s failed%s\n' "$ran" "$n" "$failed"
[ "$n" -eq 0 ]
