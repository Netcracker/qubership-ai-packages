#!/usr/bin/env bash
# Mechanical checks for a skill package's text; the judgment checks are in the package's AGENTS.md.
# Usage: check-skill.sh [<package dir>] [--index]   (default: the package this script sits in; exit 2 when it
#        cannot find one)
# Exits 1 on any finding. --index prints, per section of SKILL.md, every line in the package that cites it, which is
# the list of places an edit to that section has to visit.
set -u
pkg=""; index=0
for a in "$@"; do case $a in --index) index=1 ;; *) pkg=$a ;; esac; done
asked=${pkg:-$(dirname "$0")/..}
pkg=$(cd "$asked" 2>/dev/null && pwd) || { echo "no such package directory: $asked" >&2; exit 2; }
skill=""
for d in "$pkg"/.apm/skills/*/; do skill=${d%/}; break; done
[ -f "$skill/SKILL.md" ] || { echo "no SKILL.md under $pkg/.apm/skills/" >&2; exit 2; }
files=("$skill/SKILL.md")
[ -f "$pkg/README.md" ] && files+=("$pkg/README.md")
[ -d "$skill/references" ] && while IFS= read -r f; do files+=("$f"); done < <(find "$skill/references" -name '*.md' | sort)
[ -d "$pkg/.apm/instructions" ] && while IFS= read -r f; do files+=("$f"); done < <(find "$pkg/.apm/instructions" -name '*.md' | sort)
rc=0
report() { echo "$1"; rc=1; }

# 1. A cross-reference names a row, a bullet, or a rule by its content, never by its ordinal.
if out=$(grep -nE "(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth) (bullet|row)|\brule [0-9]" "${files[@]}"); then
  report "ordinal cross-references:"; echo "$out"
fi

# 2. A retired term does not survive in a table, a reference, or the README once the body has moved on.
retired='public API|public method|public accessor|public interface|a human call|latest minor of the major the project names'
if out=$(grep -nE "$retired" "${files[@]}"); then
  report "retired terms (extend the list in this script when a term is renamed):"; echo "$out"
fi

# 3. Outside a fenced block, a reference names no minor version and no measurement line; the measured output lives
#    in research/.
if [ -d "$skill/references" ]; then
  versions=$(for f in $(find "$skill/references" -name '*.md' | sort); do
    awk -v f="$f" '/^```/ { fence = !fence; next }
      !fence { l = $0; gsub(/`[^`]*`/, "", l)
        if (l ~ /measured on|[0-9]+\.[0-9]+\.[0-9]+|(^|[^0-9.])[0-9]+\.[0-9]+([^0-9.]|$)/) printf "%s:%d: %s\n", f, NR, $0 }' "$f"
  done)
  if [ -n "$versions" ]; then report "version numbers in the references:"; echo "$versions"; fi
fi

# 4. No ragged wrap: outside a fenced block, in a paragraph or a bullet, a line whose text is under 60 characters
#    followed by a continuation line is an unfinished edit.
ragged=$(for f in "${files[@]}"; do
  awk -v f="$f" '
    function text(l) { sub(/^  +/, "", l); sub(/^(- |[0-9]+\. )/, "", l); return l }
    function prose(l) { return !fence && l != "" && l !~ /^(\||#|---|```|name:|description:)/ }
    function cont(l) { return prose(l) && l !~ /^(- |[0-9]+\. )/ }
    NR == 1 && /^---$/ { front = 1; next }
    front && /^---$/ { front = 0; prev_prose = 0; next }
    front { next }
    /^```/ { fence = !fence; prev_prose = 0; next }
    { if (prev_prose && length(text(prev)) < 60 && cont($0)) printf "%s:%d: short line before a continuation: %s\n", f, NR-1, prev
      prev_prose = prose($0); prev = $0 }' "$f"
done)
if [ -n "$ragged" ]; then report "ragged wraps:"; echo "$ragged"; fi

# 5. Every §N cited anywhere in the package exists in SKILL.md; with --index, the citing lines per section.
sections=$(grep -oE '^## [0-9]+\.' "$skill/SKILL.md" | grep -oE '[0-9]+' | sort -n)
for n in $(grep -ohE '§[0-9]+' "${files[@]}" | tr -d '§' | sort -un); do
  echo "$sections" | grep -qx "$n" || report "§$n is cited but SKILL.md has no section $n"
done
if [ $index = 1 ]; then
  for n in $sections; do
    echo "== §$n is cited by:"
    grep -nE "§$n\b" "${files[@]}" | sed "s#^$pkg/##" | awk -F: '{ line = $0; sub(/^[^:]*:[^:]*:/, "", line); sub(/^ +/, "", line); printf "  %s:%s: %s\n", $1, $2, substr(line, 1, 100) }'
  done
fi
exit $rc
