#!/usr/bin/env sh
# Prints the git tree id of a skill directory: one hash over the names and
# the committed content of its files. Dates, line endings in the working
# copy, and ignored files do not enter it. A case result records it in
# skill-tree, so a rebase or an amend that leaves the skill unchanged can
# be told apart from a change to the skill without reading the history.
#
# Run from the repository root:
#   scripts/skill-tree.sh <skill directory> <rev>   the skill at a commit
#   scripts/skill-tree.sh <skill directory>         the skill in the working copy
set -eu

dir=${1:?usage: skill-tree.sh <skill directory> [<rev>]}
dir=${dir%/}

if [ $# -ge 2 ]; then
  git rev-parse "$2:$dir"
  exit
fi

# A private index for this invocation, so the caller's staged changes are
# left alone and concurrent invocations do not share one.
index=$(git rev-parse --git-path "skill-tree.$$.index")
trap 'rm -f "$index"' EXIT
GIT_INDEX_FILE=$index git read-tree HEAD
GIT_INDEX_FILE=$index git add -A -- "$dir"
GIT_INDEX_FILE=$index git write-tree --prefix="$dir/"
