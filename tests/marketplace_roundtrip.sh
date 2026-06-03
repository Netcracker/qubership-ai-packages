#!/usr/bin/env bash
# Network-free autotest of the marketplace producer -> consumer round-trip.
#
# It builds a monorepo-hybrid marketplace from scratch with git and asserts:
#   1. `apm pack` emits the expected plugin entry (version, tags, local-path source);
#   2. the release gate passes when the index is in sync and fails on drift;
#   3. a consumer can register the marketplace, install, inspect, and uninstall;
#   4. bumping a package version is reflected after re-packing.
#
# Not covered: `apm marketplace outdated` / version-range tracking. That needs a
# remote git host (APM rejects file:// and treats ./paths as verbatim), so it
# cannot run against self-contained local repos. See docs/publishing-packages.md.
#
# Run with: make test   (or: bash tests/marketplace_roundtrip.sh)
set -euo pipefail

req="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/requirements.txt"
APM="uvx --python 3.12 --from apm-cli --with-requirements $req apm"

real_home="${HOME}"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
# Isolate APM and git state in the temp tree; keep uv's cache so uvx stays fast.
export UV_CACHE_DIR="${UV_CACHE_DIR:-$real_home/.cache/uv}"
export HOME="$work"
export GIT_CONFIG_GLOBAL="$work/gitconfig"
git config -f "$work/gitconfig" user.email test@example.com
git config -f "$work/gitconfig" user.name "apm test"

mkt="$work/mkt"
pkg="$mkt/agent-packages/demo-pkg"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok()   { echo "ok: $*"; }

write_pkg() {  # $1 = version
  mkdir -p "$pkg/.apm/skills/demo" "$pkg/.apm/instructions"
  printf 'name: demo-pkg\nversion: %s\ndescription: Demo package\n' "$1" > "$pkg/apm.yml"
  printf -- '---\nname: demo\ndescription: A demo skill\n---\n# Demo\n' > "$pkg/.apm/skills/demo/SKILL.md"
  printf -- '---\napplyTo: "**/*.md"\n---\nBe concise.\n' > "$pkg/.apm/instructions/demo.instructions.md"
}

write_marketplace() {  # $1 = package version, $2 = description
  cat > "$mkt/apm.yml" <<YML
name: demo-marketplace
version: 0.1.0
marketplace:
  owner: { name: test, url: https://example.com }
  outputs: { claude: {} }
  versioning: { strategy: per_package }
  packages:
    - name: demo-pkg
      description: $2
      source: ./agent-packages/demo-pkg
      version: $1
      tags: ["topic:testing"]
YML
}

mj="$mkt/.claude-plugin/marketplace.json"
pack() { ( cd "$mkt" && $APM pack >/dev/null ); }
gate() { ( cd "$mkt" && $APM pack --check-versions --check-clean --dry-run >/dev/null 2>&1 ); }

# --- 1. build + assert the compiled index ---
write_pkg 1.0.0
write_marketplace 1.0.0 "Demo package"
pack
grep -q '"name": "demo-pkg"'            "$mj" || fail "demo-pkg missing from marketplace.json"
grep -q '"version": "1.0.0"'            "$mj" || fail "version 1.0.0 missing"
grep -q '"topic:testing"'               "$mj" || fail "tag missing"
grep -q '"./agent-packages/demo-pkg"'   "$mj" || fail "local-path source missing"
ok "pack emits the expected entry"

git -C "$mkt" init -q -b main
git -C "$mkt" add -A && git -C "$mkt" commit -qm "marketplace 0.1.0"

# --- 2. release gate: passes in sync, fails on drift ---
gate || fail "gate failed on an in-sync tree"
ok "gate passes when in sync"

write_marketplace 1.0.0 "Demo package (edited, not re-packed)"
git -C "$mkt" commit -qam "edit apm.yml, leave marketplace.json stale"
if gate; then fail "gate did not detect drift"; fi
ok "gate detects drift"

pack
git -C "$mkt" commit -qam "re-pack"
gate || fail "gate still failing after re-pack"
ok "gate clean again after re-pack"

# --- 3. consumer round-trip ---
cons="$work/cons"
mkdir -p "$cons/.claude"   # a harness marker so install has a deploy target
printf 'name: consumer\nversion: 0.1.0\n' > "$cons/apm.yml"
# Assert on files and exit codes, not on rendered CLI tables (Rich output is
# not reliably grep-able when stdout is captured).
( cd "$cons" && $APM marketplace add "$mkt" --name demo-marketplace >/dev/null 2>&1 ) || fail "marketplace add failed"
( cd "$cons" && $APM marketplace browse demo-marketplace >/dev/null 2>&1 )            || fail "browse failed"
( cd "$cons" && $APM install demo-pkg@demo-marketplace >/dev/null 2>&1 )              || fail "install failed"
grep -q demo-pkg "$cons/apm.lock.yaml"                                               || fail "demo-pkg not recorded in apm.lock.yaml after install"
( cd "$cons" && $APM deps list >/dev/null 2>&1 )                                     || fail "deps list failed"
( cd "$cons" && $APM uninstall demo-pkg@demo-marketplace >/dev/null 2>&1 )            || fail "uninstall failed"
if grep -q demo-pkg "$cons/apm.yml" 2>/dev/null; then fail "demo-pkg still in apm.yml after uninstall"; fi
ok "consumer add -> browse -> install -> deps -> uninstall"

# --- 4. version bump is reflected after re-pack ---
write_pkg 1.1.0
write_marketplace 1.1.0 "Demo package"
pack
grep -q '"version": "1.1.0"' "$mj" || fail "version bump 1.1.0 not reflected after re-pack"
ok "version bump reflected after re-pack"

echo "PASS"
