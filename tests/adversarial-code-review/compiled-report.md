# Installed skill evaluation

This evaluates the combined PR #97 and discussion-lifecycle changes after APM packaging and installation. The earlier
[Sol medium comparison](reassessment-report.md) remains a separate experiment with an earlier candidate.

## Artifact and setup

APM CLI 0.24.1, pinned in `requirements.txt`, packed a temporary copy of the final package and installed it into a fresh
Codex consumer. The copy adds only `dependencies: {apm: []}` to its manifest: `apm pack` otherwise rejects a standalone
package without dependencies or marketplace configuration. The published manifest is unchanged by this workaround.

For this skill-only package, `apm install` materializes `.agents/skills/adversarial-code-review/SKILL.md` and its GitLab
reference. A subsequent `apm compile --target codex` reports no additional APM context to compile. There is no generated
AGENTS.md or rewritten skill text. Byte comparisons confirmed that both installed files equal their package sources.
The eval agents read these installed files, not source excerpts or the changed paragraphs alone.

```text
installed SKILL.md SHA-256
872a60c2cb147125ff83bc8da12bba886db1b165e90c306f9a6b69f73d3fac04
installed references/gitlab.md SHA-256
34bc03b94e2de6261a4abe91a5d84eee1dc942f4ccaef2c389d09777fa9f7a69
```

Three fresh agents ran on `gpt-5.6-sol`, reasoning `medium`: one per suite, each evaluating both platforms in a single
batch. They received only the installed skill, their fixture, and, for GitLab, the installed reference and the local
`glab` skill. They did not receive expected answers or earlier results. Facts are supplied as verified evidence; no
live review, discussion mutation, or permission failure was executed. These are single samples, not reliability rates.

## Results

The lifecycle and reassessment suites use the same fixtures, schemas, and scorer as the earlier comparison.

| Suite | GitHub | GitLab |
| --- | --- | --- |
| Lifecycle decisions, machine score | 22/22 | 22/22 |
| Reassessment decisions, machine score | 8/8 | 8/8 |
| Free-form assessment behavior, manual inspection | 4/4 | 4/4 |

The lifecycle traces include refresh, verified explanation before resolution changes, and read-back for the inspected
clarification and reopen cases. GitLab traces use the high-level note commands. Their fabricated repository URL is an
eval placeholder, not a verified mapping from project ID 42; these command strings must not be used against a live host.

The free-form suite asks for a natural reviewer report and intended discussion action, without requesting separate
confidence or solution-disposition fields. Manual inspection found the intended assessment in all four cases on each
platform: address both counterarguments and replace an unsafe remedy; accept a verified existing-contract clarification;
omit the already clarified finding in a later cycle; retain an evidenced blocker despite an appeal to authority.

This is not a clean publication-compliance result. The free-form responses omit a decisive-reply link in the new
clarification case. They propose publishing the full chat report as the general comment, rather than constructing the
restricted publication content, and say to reopen disputed threads "first" without the required verified explanation
before changing state. Their short action summaries also omit per-write refresh and read-back. These limitations remain
visible in the raw output; correct verdicts do not establish correct publication mechanics.

Raw responses: [lifecycle](compiled-lifecycle-sol.json), [reassessment](compiled-reassessment-sol.json), and
[free-form reports](compiled-reports-sol.json). Additional fixtures: [free-form cases](compiled-report-cases.json).
No outputs were rewritten to improve the scores. Local package validation, description checks, 18 Python tests, and the
marketplace producer/consumer round-trip passed. Hosted CI and real GitHub/GitLab operations are separate checks.

## Repeat

From a temporary copy of the leaf package, add the empty dependency block described above, then run the pinned APM CLI:

```shell
apm pack --offline -o /tmp/review-eval-bundle
```

In a fresh consumer, run:

```shell
apm install /tmp/review-eval-bundle/adversarial-code-review-1.0.2 --target codex
```

Verify the two installed files against the source, and use their paths in the prompts from
[the lifecycle report](README.md) and [the reassessment report](reassessment-report.md). For the free-form suite, give a
fresh agent the installed skill and `compiled-report-cases.json`; request a JSON object keyed by `github` and `gitlab`,
each containing `{id, report, discussion_action}` for every independent case. Request a natural reviewer report and
intended action, with placeholders for missing identity, revision, or links. Prohibit live services and expected-answer
access. Select Sol medium explicitly for every run.

```shell
python3 tests/adversarial-code-review/score.py tests/adversarial-code-review/compiled-lifecycle-sol.json
python3 tests/adversarial-code-review/score.py \
  tests/adversarial-code-review/compiled-reassessment-sol.json \
  tests/adversarial-code-review/reassessment-expected.json
```
