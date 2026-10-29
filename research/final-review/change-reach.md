# What else a change has to reach

Evidence for four questions in `final-review`: the paragraph of *Item 2: claimed cases covered* on hunks no sentence
claims, the paragraph on values users already pass in *Item 3: boundaries, partitions, and the negative control*, and
the two paragraphs on sets and parallel paths in *Item 7: siblings of the change*, with their analogues for a change
with no code.

## Where they come from

[Netcracker/qubership-authz-agent#122][a122] moves the kind test harnesses from manifests applied with `kubectl apply`
to a Helm test-stand chart: 48 files, +1531 −791 at the head a human reviewer first read (`17b17fcf`). Before that
review, the author's runs, `final-review` in a fresh subagent, and a Codex plus Claude cross-review all passed it. The
reviewer's first round found the defects that the rules on inherited state, documented commands, and coupled limits
address, plus a general comment with six more points. The second round, on the commit that answered the first
(`5dcb6be8`), found three more. Five of these are the classes below.

| Class | Instance in PR #122 | Round |
| --- | --- | --- |
| A member added to a set is missing from a list of the others | The fix for the timeout comment added `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` to the Makefile; `test/k8s/README.md` lists the other overrides (`KIND_CLUSTER`, `E2E_HELM_ARGS`, `E2E_BASE_URL`, and more) and not these ([comment][c-list]) | 2 |
| Prose still counts a set that grew | `.github/docker-dev-config.json` went from two components to five; `README.md` still said "CI builds both", and `.github/docs-for-publication-task.md` "the two-entry array" ([general comment][g]) | 1 |
| A fix covers one of two parallel paths | A new troubleshooting row covered `make e2e-harness` and `make parity-harness`, and its remedy said only "then `make e2e`" ([comment][c-par]) | 2 |
| An existing setting reaches a new consumer | `E2E_HELM_ARGS` started reaching the test-stand chart, which also reads `TAG`, so `--set TAG=x` meant for the product charts sent the stand after `local/pip-stub:x`, which nothing builds ([general comment][g]) | 1 |
| A hunk no sentence claims | The SVT Compose stack moved Keycloak from 26.0 to 26.3.5, carried over with the ported commits; no commit message mentions it and no SVT run checked it ([general comment][g]) | 1 |

`docs-page-authoring` already says that a new option owes the documentation an entry. The set rule asks where the lists
of the other members are, so that the entry lands in each of them. `final-review` already checks claims against tests;
the hunk rule reads in the other direction. The setting rule applies the inherited-state rule to command lines: the
values users already pass are state the change meets, so it sits next to that rule rather than restating it.

## How the questions are worded

- **Sets.** The reviewer searches for two existing members by name and reads every file that names both. A search for
  the new member cannot find the list that misses it.
- **Counts.** The old size is searched in digits and in words (`both`, `two`), because the stale sentence in PR #122
  used a word.
- **Settings.** The first wording said "take the values its documentation and its callers pass". Both Opus runs with it
  asked the question about `E2E_HELM_ARGS` and settled it on the documented example, `--set IMAGE_PULL_POLICY=Never`,
  which means the same to both charts. The committed wording asks for the names the new consumer reads that the old
  consumers also read, which is where `TAG` is.
- **Parallel paths.** The first wording asked that every remedy the change writes name each path it applies to; neither
  Opus run on the whole pull request applied it to the troubleshooting row. The committed wording says how to check a
  row: list the paths its symptom or cause names, and check that its action names a step for each.
- **The trim.** Two sentences of the committed text gave the reviewer nothing to do: that every value users pass
  reaches the new consumer, and that a fix covers each parallel path or says why not, which item *Siblings of the
  change* already asks of every site. They were cut, and the first became the instruction to check the values users
  pass, not only the documented example. Two Opus runs on each of the two discriminating cases passed every check
  after the cut.

## Results

Each cell counts Opus runs that pass the check, out of the runs in that arm; the case READMEs have the per-run grades
and costs. The runs with the questions are those with the committed paragraphs, before the trim and after it. In
`authz-agent-122-review` the two runs before the trim had an earlier paragraph on parallel paths, which that case does
not grade.

| Defect | Case | Without the questions | With the questions |
| --- | --- | --- | --- |
| New member missing from the overrides list | `authz-agent-122-pr-at-fix-review` | 0 of 2 | 4 of 4 |
| Remedy names one of two paths | `authz-agent-122-pr-at-fix-review` | 0 of 2, one more as taste | 4 of 4 |
| `TAG` through `E2E_HELM_ARGS` | `authz-agent-122-review`, `authz-agent-122-pr-at-fix-review` | 0 of 18 | 7 of 8, one partial |
| Unclaimed SVT Keycloak bump | the same two | 3 of 18, two more as taste | 8 of 8 |
| Stale "both" and "two-entry array" | the same two | 0 of 18 | 8 of 8 |

On the fix commit alone, with the review comments as the task (`authz-agent-122-fix-review`), Opus finds the first two
defects without the questions as well. The inherited-state finding of `authz-agent-122-review` held in every run with
the questions.

[a122]: https://github.com/Netcracker/qubership-authz-agent/pull/122
[g]: https://github.com/Netcracker/qubership-authz-agent/pull/122#issuecomment-6362443580
[c-list]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4358898628
[c-par]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4358898645
