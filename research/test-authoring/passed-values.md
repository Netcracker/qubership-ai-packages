# Values users already pass to a setting that reaches a new consumer

Evidence for the rule in `SKILL.md` §3 that a change which lets an existing setting reach a consumer it did not reach
before owes a test or a run with the values users already pass through it, not only with the documented example.

## The incident

In [Netcracker/qubership-authz-agent#122][a122], the kind harnesses moved from manifests applied with `kubectl apply`
to a Helm test-stand chart. The Makefile variable `E2E_HELM_ARGS` passed extra arguments to the `authz-agent` and
`authz-policy-admin` installs; the change passed it to the `authz-test-stand` install too. The stand reads `TAG` and
`IMAGE_PULL_POLICY` as top-level keys, as both product charts do. A human reviewer reported ([general comment][g]) that
`--set TAG=x`, meant for the product charts, makes the stand pull `local/pip-stub:x`, which nothing builds.

The comment above the variable gave one example, `E2E_HELM_ARGS='--set IMAGE_PULL_POLICY=Never'`, which means the same
to all three charts. The author's runs and two automated review passes used only that example or no value.

## Why the rule is worded as it is

`final-review` got the same question first (`research/final-review/change-reach.md`). Its first wording asked the
reviewer to take the values the documentation and the callers pass; both Opus runs with it asked the question and
settled it on the documented example. The committed wording asks for the names the new consumer reads that the old
consumers also read, which is where `TAG` is. The test-side rule keeps that step and adds what the test asserts: what
the new consumer does with a value meant for the old ones.

The rule sits next to the inherited-state rule because the values users pass are state the change meets, like a
cluster an earlier harness set up. Its row in §3's table names the small test, a render or a parse of the new consumer
with the shared key set, such as `helm template`, because it needs no cluster.

## Results

`research/test-authoring/cases/authz-agent-122-test-plan`: the session writes the test plan for the pull request. The
rule had three wordings:

- `draft`: the three steps, with one fix (a setting of the new consumer's own) and no control.
- `reach`: twelve sentences. A review of `draft` found that an intended reach is fixed by translating the value, and
  that a test showing the old value no longer reaches the consumer also passes when nothing reaches it. This wording
  listed the kinds of setting, three fixes, the control, and that after a translation the test asserts the translated
  effect.
- `trim`, committed: five sentences. A review of `reach` found the list of setting kinds, the three fixes, and the
  translation sentence to be what the model already knows; "assert what it does with it" already covers a translated
  value. The control stays as a pointer to §7's silent case.

| Model | Arm | Plans a run with `TAG` through `E2E_HELM_ARGS` | Plans a run from the old harness's state |
| --- | --- | --- | --- |
| Opus | Without the rule | 0 of 2 | 2 of 2 |
| Opus | `draft` | 2 of 2 | 2 of 2 |
| Opus | `reach` | 2 of 2 | 2 of 2 |
| Haiku | `reach` | 1 of 3, 2 partial | 3 of 3 |
| Haiku | `trim` | 2 of 3, 1 partial | 3 of 3 |

Neither Opus run without the rule mentions `E2E_HELM_ARGS`. Every Opus run with a wording of it names `TAG` as a shared
key and proposes a setting of the stand's own or stopping the pass-through, `draft` included, so the three steps and the
documented-example sentence carry the rule. Both Opus `reach` runs plan the control; no Haiku run in either arm does.
Three runs per arm cannot tell 1 of 3 from 2 of 3, so the Haiku result shows only that `trim` loses nothing measured
here. `trim` was not run on Opus.

## Cases the rule does not apply to

The cases that declare §3 or §10 were re-run, Opus, with the rule and without it (the skill before this change, with the
replaced-mechanism paragraph as it stood before PR #188 merged). None of them changes a setting, and no run applied the
rule or used its words.

| Case | Without the rule | With the rule |
| --- | --- | --- |
| `frictionless-1799-from-scratch` | the committed run | 2 runs; one partial on check 4 (the primary-key test filters the report to one error type) |
| `nullaway-1750-from-scratch` | 2 runs, every check passes | 4 runs; one fails checks 4 and 9 (five silent fields in one test), three pass every check |
| `nullaway-1834-from-scratch` | 4 runs; check 2 passes once, check 3 three times | 4 runs; check 2 passes none, check 3 once |
| `blackbox-test-design` `parity-plan`, `spec-proven` | the committed runs | 2 runs per arm; one partial per case in the with-skill arm, and test-authoring loaded in one run of eight |

Checks 2 and 3 of `nullaway-1834-from-scratch` grade which behaviors get a case and whether the first test holds its
control in the same source, rules of §4 and §7 that the change does not touch. Three of four against one of four is
within what four runs per arm can tell apart. Two `frictionless-1799-from-scratch` runs and the first two
`nullaway-1834-from-scratch` runs with the rule used `draft`, the others `reach`; none used `trim`.

[a122]: https://github.com/Netcracker/qubership-authz-agent/pull/122
[g]: https://github.com/Netcracker/qubership-authz-agent/pull/122#issuecomment-6362443580
