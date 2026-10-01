#!/usr/bin/env sh
# Replaces each %w of service/internal/kubernetes/route.go with %v, one at a
# time, in the checkout given as the argument, runs the package's tests, and
# prints for each mutant whether a test failed and which top-level tests did.
# The pull request's evidence is this check, since it changes no production
# code: see "Red on the base" in README.md. route.go is restored at the end.
set -eu
repo=${1:?usage: mutants.sh <paas-mediation-client checkout>}
file=$repo/service/internal/kubernetes/route.go
backup=$(mktemp)
cp "$file" "$backup"
trap 'cp "$backup" "$file"' EXIT

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
  failed=$( (cd "$repo" && go test -count=1 -json ./service/internal/kubernetes 2>/dev/null) |
    python3 -c '
import json, sys
for l in sys.stdin:
    try: e = json.loads(l)
    except ValueError: continue
    if e["Action"] == "fail" and "Test" in e and "/" not in e["Test"]: print(e["Test"])
    elif e["Action"] == "fail" and "FailedBuild" in e: print("(build failed)")
' || true)
  if [ -n "$failed" ]; then
    echo "$line:$n $site: killed by"; printf '%s\n' "$failed" | sed 's/^/  /'
  else
    echo "$line:$n $site: survived"
  fi
done
