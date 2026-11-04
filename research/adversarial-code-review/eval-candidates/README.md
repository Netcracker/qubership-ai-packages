# Eval-case candidates for adversarial-code-review

Pull requests from [pgjdbc/pgjdbc][pgjdbc] and [uber/NullAway][nullaway] whose review findings are known, picked to
become cases under `../cases/`. Each candidate names a commit to review and a gold set of findings, so a run of the
skill on any model can be graded against what a reviewer, a user, or a later fix found in that code.

The data comes from a [gitcrawl][gitcrawl] mirror of both repositories, synced on 2026-11-04. The scripts rebuild it
from a newer sync.

[pgjdbc]: https://github.com/pgjdbc/pgjdbc
[nullaway]: https://github.com/uber/NullAway
[gitcrawl]: https://github.com/openclaw/gitcrawl

## Classes

A candidate is a snapshot: one pull request at one commit that a reviewer commented on. Its gold set is the reviewer's
strong findings on that commit: root comments (not replies) that a model labeled `defect`, `design`, or `test`, not
`nit`, and detectable from the diff (see [prompts/prompt-label-findings.md](prompts/prompt-label-findings.md)). The
findings are the inline comments of `vlsi` on pull requests other people wrote. Only pull requests with at least 5 such
comments, gold or not, were labeled (`--min-findings` of `extract_findings.py`), so a pull request with fewer has no
snapshot.

| Class | Rule | What it tests |
| --- | --- | --- |
| Small diff, many findings | Diff of at most 400 lines, at least 4 gold findings, ranked by findings per line | Depth on a short change |
| New findings after the author's rework | Round 2 or later, at least 4 gold findings | A second round, which the case runner gives as the whole pull request at that commit |
| Medium pull request, many findings | Diff of 401 to 5000 lines, at least 5 gold findings | Coverage on a change too large to read in one pass |
| Manual reviews, before 2025 | Reviewed before 2025, at least 3 gold findings | Gold written by a person, not by an agent |
| Missed defects | A later issue or pull request blames a merged pull request for a defect, and the defect is visible in its diff | Defects nobody found in review; the gold comes from the report |

The diff size is measured from the snapshot's base to its commit, not taken from the final pull request, which may be
several rounds larger. The base is the merge base with the pull request's base commit, or with the default branch where
the mirror has no base commit.

## Where the gold set is weaker

- **Reviews from 2025 on may be agent-assisted, and the 2026 ones are.** A gold set written by an earlier version of the
  same skill rewards agreement with it. The `accepted` count in `data/snapshots.json` says how many gold findings the
  pull request author answered in the thread or changed the code near, by the pull request's last commit. It is 0 for
  old pull requests reviewed in 2026 whose authors no longer respond, such as pgjdbc#2741, #2646, #813, and #3337, and
  for a round the author has not answered yet, such as pgjdbc#4251 round 3: nobody confirmed those findings.
- **A force-push can drop the reviewed commit.** GitHub then serves neither the commit nor its diff, and the snapshot is
  left out. That removed the first round of 15 pgjdbc pull requests, among them #842, #1187, #3082, and #3148.
- **A rebase between rounds inflates the interdiff.** pgjdbc#3964 and #2646 were rebased between rounds, and the plain
  diff between their round commits is 54138 and 28814 lines. Compare rounds with `git range-diff`.
- **The labels and the missed-defect verdicts come from Claude Haiku subagents**, judged on the comment text, or on
  about 500 characters around the reference. On reading, 38 labeled findings and 9 missed-defect pairs agreed with their
  source. Beyond those, only the gold findings of the cases built from this folder were read against the code, and the
  judgments that did not hold up are in `data/overrides.jsonl`. Confirm a candidate against the code before it becomes a
  case, as [the pgjdbc-3968 case](../cases/pgjdbc-3968-shared-connect-timeout/README.md) does.

## Keeping the gold away from the model under test

