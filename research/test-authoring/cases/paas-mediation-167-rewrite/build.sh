#!/usr/bin/env sh
# Runs the tests of service/internal/kubernetes, and of any other package with a
# _test.go file that differs from the case's base, in the checkout given as the
# argument, and prints how many tests ran and which failed. A subtest counts as a
# test of its own. Needs the Go toolchain go.mod asks for, or a newer one.
set -eu
repo=${1:?usage: build.sh <paas-mediation-client checkout>}
case_dir=$(cd "$(dirname "$0")" && pwd)
base=$(cat "$case_dir/base")

pkgs=$( { echo service/internal/kubernetes
  git -C "$repo" diff --name-only "$base" -- '*_test.go' | sed 's|/[^/]*$||'
  git -C "$repo" ls-files --others --exclude-standard -- '*_test.go' | sed 's|/[^/]*$||'; } |
  sort -u | sed 's|^|./|')

log=$(mktemp)
status=0
# $pkgs is split on purpose: one argument per package.
# shellcheck disable=SC2086
(cd "$repo" && go test -count=1 -json $pkgs > "$log" 2>&1) || status=$?

python3 - "$log" "$status" <<'PY'
import json, sys
log, status = sys.argv[1], int(sys.argv[2])
ran, failed, build_errors, other = 0, [], [], []
for line in open(log):
    try:
        e = json.loads(line)
    except ValueError:
        other.append(line.rstrip())
        continue
    action = e['Action']
    if action == 'build-output':
        build_errors.append(e['Output'].rstrip())
    elif 'Test' in e and action in ('pass', 'fail', 'skip'):
        ran += 1
        if action == 'fail':
            failed.append(e['Test'])
    elif 'Test' not in e and action == 'fail' and 'FailedBuild' in e:
        build_errors.append(f"{e['Package']}: build failed")
if ran == 0:
    lines = build_errors + other
    print(f'no test ran, and go test exited with {status}' + ''.join(f'\n  {l}' for l in lines[:15]))
elif status != 0 and not failed:
    print(f'{ran} tests ran and none failed, but go test exited with {status}'
          + ''.join(f'\n  {l}' for l in (build_errors + other)[:15]))
else:
    print(f'{ran} tests ran, {len(failed)} failed' + ''.join(f'\n  {t}' for t in failed))
PY
[ "$status" -eq 0 ]
