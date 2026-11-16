---
name: codeowners-for-bot-updates
disable-model-invocation: true
description: "Prepare a pull request that edits CODEOWNERS so automerged Renovate or Dependabot PRs stop requesting review from the code owners, while PRs someone must merge by hand still reach them. Use when the user asks to stop code-owner review requests on bot PRs, to make bot-updated files ownerless, or to roll that change out across repositories."
---

# CODEOWNERS for files that bots update

A code owner gets a review request for every PR that touches a file they own, including a Renovate PR that merges
itself a few minutes later. The fix is a block of CODEOWNERS lines with no owners, placed right after the `*` line: the
last matching line wins, so a PR that changes only those files requests no review, and the project's own lines after the
block still give their files owners.

The block trades precision for fewer review requests. A pattern such as `go.mod` or `values.yaml` also reaches a rare
file whose only owner was the `*` line and that a bot never changed: a `vendor/go.mod` under Renovate `ignorePaths`, a
`charts/production/values.yaml` added after the run. Such a file loses its owners, and that is accepted. Do not add
machinery to find these files; where the owners want one reviewed, a line after the block or `--keep` gives it owners
again.

Every file a commit authored by the bot changed goes in the block, however its PR was merged: a bot PR merged by hand
is one automerge did not finish, a failed check or a major update, and it needs no review request either. A file that
only a person's commit in a bot PR changed keeps its owners. So does source code, which a bot changes only to rewrite
imports on a major update, and the files a `packageRules` entry excludes from automerge, because the review request is
the only notification such a PR sends. The author is the bot (`renovate[bot]`); the committer of a Renovate commit is
`GitHub`, because Renovate commits through the API.

## 1. Check that automerge is on

Run the script on the repository:

```bash
python3 -I <skill-dir>/scripts/bot_paths.py --repo <owner>/<name>
```

With `--repo` alone it reads everything through `gh`: the bot PRs, the tree and CODEOWNERS of the default branch, and
the branch rules. That is enough to decide whether the repository needs a PR at all, so a rollout across many
repositories runs it on each one, with `--json`, before cloning any. It takes 10 to 30 seconds per repository.

For the repositories that get a PR, clone, and pass the clone as well:

```bash
python3 -I <skill-dir>/scripts/bot_paths.py --repo <owner>/<name> --repo-dir <clone>
```

The clone adds the commits a bot pushed with no PR (Renovate branch automerge) and reads `origin/<default branch>`, so
fetch it first.

When the script exits with `none of the N bot PRs on <branch> was automerged`, stop: every bot PR there needs its review
request. Automerge comes first, through the `enable-renovate-automerge` skill.

## 2. Read the report

The summary lines decide whether the change is safe at all:

- `ruleset_requires_code_owner_review`: when it is `true` or `unknown`, ask the user before going on. The block then
  removes the code-owner approval requirement from human PRs to those files too, `.github/workflows/` included, not
  just a review request. With `false`, the change removes only review requests: say so in the PR description.
- `pr_assigner_workflows` and `pr_assigner_warnings`: Netcracker's `pr-assigner` assigns the owners of the first line
  that starts with `*`, or of the last line when no line does. The block goes right after the `*` line, so the `*` line
  stays the first one; a CODEOWNERS file with no `*` line gets the block at the end and needs the user's decision before
  it is written, because the block's `*Dockerfile*` or `*.gradle` line would come first.
- `lock_file_maintenance`: when `turn_on_automerge` is `true`, lock file maintenance PRs were merged by hand, and their
  files go ownerless anyway. The same PR then sets `"lockFileMaintenance": {"automerge": true}` in
  `renovate.json`, unless a preset the repository extends already does (Netcracker's
  `github>Netcracker/renovate-config:automerge` does); otherwise the weekly lock file PR notifies no one.
- `renovate_ignore_paths`: paths there get no more bot PRs, and their rows have the verdict `ignored`. Only the
  repository's own JSON configuration is read, not presets or inherited configuration. A pattern from the block may
  still reach an ignored path, which then loses its owners, as the trade-off above accepts.
- `prs_with_commits_by_others`: PRs where someone else pushed a commit; their files count only where a bot commit
  changed them.
- `prs_with_over_100_files`: the API lists only the first 100 files of these PRs. Check their remaining files with
  `gh pr diff <n> --name-only`.

The table lists every path a bot PR changed that is still in the tree (`--all` adds deleted ones), with its verdict, the
automerged and hand-merged PRs that changed it, and the CODEOWNERS line that matches it now. A row changed three times
or fewer lists every PR with its merge commit, so you can open each one; a row changed more often shows the count and
the latest PR.

A PR counts as automerged when GitHub auto-merge was on, when a bot merged it, or when Renovate's description says
`**Automerge**: Enabled`. The verdict of a path:

- `ownerless (automerged)`, `ownerless (merged by hand)`: a commit the bot authored changed it.
- `keep (source code)`: a bot rewrote it, usually its imports. `--ownerless-source <path>` overrides this.
- `keep (--keep)`: given with `--keep`.
- `ignored`: Renovate `ignorePaths` covers it, so no bot PR changes it any more.

