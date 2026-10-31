# Case: review qubership-authz-agent#122 whole, at the commit that answered the first review

A regression case for `final-review`, with `test-authoring` loaded. The input is
[Netcracker/qubership-authz-agent#122][pr] at `5dcb6be8`, four commits on top of `58316ca6`: the three commits of
`authz-agent-122-review` and the commit that answered the reviewer's first three comments. The task, as in that case,
is the commit messages alone; the reviewer reads the whole pull request, as a human reviewer's second round did.

That round reported two defects the fix commit had introduced, and the reviewer's general comment on the earlier commit
still applied to three more. Each is one of the classes in `research/final-review/change-reach.md`.

[pr]: https://github.com/Netcracker/qubership-authz-agent/pull/122

## What it exercises

The questions of `change-reach.md`: the paragraph of `final-review` item *Claimed cases covered* on hunks no sentence
claims, the paragraph on values users already pass in item *Boundaries, partitions, and the negative control*, and the
paragraphs on sets and parallel paths in item *Siblings of the change*.

## Checks

Grade each by reading `result.md`; the grep only finds the candidates.

1. **A new member missing from a list of the others.** Pass: a substantive finding that `test/k8s/README.md` lists the
   Makefile overrides and leaves out `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`. Partial: the same, filed as taste.
   `grep -niE 'overrid' result.md`
2. **A remedy that names one of two paths.** Pass: a substantive finding that the troubleshooting row in
   `docs/local-integration-tests.md` covers `make parity-harness` and says only "then `make e2e`". Partial: the same,
   filed as taste. `grep -niE 'make parity\b|then .make e2e' result.md`
3. **`E2E_HELM_ARGS` reaches the stand.** As check 4 of `authz-agent-122-review`.
4. **A hunk no commit message claims.** As check 5 of `authz-agent-122-review`.
5. **A count that the change made stale.** As check 6 of `authz-agent-122-review`.

## Skill parts

- `final-review`: `SKILL.md` §2 items *Claimed cases covered*, *Boundaries, partitions, and the negative control*, and
  *Siblings of the change*
- `test-authoring`: loaded, not checked
- `english-developer-style`: loaded, not checked

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `58316ca6ca5d0d91932873de01fb40397d5dd4df` (the parent of the pull request's first commit), and `5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2` (the commit the second review round read). |
| `prompt.md` | The task, with `<skills>` and `<base>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` ran with the rules on documented commands and coupled limits (pull requests 182 and 183) and without the questions of `change-reach.md`; `reach-1` and `reach-2` with an earlier wording of the question on parallel paths; `reach-3` and `reach-4` with the committed text before two sentences were cut from it; `reach-5` and `reach-6` with the committed text. `skill-tree` records the tree of each skill. |

## How to run

From the repository root, once per model, arm, and run:

```bash
research/final-review/cases/run-review-case.sh research/final-review/cases/authz-agent-122-pr-at-fix-review <model> <label> <rev>
```

## Results, 2026-10-23

Opus, two runs per arm.

| Arm | Check 1 | Check 2 | Check 3 | Check 4 | Check 5 | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- |
| `base` | fail, fail | fail, partial | fail, fail | partial, fail | fail, fail | 2.60, 2.43 |
| `reach-1`, `reach-2` (earlier wording) | fail, pass | fail, fail | pass, pass | pass, pass | pass, pass | 2.19, 2.98 |
| `reach-3`, `reach-4` (committed, before the trim) | pass, pass | pass, pass | pass, partial | pass, pass | pass, pass | 2.07, 2.57 |
| `reach-5`, `reach-6` (committed) | pass, pass | pass, pass | pass, pass | pass, pass | pass, pass | 2.79, 2.68 |

- **Check 2.** The earlier wording asked that every remedy the change writes name each path it applies to. Neither run
  applied it to the troubleshooting row. The committed wording says how to check: list the paths a row's symptom or
  cause names, and check that its action names a step for each. Both runs then report the row; `reach-4` quotes the
  symptom's `make e2e-harness` **or** `make parity-harness` against the action's single `make e2e`.
- **Check 3.** `reach-4` names `TAG` and `IMAGE_PULL_POLICY` as the keys the stand shares with the product charts, then
  concludes that a value which works for the agent works for the stand, and files nothing.
- **Check 4.** `base-1` files the SVT bump as taste.
- **The trim.** `reach-5` and `reach-6` ran after two sentences that told the reviewer nothing to do were cut: that
  every value users pass reaches the new consumer, and that a fix covers each parallel path or says why not, which the
  first paragraph of item *Siblings of the change* already asks of every site. Both runs pass every check.
- **Cost.** The `reach` runs cost 2.07 to 2.98 against 2.43 and 2.60 for `base`.

`authz-agent-122-fix-review` reviews the fix commit alone, with the comments it answered as the task statement. There
the control already finds checks 1 and 2 on Opus.

## Results of the `instr` arm, 2026-10-30

`instr-<n>` ran final-review tree `796a9b8d` on branch `vs/instruction-patch-rules`, with `apm-authoring` supplied to
the reviewer as well; the change has no skill or instruction file, so no report used it. Graded by reading
`result.md`. Opus and Haiku, two runs each.

| Model | Check 1 | Check 2 | Check 3 | Check 4 | Check 5 | Words | Cost, USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Opus | pass, pass | pass, pass | pass, pass | pass, pass | fail, pass | 3102, 2457 | 2.06, 1.91 |
| Haiku | fail, pass | fail, fail | fail, pass | pass, pass | pass, fail | 1612, 1687 | 0.98, 0.70 |

- Opus checks 1 to 4 pass in both runs. Check 1: "The new suite-timeout variables are missing from the overrides list"
  (`instr-1`), "missing from the README list of overrides" (`instr-2`). Check 2: "The troubleshooting action names only
  `make e2e` for a symptom that includes `parity-harness`" (`instr-1`), "Remedy row names `make e2e` only, though its
  symptom names `parity-harness` too" (`instr-2`). Check 3: "`TAG` and `IMAGE_PULL_POLICY` ask for images nothing
  builds" (`instr-1`), "`--set TAG=…` or `IMAGE_PULL_POLICY=Always` aimed at the agent breaks the stand's `local/*`
  images" (`instr-2`), each substantive. Check 4: the SVT Keycloak bump is in a substantive row of both tables.
- Opus check 5: `instr-2` passes ("'CI builds both' is stale; the dev config builds five images"). `instr-1` has no
  finding on `README.md` "CI builds both" or on "two-entry"; its Item 7 covers the troubleshooting row, the override
  list, `kubectl wait --for=create`, and pip-stub's other users.
- Haiku check 1: `instr-2` F22 passes ("`E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` are missing from the override
  list"). `instr-1` has no finding on the override list; its Item 7 reads "The Makefile twins (`e2e-*`/`parity-*`) are
  symmetric."
- Haiku check 2: `instr-1` row 4 asks for a run of the `make e2e-down` remedy and does not mention the second path.
  `instr-2` settles it in Item 7: "the ownership troubleshooting row names both targets and one action that covers both
  namespaces."
- Haiku check 3: `instr-2` F21 passes ("`--set TAG=x`, meant for the agent, makes the stand ask for
  `local/pip-stub:x` and others, none built"). `instr-1` names neither `E2E_HELM_ARGS` nor `TAG`.
- Haiku check 4: both runs file the Keycloak bump as substantive, `instr-1` row 7 ("changes 26.0 to 26.3.5@digest") and
  `instr-2` F11.
- Haiku check 5: `instr-1` row 9 passes ("the README says CI "builds both" images from the dev config, which now lists
  five. The publication doc says "The two-entry array""). `instr-2` files the dev config only as an unclaimed hunk
  (F13, "Adds three components to the dev build config. Not claimed.").

Against the `1b1ebc3e` runs. Opus went from ten passes in ten to nine: check 5 of `instr-1` went from pass to fail. It
writes 3102 and 2457 words against 2735 and 2729 and costs 2.06 and 1.91 against 2.20 and 1.77. Haiku stays at five
passes in ten, on different cells: check 1 `instr-2` fail to pass, check 3 `instr-1` pass to fail, check 5 `instr-1`
fail to pass and `instr-2` pass to fail; check 2 is fail, fail on both trees and check 4 pass, pass. Haiku writes 1612
and 1687 words against 1721 and 1812 and costs 0.98 and 0.70 against 0.61 and 0.54; `instr-1` took 58 turns against
37.