The model has to see the snapshot and nothing written after it. `../cases/run-review-case.sh` provides only part of
that. It fetches the head commit into an empty repository, only as deep as the base, so the later commits of the pull
request and the default branch with the fix are not in the working copy. The ban on GitHub, though, is a sentence in the
prompt: the session runs with `--permission-mode bypassPermissions`, so nothing stops a `git fetch`, `gh`, or a web
fetch, and nothing stops it reading any file the user can read. The runner therefore records every tool call in
`tools.txt`, and a run counts only after a reader has read `tools.txt` in full and found no call that read anything
written after the snapshot. Until then the run is unverified. `access.txt` lists the calls to read first (a web tool,
`gh`, `curl`, `wget`, a `git fetch`, `pull`, `clone`, or `remote`, a `cd` or `pushd`, and a path outside the clone and
the skill copy), but an empty `access.txt` is not a clean run: it resolves a relative path against the clone and does
not follow the shell, so a path built at run time or reached after a `cd` it misses can escape it. Enforcing the rules
with `--disallowedTools` or a sandbox that sees only the working copy would make the full read unnecessary. The rules a
case built from this folder needs:

- The prompt names neither the pull request nor the issue that blamed it, and takes the description from the commit
  messages. The current description on GitHub may have been edited after the review.
- The session reads no network source, and not the gitcrawl database
  (`~/Library/Application Support/gitcrawl/gitcrawl.db` on macOS), local clones with fetched pull request refs, this
  folder, or the case's own `README.md`, which holds the gold answer.
- A later round is given without the findings of the earlier rounds. A finding from an earlier round that the author
  left unfixed is valid in the later one, and the grade does not count it against the run.
- A pull request merged before the model's training cutoff may be remembered. A candidate reported after the cutoff,
  such as pgjdbc#3968, which issue #4514 blamed in November 2026, is the safer kind.

## Candidates, 2026-11-04

Generated by `scripts/list_classes.py --top 8`. *Gold* counts the gold findings, *Accepted* how many of them the author
answered or changed the code near, and *Substantive* how many were labeled `substantive`.

### Small diff, many findings

| Snapshot | Diff lines | Gold | Accepted | Substantive | Reviewed | Rare categories |
| --- | --- | --- | --- | --- | --- | --- |
| pgjdbc/pgjdbc#3337 round 1 (`89ac4bff`) | 37 | 5 | 0 | 2 | 2026 | error-handling |
| pgjdbc/pgjdbc#4484 round 1 (`377ed432`) | 50 | 4 | 0 | 1 | 2026 | error-handling |
| pgjdbc/pgjdbc#900 round 3 (`ede2da18`) | 73 | 4 | 4 | 1 | 2017 | compatibility |
| pgjdbc/pgjdbc#2741 round 1 (`454bc842`) | 288 | 11 | 0 | 7 | 2026 | error-handling, performance |
| pgjdbc/pgjdbc#4459 round 1 (`9ed14e8d`) | 197 | 4 | 4 | 0 | 2026 | - |
| pgjdbc/pgjdbc#857 round 2 (`e93883c6`) | 200 | 4 | 4 | 1 | 2017 | concurrency |
| pgjdbc/pgjdbc#4296 round 2 (`009a0d29`) | 200 | 4 | 4 | 0 | 2026 | - |
| pgjdbc/pgjdbc#1087 round 1 (`d6d7e45f`) | 210 | 4 | 4 | 0 | 2018 | - |

### New findings after the author's rework

| Snapshot | Diff lines | Gold | Accepted | Substantive | Reviewed | Rare categories |
| --- | --- | --- | --- | --- | --- | --- |
| pgjdbc/pgjdbc#4251 round 3 (`0b6a1442`) | 3749 | 20 | 0 | 9 | 2026 | compatibility, error-handling, security |
| pgjdbc/pgjdbc#4251 round 2 (`71d1f287`) | 1821 | 16 | 16 | 8 | 2026 | error-handling, security |
| pgjdbc/pgjdbc#2646 round 4 (`06269609`) | 2795 | 13 | 0 | 7 | 2026 | compatibility, error-handling, security |
| pgjdbc/pgjdbc#813 round 3 (`ea3ead97`) | 635 | 12 | 0 | 2 | 2026 | error-handling |
| pgjdbc/pgjdbc#3964 round 3 (`1d9b3a8f`) | 474 | 7 | 7 | 5 | 2026 | error-handling |
| pgjdbc/pgjdbc#4332 round 2 (`925a4385`) | 733 | 7 | 7 | 1 | 2026 | - |
| pgjdbc/pgjdbc#3964 round 4 (`f317710f`) | 1133 | 6 | 6 | 3 | 2026 | compatibility, error-handling |
| uber/NullAway#1813 round 2 (`2a38508d`) | 2569 | 5 | 5 | 1 | 2026 | - |