A file name is written unanchored when every copy of it in the tree is bot-updated. Source code is always anchored to
its path.

Major updates are not automerged by design, and the block leaves them without a reviewer; if the user wants one, a
`packageRules` entry with `"matchUpdateTypes": ["major"]` and `reviewers` in `renovate.json` names one.

## 3. Find the files that must keep their owners

The PR history only shows the rules that have fired. Read the effective Renovate configuration, `renovate.json` and the
presets it extends (`github>Netcracker/renovate-config:automerge` and others), for:

- `packageRules` with `"automerge": false`: each file their `matchFileNames`, `matchManagers`, or `matchDepNames`
  reaches keeps its owners. Pass every such path with `--keep <path>` and rerun the script.
- `lockFileMaintenance`: whether it is enabled and whether it is automerged, which settles the lock files.
- `reviewers`, `assignees`, `assigneesFromCodeOwners`, `reviewersFromCodeOwners`: if Renovate sets reviewers or
  assignees from CODEOWNERS, the block changes those too.

When a pattern in the block matches a `keep` path, the script keeps the pattern so it covers files added later. A path
whose last matching line comes after the `*` line keeps its owners through that line. A path owned by the `*` line, or
by any line of a file that has no `*` line, gets an override line after the patterns, inside the block, with that line's
owners; the old block is left out of this lookup, so a rerun follows an ownership change. A path whose last matching
line has no owners gets no override and shows in the check of step 5. Check that the owners on each override line are
the ones the user wants.

## 4. Write the block

Write it with the script, which replaces the block in the clone's CODEOWNERS file and checks the result:

```bash
python3 -I <skill-dir>/scripts/bot_paths.py --repo <owner>/<name> --repo-dir <clone> --write
```

The block sits right after the last `*` line, or at the end of a file with no `*` line, between
`# BEGIN codeowners-for-bot-updates: ...` and `# END codeowners-for-bot-updates`. A later run with `--write` removes
the old block and writes the new one in that place, so the block follows the history without hand edits. Lines outside
the markers, the `*` line and its owners included, stay as they are, and project lines that override the block belong
after it. The patterns are sorted by name, ignoring a leading `/` or `*`, and the comment in the block links to this
skill. Remove an earlier ownerless block written by hand before the first run, or it stays in the file beside the
generated one.

A pattern comes from the history, from the always-on list (`/.github/workflows/`, `*Dockerfile*`, the compose files,
`*.gradle`, `*.gradle.kts`), or from an ecosystem found in the tree: `go.mod` and `go.sum` for Go, `pom.xml` for
Maven, the Gradle wrapper files, `Chart.yaml` and `Chart.lock` for Helm, the helmfile names Renovate reads, the
directories `apm install` writes, and so on. A well-known file name is written unanchored, so it covers every copy in
the tree and every copy added later. Other paths are anchored with a leading `/`, unless every copy of their file name
in the tree is bot-updated. A chart's `values.yaml` holds its configuration besides image tags, so it is not on the
well-known list and follows the same rule.

`tree matches` and `untouched by bots` show which existing files a pattern reaches beyond the bot history. Where the
owners would want to review those, pass the files with `--keep`, which writes an override line after the patterns unless
a line after the block owns them. A few such files losing their owners is the trade-off described at the top, not a
defect to chase.

## 5. Verify

With `--write`, the section `Paths whose last matching line in ... disagrees with the verdict` checks the written file
and must be empty, apart from paths the user decided on. To check a file edited by hand, pass it with `--codeowners
<file>` instead. The last section, `Bot-updated paths a line after the block keeps owned`, lists the paths whose bot PRs
still request review because a project line after the block owns them. That is how the placement works, not a mismatch:
show the list to the user, who may move or narrow such a line. The script matches each pattern separately with `git
check-ignore --no-index`. A combined gitignore file would stop at an excluded parent directory, and GitHub's CODEOWNERS
has no such rule. After the push, `gh api "repos/<owner>/<name>/codeowners/errors?ref=<branch>"` must return an empty
`errors` list.

## 6. Open the PR

Load `change-description-authoring` and `english-developer-style` for the commit message and the description. Use a
`chore(codeowners):` subject. A reviewer of this change needs to read in the description:

- one bot PR that requested review from every owner, as the problem;
- the files and patterns that lose their owners, and the evidence for them: automerged PRs, numbers where a file has
  few;
- what keeps its owners and why, such as rules with `automerge: false`, and whether the PR turns on lock file
  maintenance automerge;
- what changes for human PRs: review requests only, or the code-owner approval gate too, per the branch rules;
- that major updates now reach no one through CODEOWNERS, and the `renovate.json` rule that would name a reviewer;
- how the block was checked: the counts of bot-changed paths that end on an ownerless line and on an owned one.

CODEOWNERS is read from the base branch, so PRs opened after the merge are the first affected.
