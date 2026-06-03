#!/usr/bin/env bash
# Install-smoke test: register this marketplace and try to install each package
# into a fresh project, deploying to several harness targets.
#
# It catches breakage that `apm pack --check-clean` cannot: a moved subdir, a
# broken package apm.yml, an unresolvable dependency, or a deleted/renamed
# upstream repo. `apm pack` only resolves remote refs via `git ls-remote`; it
# never clones or installs a package.
#
# The marketplace is registered from the local checkout at the current commit,
# so local-path packages resolve to this revision's files (not the repo's
# default branch); remote packages are fetched from their own repositories.
# `apm install` does not fail the process on a bad package, so success is judged
# by the lockfile, not the exit code.
#
# Environment:
#   APM_REQUIREMENTS  requirements.txt that pins apm-cli          (required)
#   TARGETS           comma-separated deploy targets              (default: claude,codex,cursor)
#   MODE              all | diff                                  (default: all)
#   BASE_SHA          base commit, required when MODE=diff
#   GITHUB_TOKEN      authenticates GitHub API calls (avoids 403 rate limits)
#
# Run locally with: make install-smoke
set -euo pipefail

req="${APM_REQUIREMENTS:?APM_REQUIREMENTS must point to a requirements.txt}"
targets="${TARGETS:-claude,codex,cursor}"
mode="${MODE:-all}"
workspace="$(git rev-parse --show-toplevel)"
ref="$(git rev-parse HEAD)"
mkt_rel=".claude-plugin/marketplace.json"
mkt_json="$workspace/$mkt_rel"
mkt_name="$(jq -r '.name' "$mkt_json")"

# Print the package names to install-test, one per line.
select_packages() {
  if [ "$mode" = all ]; then
    jq -r '.plugins[].name' "$mkt_json"
    return
  fi
  # MODE=diff: a package is in scope when its marketplace entry changed (new or
  # edited), or, for a local-path package, when files under its source directory
  # changed. Remote entries change only through apm.yml, so the entry diff
  # covers them.
  local base="${BASE_SHA:?BASE_SHA must be set when MODE=diff}"
  local changed base_json name head_entry base_entry src dir
  changed="$(git diff --name-only "$base" HEAD)"
  base_json="$(git show "$base:$mkt_rel" 2>/dev/null || echo '{}')"
  while IFS= read -r name; do
    head_entry="$(jq -cS --arg n "$name" '.plugins[] | select(.name==$n)' "$mkt_json")"
    base_entry="$(printf '%s' "$base_json" | jq -cS --arg n "$name" '(.plugins // [])[] | select(.name==$n)' 2>/dev/null || true)"
    if [ "$head_entry" != "$base_entry" ]; then
      echo "$name"
      continue
    fi
    src="$(printf '%s' "$head_entry" | jq -r '.source')"
    case "$src" in
      ./*)
        dir="${src#./}"
        if printf '%s\n' "$changed" | grep -q "^${dir%/}/"; then
          echo "$name"
        fi
        ;;
    esac
  done < <(jq -r '.plugins[].name' "$mkt_json")
}

names="$(select_packages | sort -u)"
if [ -z "$names" ]; then
  echo "No packages to install-test (mode=$mode)."
  exit 0
fi
count="$(printf '%s\n' "$names" | wc -l | tr -d ' ')"
echo "Install-testing $count package(s) [targets=$targets, mode=$mode]:"
printf '%s\n' "$names" | sed 's/^/  /'

# Isolate apm/git state in a scratch HOME so a local run does not touch the
# developer's real marketplace registrations; keep uv's cache warm.
real_home="$HOME"
state="$(mktemp -d)"
trap 'rm -rf "$state"' EXIT
export HOME="$state"
export GIT_CONFIG_GLOBAL="$state/gitconfig"
git config -f "$state/gitconfig" user.email apm-smoke@example.com
git config -f "$state/gitconfig" user.name "apm install-smoke"
git config -f "$state/gitconfig" --add safe.directory "$workspace"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$real_home/.cache/uv}"

apm() { uvx --python 3.12 --from apm-cli --with-requirements "$req" apm "$@"; }

if ! apm marketplace add "$workspace" --ref "$ref" --name "$mkt_name" >/dev/null; then
  echo "Failed to register marketplace from $workspace at $ref" >&2
  exit 1
fi

rc=0
while IFS= read -r name; do
  proj="$(mktemp -d)"
  if (
        cd "$proj" || exit 1
        printf 'name: smoke\nversion: 0.0.0\n' > apm.yml
        mkdir -p .claude   # a harness marker so apm always has a deploy root
        apm install "${name}@${mkt_name}" --target "$targets" >/dev/null 2>&1
        [ -f apm.lock.yaml ] && grep -q -- "$name" apm.lock.yaml
     ); then
    echo "ok:   $name"
  else
    echo "FAIL: $name"
    rc=1
  fi
  rm -rf "$proj"
done <<EOF
$names
EOF

if [ "$rc" -eq 0 ]; then
  echo "All install-smoke checks passed."
else
  echo "Some install-smoke checks FAILED." >&2
fi
exit "$rc"