### Medium pull request, many findings

| Snapshot | Diff lines | Gold | Accepted | Substantive | Reviewed | Rare categories |
| --- | --- | --- | --- | --- | --- | --- |
| pgjdbc/pgjdbc#4251 round 3 (`0b6a1442`) | 3749 | 20 | 0 | 9 | 2026 | compatibility, error-handling, security |
| pgjdbc/pgjdbc#4251 round 2 (`71d1f287`) | 1821 | 16 | 16 | 8 | 2026 | error-handling, security |
| pgjdbc/pgjdbc#2646 round 4 (`06269609`) | 2795 | 13 | 0 | 7 | 2026 | compatibility, error-handling, security |
| pgjdbc/pgjdbc#813 round 3 (`ea3ead97`) | 635 | 12 | 0 | 2 | 2026 | error-handling |
| pgjdbc/pgjdbc#3964 round 3 (`1d9b3a8f`) | 474 | 7 | 7 | 5 | 2026 | error-handling |
| pgjdbc/pgjdbc#4332 round 2 (`925a4385`) | 733 | 7 | 7 | 1 | 2026 | - |
| pgjdbc/pgjdbc#3964 round 4 (`f317710f`) | 1133 | 6 | 6 | 3 | 2026 | compatibility, error-handling |
| pgjdbc/pgjdbc#4251 round 1 (`39e88b9b`) | 1756 | 6 | 6 | 2 | 2026 | error-handling, resource |

### Manual reviews, before 2025

| Snapshot | Diff lines | Gold | Accepted | Substantive | Reviewed | Rare categories |
| --- | --- | --- | --- | --- | --- | --- |
| pgjdbc/pgjdbc#857 round 2 (`e93883c6`) | 200 | 4 | 4 | 1 | 2017 | concurrency |
| pgjdbc/pgjdbc#900 round 3 (`ede2da18`) | 73 | 4 | 4 | 1 | 2017 | compatibility |
| pgjdbc/pgjdbc#1087 round 1 (`d6d7e45f`) | 210 | 4 | 4 | 0 | 2018 | - |
| pgjdbc/pgjdbc#2829 round 3 (`9e39f461`) | 446 | 4 | 4 | 0 | 2023 | - |
| pgjdbc/pgjdbc#3252 round 2 (`71bf1fa0`) | 260 | 4 | 4 | 0 | 2024 | - |
| pgjdbc/pgjdbc#857 round 1 (`4fbdf295`) | 199 | 3 | 3 | 1 | 2017 | concurrency |
| pgjdbc/pgjdbc#1946 round 6 (`dabd8c55`) | 4692 | 3 | 0 | 0 | 2024 | - |
| pgjdbc/pgjdbc#2467 round 1 (`820e35c4`) | 348 | 3 | 3 | 0 | 2022 | - |

### Missed defects

| Culprit | Reported in | Fixed by | Kind | Defect |
| --- | --- | --- | --- | --- |
| uber/NullAway#1972 | #2093 | #2095 | performance | Restoring nullness through intersection bounds made the assignment check take exponential time on cyclic bounds. |
| uber/NullAway#2015 | #2072 | #2072 | correctness | Nested nullness check of explicitly typed lambda parameters warned on overrides of null-unmarked methods, a false positive. |
| uber/NullAway#2005 | #2026 | #2026 | correctness | The unboxing check on primitive conditional expressions reports a false positive in spring-framework, breaking the snapshot build. |
| uber/NullAway#1849 | #2030 | - | crash | The stale wildcard bounds fix causes a ClassCastException on field reads through a wildcard of a class with an intersection bound. |
| pgjdbc/pgjdbc#4336 | #4437 | #4437 | docs | Javadoc from 4336 describes only the length checks, though isBroken also covers unknown message types and stalled handshakes. |
| uber/NullAway#1837 | #1845 | #1845 | correctness | Wildcard copies dropped the bound field, and the new restoration path from this change then produced wrong super-wildcard bounds. |
| uber/NullAway#1758 | #1769 | - | correctness | Inherited null-implies-null models ignore explicit @Nullable return annotations on overrides, dropping a dereference error. |
| uber/NullAway#1749 | #1799 | - | correctness | Enhanced-for dataflow tracking of nullable elements caused the 0.14.1 regression for optionally nullable iterables, per the reporter. |

