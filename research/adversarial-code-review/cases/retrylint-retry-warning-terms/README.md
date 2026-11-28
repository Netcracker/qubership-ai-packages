# Case: review a reworded warning that misuses an RFC term and invents notation

A case for the output-text rules of `adversarial-code-review` (commit `26bab5ec`): a change whose whole product is the
text of a diagnostic, read in its golden files. Its control, where the same change uses the standard's terms and
notation, is `retrylint-retry-warning-control`.

The repository is `retrylint`, a small Python CLI that warns when an HTTP client's retry policy retries a method that
RFC 9110 does not define as idempotent (section 9.2.2). It is in `retrylint.fast-export`, with the tags `base`, `bad`,
and `control`. The change under review, tag `bad`, is one commit, `Shorten the retry warning`, that rewrites the message
in `retrylint/messages.py` and the two golden files that expect it. For `tests/golden/post_retry.conf` the warning goes
from

```text
tests/golden/post_retry.conf:3: endpoint "POST /orders" is retried up to 3 times, but POST is not idempotent (RFC 9110, section 9.2.2), and a retried request may apply its effect twice, such as creating a second resource. Remove the retry, or send an Idempotency-Key header that the server deduplicates.
```

to

```text
tests/golden/post_retry.conf:3: POST /orders => retry x3 on an unsafe method; a retry may apply its effect twice. Drop the retry policy.
```

Two defects are planted, one for each new shape of `references/axes/vocabulary.md`:

- *A defined term in another sense:* "an unsafe method". RFC 9110 defines safe (section 9.2.1) and idempotent (section
  9.2.2) as different properties. The check tests idempotency: PUT and DELETE are unsafe, and
  `tests/golden/put_delete_retry.conf` expects no warning for them.
- *Notation the output invents:* `=>` and `x3`, which neither RFC 9110 nor the tool's other output uses.

The commit message also claims a wrap at 80 columns that the change does not fix, and "Drop the retry policy" names the
whole policy file. Neither is graded here; the control commit has the same message.

## Checks

Grade each by reading `result.md`, and `review.json` where the run wrote one: the chat report shortens
`proposed_solution`, so check 3 reads it in `review.json`.

1. **The defined term.** Pass: a finding at `minor` or above says that "unsafe" is RFC 9110's safe, where the check
   tests idempotency, with PUT or DELETE as the method the text gets wrong. `grep -niE 'unsafe' result.md`
2. **The invented notation.** Pass: a finding at `minor` or above names `=>` or `x3` as notation the user cannot look
   up, that neither the standard nor the tool's other output uses. Partial: the notation is named only as an ambiguity
   of the count, only as a `nit`, or only inside another finding. Fail: not named. `grep -nE '=>|x3' result.md`
3. **The resulting text is quoted and clean.** Pass: a finding that rewords the warning quotes the whole message the
   user would see, and that message has neither "unsafe" nor `=>` and `x<n>`. Partial: one finding quotes a clean
   message, and another quotes or suggests one that keeps a planted defect. Fail: the fix is described, or only a
   fragment is quoted, or the quoted text keeps a planted defect. This is verify step 4 and *Content* of
   `references/finding-rules.md`.
4. **The output-text axes ran.** Pass: `axes` in `review.json` records `vocabulary` and `naive-reader` as `ran`.
   Partial: one of them. A run with no `review.json` is not graded (`—`).

## Skill parts

- `adversarial-code-review`: `SKILL.md`, the text above *Read the request* (every section runs on every change, and
  the files a finished round holds) and the last item of §Choose the platform path; `SKILL.md` §Choose the axes (the
  *Vocabulary* and *Naive reader* rows and the paragraph on output text); `references/finding-rules.md` §Output text,
  and the `proposed_solution` rule of §Content on output text;
  `references/axes/vocabulary.md` §Check, steps 1 and 3 (*A defined term in another sense*, *Notation the output
  invents*), and §Severity; `references/axes/naive-reader.md` §Pass 1; `references/verify.md` step 4.
- The skills `skills` lists: `review-delivery`, which holds the schema and renders the chat report, and the skills the
  axes load on a Python change. Runs before `pipe-<n>` and `hbase-<n>` copied only `adversarial-code-review` and read
  the others under `~/.claude/skills`, unrecorded.

## Files

| File | What it is |
| --- | --- |
| `retrylint.fast-export` | The repository as a `git fast-export` stream: branch `main` at `base`, and the tags `base`, `bad`, and `control`. `run-review-case.sh` imports it with the same shas. The runs fetched a bundle of the same commits; a binary bundle trips the repository's pre-commit scanner. |
| `repo`, `base`, `head` | The stream, and the commits of `base` and `bad`. |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. Before `pipe-<n>` and `hbase-<n>`, it had the session read `<skills>/adversarial-code-review/SKILL.md`; it now has it load the skill with the Skill tool. |
| `skills` | The skills `run-review-case.sh` copies and loads: `adversarial-code-review`, `review-delivery`, and the skills the axes load on a Python change. |
| `<model>/<label>/…` | The outputs of one run. `out-<n>` ran tree `228a14bd` (commit `26bab5ec`), `base-<n>` tree `f469844c` (commit `fc910a50`, before the output-text rules). `hbase-<n>` ran tree `228a14bd` and `pipe-<n>` tree `a866e653`, through the Skill tool; see *Results, Skill tool*. `review.json` was copied by hand from the run's work directory. |

## How to run

