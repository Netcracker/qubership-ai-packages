# Case: review qubership-authz-agent#122 whole, at the commit that answered the first review

A regression case for `adversarial-code-review`, adapted from the `final-review` case of the same name. The input is
[Netcracker/qubership-authz-agent#122][pr] at `5dcb6be8`, four commits on top of `58316ca6`: the three commits of the
pull request's first round and the commit that answered the reviewer's first three comments. The GitHub integration is
not available to the session, so the description is the commit messages and the discussion is empty; the reviewer
reads the whole pull request, as a human reviewer's second round did.

That round reported two defects the fix commit had introduced, and the reviewer's general comment on the earlier commit
still applied to three more. Each is one of the classes in `research/final-review/change-reach.md`.

[pr]: https://github.com/Netcracker/qubership-authz-agent/pull/122

## What it exercises

The questions of `change-reach.md` as `adversarial-code-review` asks them: the paragraph on hunks no sentence claims in
area *Intent and scope*, the bullet *Passed values* in area *Compatibility and evolution*, and the paragraph on sets,
counts, and remedies in area *Verification and documentation*.

## Checks

Grade each by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or
`non-blocking`; a defect named only in a question under *Needed to complete the review* is partial.

1. **A new member missing from a list of the others.** Pass: a finding that `test/k8s/README.md` lists the Makefile
   overrides and leaves out `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`. `grep -niE 'overrid' result.md`
2. **A remedy that names one of two paths.** Pass: a finding that the troubleshooting row in
   `docs/local-integration-tests.md` covers `make parity-harness` and says only "then `make e2e`".
   `grep -niE 'make parity\b|then .make e2e' result.md`
3. **`E2E_HELM_ARGS` reaches the stand.** Pass: a finding that `E2E_HELM_ARGS` now reaches the test-stand install,
   which reads `TAG` (or `IMAGE_PULL_POLICY`) as the product charts do, so a value meant for them makes the stand ask
   for images nothing builds. Partial: the report names the shared keys and files nothing. Fail: neither, or a report
   that settles the question on the documented `IMAGE_PULL_POLICY` example. `grep -niE 'E2E_HELM_ARGS|TAG' result.md`
4. **A hunk no commit message claims.** Pass: a finding that the SVT Compose stack moves Keycloak from 26.0 to 26.3.5
   and no commit message says so. `grep -niE 'svt|26\.3' result.md`
5. **A count that the change made stale.** Pass: a finding on `README.md` "CI builds both" or
   `.github/docs-for-publication-task.md` "the two-entry array", now that `.github/docker-dev-config.json` lists five
   components. `grep -niE 'builds both|two-entry' result.md`

The skill keeps at most three `non-blocking` findings, so a defect the run judged optional can be dropped for the
limit; the report then has no trace of it, and the check fails.

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, areas *Intent and scope*, *Compatibility and evolution*, and
  *Verification and documentation*; §Finding model and §Report, for the limit on `non-blocking` findings

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `58316ca6ca5d0d91932873de01fb40397d5dd4df` (the parent of the pull request's first commit), and `5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2` (the commit the second review round read). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran with the skill before the questions of `change-reach.md`; `reach-1` and `reach-2` with a first wording that set no severity and left out the question on the fix's own parallel paths; `reach-3` and `reach-4` with a second wording that added both and listed no places a set's members appear; `reach-5` and `reach-6` with the committed wording, before pull request 185 added the question on a replaced mechanism; `reach-7` and `reach-8` with the committed text. `skill-tree` records the tree of the skill. |

## How to run

From the repository root, once per model, arm, and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/authz-agent-122-pr-at-fix-review <model> <label> <rev>
```

## Results, 2026-10-24

Opus, two runs per arm. `base` ran the skill at `906df48`.

| Arm | Check 1 | Check 2 | Check 3 | Check 4 | Check 5 | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- |
| `base` | fail, fail | fail, fail | fail, fail | fail, fail | fail, fail | 1.43, 1.64 |
| `reach-1`, `reach-2` (first wording) | pass, fail | pass, pass | fail, pass | pass, pass | pass, fail | 2.09, 1.66 |
| `reach-3`, `reach-4` (second wording) | fail, fail | pass, pass | pass, pass | pass, pass | fail, fail | 1.57, 1.81 |
| `reach-5`, `reach-6` (committed wording) | pass, pass | fail, pass | fail, pass | pass, fail | fail, fail | 1.68, 1.83 |
| `reach-7`, `reach-8` (committed, after PR 185) | pass, fail | fail, fail | fail, pass | pass, pass | fail, pass | 1.78, 1.62 |

- **The base arm.** Both runs report the 10-minute `-test.timeout` that the documented timeout settings leave out,
  `base-1` as `blocking` and `base-2` as `non-blocking`, and the kubectl 1.31 requirement of `kubectl wait
  --for=create`. Neither names any of the five defects. `base-1` reports the unused parity-realm fixtures, but not the
  SVT Keycloak bump, so check 4 fails.
- **The three wordings.** They pass 7, 6, and 5 checks of 10, and the committed text 5 of 10 again after pull request
  185. Two runs per wording cannot rank them: every check that one wording passes twice, another passes once. Across
  the eight `reach` runs, check 4 passes seven times, check 2 and check 3 five times, check 1 four times, and check 5
  twice.
- **The limit on `non-blocking` findings.** `reach-1`, `reach-2`, and `reach-3` each report three `non-blocking`
  findings, the most the skill allows, and the result cannot tell a defect the run never found from one it dropped for
  the limit. The second wording therefore makes an unclaimed hunk and a passed value that breaks the new consumer
  `blocking`; in the six runs since, each of the two, when reported, is `blocking`. `reach-4` and `reach-6` report one
  `non-blocking` finding and still miss the stale count, so the limit does not explain check 5.
- **The question on a replaced mechanism.** In `reach-7` and `reach-8` it takes one of the three `non-blocking`
  slots: both report that a missing suite image now fails after about 15 minutes instead of 3. Both runs fill the limit
  again.
- **The places a set's members appear.** The second wording replaced final-review's list of places (a page's table of
  overrides, a help text, a CI matrix, a schema) with "every file that names both". Both of its runs missed the
  override list; the committed text restores the list, and both of its runs find it. `reach-5` puts it in a finding of
  its own, `reach-6` inside the `blocking` finding on the timeouts.
- **Check 5.** Only `reach-1` and `reach-8` report "CI builds both". The new members there are entries of
  `.github/docker-dev-config.json`, and none of the other six runs treats that file's list of components as a set.
- **Cost.** The `reach` runs cost 1.57 to 2.09 against 1.43 and 1.64 for `base`. `base` ran before pull request 185
  and was not re-run after it.