The defect texts are the judge's summaries of the report, not checked against the code.

## Cases built from the candidates

Three per class, plus pgjdbc-3968, are cases under `../cases/`. Each finding became a check only after it was read
against the code at the head; the case README lists the checks and links each to its source comment or report.
Findings that did not hold up, duplicated another, or were style only were left out. A case was built from each of the
three strongest candidates of its class even where that left fewer checks than the class rule asks of a candidate:
nullaway-1968-r3 and pgjdbc-2829-r3 have 4 gold findings where a medium pull request needs 5, and pgjdbc-2420 has 2
after its override where a manual review needs 3.

| Class | Case | Commits | Checks |
| --- | --- | --- | --- |
| Small diff, many findings | [pgjdbc-900-r3-login-timeout-defaults](../cases/pgjdbc-900-r3-login-timeout-defaults/README.md) | 7 | 3 |
| Small diff, many findings | [pgjdbc-4307-updatable-table-scanner](../cases/pgjdbc-4307-updatable-table-scanner/README.md) | 1 | 4 |
| Small diff, many findings | [pgjdbc-4443-xa-rmfail-tests](../cases/pgjdbc-4443-xa-rmfail-tests/README.md) | 1 | 4 |
| New findings after the author's rework | [pgjdbc-4251-r2-oauth-bearer-auth](../cases/pgjdbc-4251-r2-oauth-bearer-auth/README.md) | 4 | 16 |
| New findings after the author's rework | [pgjdbc-3964-r3-tcp-keepalive-options](../cases/pgjdbc-3964-r3-tcp-keepalive-options/README.md) | 17 | 7 |
| New findings after the author's rework | [pgjdbc-4332-r2-bind-log-truncation](../cases/pgjdbc-4332-r2-bind-log-truncation/README.md) | 4 | 7 |
| Medium pull request, many findings | [nullaway-1813-polynull-library-models](../cases/nullaway-1813-polynull-library-models/README.md) | 28 | 5 |
| Medium pull request, many findings | [nullaway-1968-r3-method-ref-return-models](../cases/nullaway-1968-r3-method-ref-return-models/README.md) | 17 | 4 |
| Medium pull request, many findings | [pgjdbc-2829-r3-lazycleaner-phantom-refs](../cases/pgjdbc-2829-r3-lazycleaner-phantom-refs/README.md) | 14 | 3 |
| Manual reviews, before 2025 | [pgjdbc-1087-java-time-updateobject](../cases/pgjdbc-1087-java-time-updateobject/README.md) | 11 | 3 |
| Manual reviews, before 2025 | [pgjdbc-857-r2-concurrent-warnings](../cases/pgjdbc-857-r2-concurrent-warnings/README.md) | 3 | 4 |
| Manual reviews, before 2025 | [pgjdbc-2420-char-array-password](../cases/pgjdbc-2420-char-array-password/README.md) | 1 | 2 |
| Missed defects | [pgjdbc-3968-shared-connect-timeout](../cases/pgjdbc-3968-shared-connect-timeout/README.md) | 2 | 1 |
| Missed defects | [nullaway-1849-wildcard-intersection-cce](../cases/nullaway-1849-wildcard-intersection-cce/README.md) | 21 | 1 |
| Missed defects | [pgjdbc-4204-blob-skip-seek](../cases/pgjdbc-4204-blob-skip-seek/README.md) | 3 | 2 |
| Missed defects | [pgjdbc-3905-close-before-flush](../cases/pgjdbc-3905-close-before-flush/README.md) | 2 | 1 |

pgjdbc#2719 is not a missed defect, although the judge marked it introduced: a reviewer posted a suggestion that fixes
`LONG_MAX_VALUE`, and the merged commit took only half of it. Check a missed-defect candidate's review comments before
building a case from it.