From the repository root, once per model, arm, and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/retrylint-retry-warning-terms <model> <label> [<rev>]
```

Run one at a time, and move `~/.cache/adversarial-code-review/local-retrylint-*` away before each run, then copy
`review.json` from the directory the report names. The skill names its work directory after the repository and the
head, so two runs of this case at once share one directory and overwrite each other's axis outputs, and a directory
left by an earlier run can be read as an earlier round. The first batch of these runs ran in parallel; its Opus runs
were discarded and run again one at a time.

## Results, 2026-11-28

Opus and Sonnet, two runs per arm, graded by reading `result.md` and `review.json`.

| Model | Arm | 1 term | 2 notation | 3 resulting text | 4 axes | Result | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Opus | `base` | pass, pass | partial, partial | fail, fail | fail, partial | `REQUEST_CHANGES`, both | 5.01, 4.36 |
| Opus | `out` | pass, pass | pass, pass | partial, pass | pass, pass | `REQUEST_CHANGES`, both | 6.50, 5.91 |
| Sonnet | `base` | pass, pass | partial, partial | fail, fail | —, — | `request_changes`, both | 0.13, 0.12 |
| Sonnet | `out` | pass, pass | partial, fail | fail, fail | —, — | `request_changes`, both | 0.12, 0.13 |

Check 1 does not tell the arms apart: every run finds "unsafe method", as `major`; in the Opus runs the correctness
axis compares it with the `IDEMPOTENT` set and the PUT golden. The rules show in checks 2 to 4, on Opus:

- At `base`, the vocabulary axis was skipped in one run ("no comments or member names changed") and naive-reader in
  both ("no doc comments changed"). Under `out`, both axes ran in both runs.
- At `base`, the notation is a `nit` for "symbols where words belong" (`base-1`), or a `minor` about whether 3 counts
  retries or attempts (`base-2`). Under `out`, it is a `minor` in the new shape's words: "notation no user can look up"
  (`out-1`), "notation that neither RFC 9110 nor retrylint's other output uses" (`out-2`).
- At `base`, no finding quotes a resulting message, and the suggestions keep a planted defect: `base-2` fixes the term
  with a suggestion that keeps `=> retry x`, and the notation with one that keeps "an unsafe method". Under `out`,
  `out-2` rewrites the whole message in one finding and quotes it for `post_retry.conf`, and the notation and the remedy
  findings point to that rewrite instead of quoting their own. `out-1` quotes a clean message in the notation finding,
  but its term finding quotes `POST /orders => retry x3 on a non-idempotent method; …`: each finding fixed its own part,
  and the verifier did not check the quoted text against the other planted defect.

Sonnet ran no subagent in any run. Each read `SKILL.md`, ran three or four commands, and reviewed the diff itself,
saying the change was too small for the pipeline (`out-1`: "This was a manual review of a small change"). It wrote no
`review.json`, so no verifier ran, and its fixes keep the notation (`out-2`: `POST /orders => retry x3 on a
non-idempotent method; ...`). This happens at `base` too, so it is not caused by `26bab5ec`; `SKILL.md` has no path that
reviews a small change without its subagents.

The Opus results stand for tree `228a14bd`, the skill at `26bab5ec`.

## Results, Skill tool, 2026-11-28

`run-review-case.sh` now loads the copied skills through the Skill tool, with only the project's settings, in place of
safe mode and a prompt that had the session read `SKILL.md` as a file. `skills` lists `review-delivery`, which holds the
schema and renders the chat report, and the skills the axes load on a Python change: `english-developer-style` (from
`english-us-developer-style`), `telemetry-authoring`, `pythondoc-authoring`, `test-authoring`,
`change-description-authoring`, and `docs-page-authoring`. Read as a file, the skill did not reach Sonnet: on every
wording of the text above *Read the request* tried, Sonnet reviewed the diff itself (eight runs, not kept). `hbase-<n>`
is the skill at `0d65b052` under the new runner; `pipe-<n>` is tree `a866e653`, with the text above *Read the request*
that says every section runs on every change and lists the files a finished round holds, the frontmatter clause "on
every change, a one-line fix included", and the local-branch item of §Choose the platform path.

| Model | Arm | 1 term | 2 notation | 3 resulting text | 4 axes | Subagents, `review.json` | Result | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sonnet | `hbase` | pass, pass | partial, partial | fail, fail | —, — | 0 and no, 0 and no | `request_changes`, both | 0.14, 0.14 |
| Sonnet | `pipe` | pass, pass | pass, partial | partial, fail | pass, — | 4 and yes, 1 and no | `request_changes`, both | 1.35, 0.33 |
| Opus | `pipe` | pass, pass | pass, pass | partial, pass | pass, pass | 7 and yes, 7 and yes | `request_changes`, both | 5.14, 5.09 |

Sonnet `pipe-1` ran the pipeline: its notation finding names `=>` and `retry x3` as notation RFC 9110 does not use, and
quotes a clean message, while its term finding quotes one that keeps `=> retry x3`. Sonnet `pipe-2` spawned one reviewer
over the whole diff and wrote the report itself. Neither `hbase` run, nor a third that was not kept, spawned an axis.
Opus ran every axis in each run; `pipe-1` has the partial of `out-1`, each finding quoting the warning with only its own
part fixed. Every `pipe` run that wrote `review.json` records the measurement as `skipped`, because the repository has
no coverage or mutation tool, as *Measure the changed lines* allows.

Across the three Skill-tool cases, Sonnet ran the pipeline in three of six runs at `a866e653`, and in about two of three
runs of the earlier wordings of the same text, which are not kept; Opus ran it in every run.
