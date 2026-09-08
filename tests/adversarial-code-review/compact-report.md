# Compact skill evaluation

The skill now uses one reassessment section, a discussion-action table, and a shared write procedure. Publication
permission and personal attribution are stated once. The harness supplies model metadata; the skill does not write a
`Model` line. Humanizer was applied to the technical prose without changing the review areas or verdict rules.

| Main skill | Words | Lines |
| --- | --- | --- |
| Original baseline (`3eee3aa`) | 2659 | 323 |
| Before compaction (`c4625dc`) | 3473 | 390 |
| Final compact version | 2659 | 331 |

## Validation

The compact draft scored 22/22 lifecycle cases and 8/8 reassessment cases on both GitHub and GitLab with Sol medium.
Those raw responses are in [lifecycle](compact-lifecycle-sol.json) and [reassessment](compact-reassessment-sol.json).
One fresh agent handled both suites and platforms; these are batched observations, not independent repeated samples.
The fixtures and expected decisions are unchanged from the earlier evaluations.

The final edits remove model-attribution instructions and make `Result:` the first line of the general comment. The
reassessment and discussion
outcome sections are byte-identical to the decision-tested draft. A separate fresh Sol medium agent tested the final
installed skill through the [local publication API](publication/README.md), using the PR #106 replay and synthetic
clarification case on each platform. It receives the skill, API contract and supplied evidence, but no expected answers.

The final publication run produced the correct decisions, thread states, comment bodies and attribution in all four
workflows. It posted and verified required explanations before resolving and read back the resulting state. However,
it reused the earlier revision read across a reply and resolve instead of refreshing the tuple before that separate
write. The strict publication score is therefore 0/4, with that same failure in each workflow. The raw traces are
committed under `publication/recorded/compact_result`; the scorer exits 1 for this recorded failure.

The preceding `compact_harness` run refreshed revisions correctly but added a PR/MR heading before the result line.
Its raw traces are retained too. Rewording the format requirement removed that heading in the final run, but these
single samples do not prove either a causal improvement or a reliable write sequence. Neither run was edited to pass.

This simulation records reads and writes, rather than asking only for a plan. It checks selected result, discussion
state,
content and operation-order rules. It does not test a live provider, transport failures, concurrent updates, native CLI
syntax, or whether a real harness appends model metadata correctly. A single batch cannot establish a reliability rate.

Both compact variants were packed and installed into isolated Codex consumers using APM 0.24.1, with the same temporary
empty-dependency manifest workaround described in [the earlier artifact report](compiled-report.md). The installed
final skill matches the source byte for byte. Skill validation, Markdown lint, package and description checks passed.
An independent comparison checked that the compression preserved the previous review and publication requirements;
model attribution was then removed at the user's request.

## Fingerprints

```text
decision-tested compact draft SKILL.md SHA-256
0662ad4bfa3b928ce4e3e5619262fe4d2ce559ad67d381cb43695a5de5af21f0
final installed SKILL.md SHA-256
59d0b704adbc5ee3c9d00d5e163eb6876da937399198f5f102c2cb949c2b367e
unchanged GitLab reference SHA-256
34bc03b94e2de6261a4abe91a5d84eee1dc942f4ccaef2c389d09777fa9f7a69
```

Repeat the decision checks with the existing scorer and the publication check with the recorded API traces:

```shell
python3 tests/adversarial-code-review/score.py tests/adversarial-code-review/compact-lifecycle-sol.json
python3 tests/adversarial-code-review/score.py \
  tests/adversarial-code-review/compact-reassessment-sol.json \
  tests/adversarial-code-review/reassessment-expected.json
python3 tests/adversarial-code-review/publication/score.py \
  tests/adversarial-code-review/publication/recorded compact_result
```