Corrections found while building the cases are in `data/overrides.jsonl`, one line each with the reason, and the
scripts apply them on every rebuild. A line with `url` and `"gold": false` keeps a finding out of the gold set: two
findings the author refuted and three that are style only. A line with `repo`, `culprit`, and `verdict` replaces the
judge's verdict on a blamed pull request, as `flagged-in-review` does for pgjdbc#2719. A finding that only duplicates
another stays gold; the case merges the two into one check.

## Files

| File | What it is |
| --- | --- |
| `data/findings.jsonl` | One labeled finding per line: repository, pull request, round, commit, path, line, comment URL, the label, and, for gold findings, `author_replied` and `code_changed`. The comment text stays in the mirror; read it by URL. |
| `data/snapshots.json` | One snapshot per commit the reviewer commented on: base, commit, previous round's commit, diff size, gold finding ids, and the counts the tables show. |
| `data/missed-defects.jsonl` | One culprit pull request per line, with every issue or pull request that blamed it, the fixing pull requests, and the judge's verdict and one-sentence defect. |
| `data/overrides.jsonl` | Corrections to the labels and verdicts, with the reason for each. |
| `prompts/prompt-label-findings.md` | The prompt that labels findings, one batch per subagent. |
| `prompts/prompt-judge-missed-defects.md` | The prompt that judges missed-defect candidates. |
| `scripts/extract_findings.py` | Mirror to findings, and findings to labeling batches. |
| `scripts/build_snapshots.py` | Labeled findings to snapshots, with acceptance. |
| `scripts/find_missed_defects.py` | Mirror to missed-defect candidates. |
| `scripts/merge_missed_verdicts.py` | Candidates and judge verdicts to `data/missed-defects.jsonl`. |
| `scripts/list_classes.py` | Snapshots and verdicts to the tables above. |

## Rebuilding the data

The mirror needs the comments and review comments of every pull request the reviewer reviewed. The pgjdbc mirror had
been synced with metadata only, so this run synced those pull requests by number through GraphQL, at most 100 numbers
per call; a batch that timed out with HTTP 504 went through in batches of 10.

```bash
gh api --paginate -X GET search/issues -f q='repo:pgjdbc/pgjdbc is:pr reviewed-by:vlsi' -f per_page=100 \
  --jq '.items[].number' > reviewed.txt
split -l 100 reviewed.txt chunk_
for f in chunk_*; do
  gitcrawl sync pgjdbc/pgjdbc --numbers "$(paste -sd, - < "$f")" --state all \
    --include-comments --with pr-metadata --graphql-history
done
gitcrawl sync uber/NullAway --state all --since 2026-10-20T00:00:00Z --include-comments --with pr-metadata
```

Then, from this folder:

1. Extract the findings and the labeling batches:
   `scripts/extract_findings.py --reviewer vlsi --repo pgjdbc/pgjdbc --repo uber/NullAway --out findings.jsonl
   --batch-dir batches`.
2. Label each batch with `prompts/prompt-label-findings.md`, one Haiku subagent per batch.
3. Build the snapshots: `scripts/build_snapshots.py --findings findings.jsonl --labels 'batches/*.out.jsonl'
   --clone pgjdbc/pgjdbc=<clone> --clone uber/NullAway=<clone> --out-findings data/findings.jsonl
   --out-snapshots data/snapshots.json --overrides data/overrides.jsonl`, with `--exclude` for each pull request that
   has no code to review. This run excluded the pgjdbc release-notes, AI-rules, website-deploy, and docs pull requests
   #2541, #3359, #4335, #4437, and #4510, and the issue-template pull request NullAway#2019.
4. Find the missed-defect candidates: `scripts/find_missed_defects.py --repo pgjdbc/pgjdbc --out pgjdbc.jsonl`, and
   the same for NullAway, then judge each file with `prompts/prompt-judge-missed-defects.md` into
   `pgjdbc.verdicts.jsonl` and `NullAway.verdicts.jsonl`, one verdict per candidate in the same order.
5. Join them, one line per blamed pull request: `scripts/merge_missed_verdicts.py --pair pgjdbc.jsonl
   pgjdbc.verdicts.jsonl --pair NullAway.jsonl NullAway.verdicts.jsonl --out data/missed-defects.jsonl
   --overrides data/overrides.jsonl`.
6. Print the tables: `scripts/list_classes.py --top 8`.

`build_snapshots.py` fetches every commit it needs into the clones by sha, which adds objects but moves no branch.
