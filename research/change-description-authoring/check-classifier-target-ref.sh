#!/usr/bin/env bash
# Runs the merge-model classifier of SKILL.md section 4, as the skill prints it, against target branches whose names
# carry shell syntax, and checks that each name reaches git as one revision: no command in the name runs, a file of the
# same name in the working tree changes nothing, and the count is the one of that branch. The block is read from
# SKILL.md, so the check fails when the skill's command changes into one that does not hold.
#
# Each branch is reached twice: through `gh pr view`, replaced by a stub that prints what the real `--jq` expression
# prints, and through the `origin/HEAD` fallback with the stub failing as `gh` does where no pull request exists.
#
# A base branch the remote does not have must stop the count with an error rather than print zeros.
#
# A control case runs the form an earlier draft of the skill printed, `git log -n 40 --first-parent '<target>'`, with
# the name typed in place of the placeholder, and expects the name with a `'` in it to run its command. If the control
# stops firing, the hostile names no longer exercise anything.
#
# Run from the repository root:
#   research/change-description-authoring/check-classifier-target-ref.sh
set -euo pipefail

skill=agent-packages/change-description-authoring/.apm/skills/change-description-authoring/SKILL.md
block=$(awk '/^```bash$/ {inside = 1; text = ""; next} inside && /^```$/ {inside = 0; if (text ~ /target=/) print text; next} inside {text = text $0 "\n"}' "$skill")
if [[ -z $block ]]; then
  echo "no bash block that sets target= in $skill" >&2
  exit 1
fi

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# Upstream: main holds one squash-shaped commit; every hostile branch adds one plain commit on top, so a count of
# "squash 1 plain 1" shows that git read that branch and not main.
git init -q -b main "$work/up"
git -C "$work/up" -c user.name=t -c user.email=t@t commit -q --allow-empty -m 'Add the base (#1)'
git -C "$work/up" -c user.name=t -c user.email=t@t commit-tree -p HEAD -m 'Plain commit' 'HEAD^{tree}' > "$work/plain"
# shellcheck disable=SC2016 # the names are literal; nothing in them may expand
names=(
  'main;touch${IFS}pwned'
  'main$(touch${IFS}pwned)'
  'main`touch${IFS}pwned`'
  "q';touch\${IFS}pwned;'"
)
for name in "${names[@]}"; do
  git -C "$work/up" update-ref "refs/heads/$name" "$(cat "$work/plain")"
done
git clone -q "$work/up" "$work/clone"
# An untracked file named like each target: without `--`, git log stops on "ambiguous argument".
mkdir "$work/clone/origin"
for name in "${names[@]}"; do
  touch "$work/clone/origin/$name"
done

mkdir "$work/bin"
cat > "$work/bin/gh" <<'EOF'
#!/usr/bin/env bash
# Stands in for `gh pr view --json baseRefName --jq .baseRefName`.
[[ -n ${STUB_BASE+set} ]] || { echo 'no pull requests found' >&2; exit 1; }
printf '%s\n' "$STUB_BASE"
EOF
chmod +x "$work/bin/gh"

failures=0
run_case() { # <case name> <expected output> <command text> [STUB_BASE value]
  local label=$1 want=$2 command=$3 got
  rm -f "$work/clone/pwned"
  if [[ $# -ge 4 ]]; then
    got=$(cd "$work/clone" && STUB_BASE=$4 PATH="$work/bin:$PATH" bash -c "$command" 2>&1) || true
  else
    got=$(cd "$work/clone" && PATH="$work/bin:$PATH" bash -c "$command" 2>&1) || true
  fi
  local ran=no
  [[ -e $work/clone/pwned ]] && ran=yes
  if [[ $got == "$want" && $ran == no ]]; then
    echo "ok   $label"
  else
    echo "FAIL $label: output [$got], want [$want]; command in the name ran: $ran"
    failures=$((failures + 1))
  fi
}

# origin/HEAD points at main during each pull request case, so a fallback taken by mistake counts main, not the branch.
for name in "${names[@]}"; do
  git -C "$work/clone" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
  run_case "pull request base $name" 'merge 0 squash 1 plain 1' "$block" "$name"
  git -C "$work/clone" symbolic-ref refs/remotes/origin/HEAD "refs/remotes/origin/$name"
  run_case "default branch $name" 'merge 0 squash 1 plain 1' "$block"
done

run_case 'pull request base missing from the remote' 'no commits read: the target branch is not on the remote' \
  "{ $block
} 2> /dev/null" 'release/missing'

# Control: the earlier form, the name typed between single quotes, runs the command in a name that holds a quote.
rm -f "$work/clone/pwned"
(cd "$work/clone" && bash -c "git log -n 40 --first-parent 'origin/q';touch\${IFS}pwned;'' --format='%P%x09%s'" > /dev/null 2>&1) || true
if [[ -e $work/clone/pwned ]]; then
  echo "ok   control: the quoted form runs the command in q';touch\${IFS}pwned;'"
else
  echo "FAIL control: the quoted form did not run the command, so the hostile names test nothing"
  failures=$((failures + 1))
fi

exit "$((failures > 0))"
