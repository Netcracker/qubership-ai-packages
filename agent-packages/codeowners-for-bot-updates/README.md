# codeowners-for-bot-updates

Prepare a CODEOWNERS change that stops automerged Renovate and Dependabot PRs from requesting review from the code
owners. A file loses its owners when a commit the bot authored changed it, however the PR was merged. Source code, files
only a person's commit in a bot PR changed, and files a Renovate rule excludes from automerge keep them, unless a
well-known pattern reaches them.

The skill sets `disable-model-invocation: true`, so the agent does not start it on its own: invoke it by name, with
`/codeowners-for-bot-updates` in Claude Code, and say which repository or repositories to change.

## Trade-off

The skill prefers fewer review requests from bots over exact ownership of rare files. The block goes right after the `*`
line, so the project's own lines after it keep their files owned, and a bot PR to such a file still requests review from
its owners. A pattern such as `go.mod` or `values.yaml` can still reach a file that only the `*` line owned and that no
bot changed, such as `vendor/go.mod` under Renovate `ignorePaths` or a `charts/production/values.yaml` added after the
run, and that file loses its owners. The skill does not try to find such files: a line after the block, or `--keep`,
gives one its owners back.

The always-on patterns (`/.github/workflows/`, `*Dockerfile*`, the compose files, `*.gradle`) and the manifests of the
ecosystems found in the tree go ownerless whoever changes them, so a person's PR that changes only such files requests
no review either. Where the branch rules require code-owner review, the block also removes that approval gate, and the
skill asks the user before writing it.

## What it does

1. Runs `scripts/bot_paths.py`, which reads the repository's bot PRs through `gh`, with or without a clone, sorts them
   into automerged and merged by hand, and lists every path they changed with example PRs and the CODEOWNERS line that
   matches it now.
2. Proposes a block of ownerless patterns: the paths the bot's commits changed, generalized to a file name where that
   is safe, plus well-known files of the ecosystems found in the tree, so a file added later is already covered.
3. Adds override lines for paths that must keep their owners, that a pattern would otherwise reach, and that no line
   after the block owns.
4. Reports what decides whether the change is safe: whether the branch rules require code-owner review, how
   `pr-assigner` reads the file, and how lock file maintenance PRs are merged.
5. Writes the block between marker lines right after the `*` line of CODEOWNERS, so a later run replaces it, and checks
   the result against the same history before the PR is opened.

The script needs `gh` with read access to the repository, `git`, and Python 3.9 or later. It does not change any
repository.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/codeowners-for-bot-updates
```
