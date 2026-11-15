# codeowners-for-bot-updates

Prepare a CODEOWNERS change that stops automerged Renovate and Dependabot PRs from requesting review from the code
owners. A file loses its owners when a commit the bot authored changed it, however the PR was merged. Source code, files
only a person's commit changed, files a Renovate rule excludes from automerge, and paths Renovate ignores keep them.

The skill is user-invoked: ask the agent to stop code-owner review requests on bot PRs, or to roll that change out
across several repositories.

## What it does

1. Runs `scripts/bot_paths.py`, which reads the repository's bot PRs through `gh`, with or without a clone, sorts them
   into automerged and merged by hand, and lists every path they changed with example PRs and the CODEOWNERS line that
   matches it now.
2. Proposes a block of ownerless patterns: the paths the bot's commits changed, generalized to a file name where that
   is safe, plus well-known files of the ecosystems found in the tree, so a file added later is already covered.
3. Adds override lines for paths that must keep their owners and that a pattern would otherwise reach.
4. Reports what decides whether the change is safe: whether the branch rules require code-owner review, how
   `pr-assigner` reads the file, and how lock file maintenance PRs are merged.
5. Writes the block between marker lines at the end of CODEOWNERS, so a later run replaces it, and checks the result
   against the same history before the PR is opened.

The script needs `gh` with read access to the repository, `git`, and Python 3.9 or later. It does not change any
repository.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/codeowners-for-bot-updates
```
