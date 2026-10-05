#!/usr/bin/env sh
# Replaces each %w of service/internal/kubernetes/route.go with %v, one at a
# time, in the checkout given as the argument, runs the package's tests, and
# prints for each mutant which top-level tests failed. A mutant counts as
# killed only by a failed test: one the package does not build with is
# unviable, and a run that fails with no failed test has no result. The
# script exits with 1 when any mutant is unviable or has no result.
# The pull request's evidence is this check, since it changes no production
# code: see "Red on the base" in README.md. route.go is restored at the end.
set -eu
repo=${1:?usage: mutants.sh <paas-mediation-client checkout>}
file=$repo/service/internal/kubernetes/route.go
backup=$(mktemp)
out=$(mktemp)
cp "$file" "$backup"
trap 'cp "$backup" "$file"; rm -f "$out"' EXIT
untested=0

# line:occurrence:site, for the route.go of the case's base.
for m in \
  100:1:resolveRouteResult,gateway-api-only \
  106:1:resolveRouteResult,legacy-ingress-only \
  117:1:dualModeRouteError,both-failed,httproute \
  117:2:dualModeRouteError,both-failed,ingress \
  122:1:dualModeRouteError,one-failed \
  451:1:resolveSingleResourceDeleteResult \
  462:1:dualModeDeleteError,both,httproute \
  462:2:dualModeDeleteError,both,ingress \
  465:1:dualModeDeleteError,httproute \
  467:1:dualModeDeleteError,ingress \
  23:1:errPlaceIngressIntoCache \
  283:1:HTTPRoute-cache,create \
  699:1:HTTPRoute-cache,update; do
  line=${m%%:*}; rest=${m#*:}; n=${rest%%:*}; site=${rest#*:}
  cp "$backup" "$file"
  sed -i.orig "${line}s/%w/%v/${n}" "$file" && rm -f "$file.orig"
  if cmp -s "$backup" "$file"; then
    echo "$line:$n $site: no %w to replace; route.go differs from the base"
    continue
  fi
  status=0
  (cd "$repo" && go test -count=1 -json ./service/internal/kubernetes) >"$out" 2>/dev/null || status=$?
  events=$(python3 -c '
import json, sys
for l in sys.stdin:
    try: e = json.loads(l)
    except ValueError: continue
    if e["Action"] != "fail": continue
    if "FailedBuild" in e: print("build")
    elif "Test" in e and "/" not in e["Test"]: print("test " + e["Test"])
' <"$out")
  failed=$(printf '%s\n' "$events" | sed -n 's/^test //p')
  if printf '%s\n' "$events" | grep -qx build; then
    echo "$line:$n $site: unviable, the package does not build"
    untested=$((untested + 1))
  elif [ -n "$failed" ]; then
    echo "$line:$n $site: killed by"; printf '%s\n' "$failed" | sed 's/^/  /'
  elif [ "$status" -ne 0 ]; then
    echo "$line:$n $site: no result, go test exited with $status and no test failed"
    untested=$((untested + 1))
  else
    echo "$line:$n $site: survived"
  fi
done
if [ "$untested" -ne 0 ]; then
  echo "$untested mutants were not tested"
  exit 1
fi
