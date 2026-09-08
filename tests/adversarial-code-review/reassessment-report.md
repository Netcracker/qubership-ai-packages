# Reassessment structure evaluation

Compare the skill immediately before and after separating evidence assessment from feedback formatting and publication.
The baseline already includes account-based discussion ownership and Resolve/Reopen behavior. This comparison isolates
that reorganization and the explicit reassessment of confidence, blocking status, and proposed solutions.

## Setup

All four new agents use `gpt-5.6-sol` with `medium` reasoning, explicitly selected for both variants. One fresh context
per variant and suite evaluates both platforms. Each platform is evaluated in the same batch, so these are not
independent repeated samples. No live services, remote writes, or code-review verification commands are executed.
The fixtures supply already checked evidence to isolate the reviewer's subsequent decisions.

- Baseline: [pre-structure-skill.txt](pre-structure-skill.txt), with the unchanged GitLab reference.
- Candidate: the restructured skill identified by the fingerprint below, before integration with PR #97.
  The current source has since changed; see [the installed-artifact evaluation](compiled-report.md) for the final version.
- Reassessment: [8 cases](reassessment-cases.json) and [expected decisions](reassessment-expected.json).
- Discussion lifecycle: [22 cases](cases.json) and [expected decisions](expected.json).

Agents could read only their selected skill, the relevant GitLab reference and installed `glab` skill, and the fixture.
They did not receive expected answers, prior results, or the other variant. The earlier non-Sol lifecycle results in
[README.md](README.md) are a separate historical experiment and are not included in this comparison.

The reassessment output schema explicitly requests confidence, severity, solution disposition, result, reason, and
ordered operations. This tests consistent decisions when those fields are requested; it does not prove the agent would
spontaneously expose or reconsider every field in an unconstrained live review. The lifecycle schema requests action,
reply, result, reason, and ordered operations. Existing case IDs and descriptions are identical across variants.

## Results

| Suite | Baseline GitHub | Candidate GitHub | Baseline GitLab | Candidate GitLab |
| --- | --- | --- | --- | --- |
| Reassessment decisions | 8/8 | 8/8 | 8/8 | 8/8 |
| Lifecycle, raw machine score | 20/22 | 22/22 | 20/22 | 22/22 |
| Lifecycle, after manual label adjudication | 22/22 | 22/22 | 22/22 | 22/22 |

These runs show no decision-quality improvement and no observed decision regression from the restructuring. The new
text makes the assessment-before-formatting sequence explicit, but this benchmark does not prove greater reliability
in unconstrained reviews. All results are one-shot fixture observations on Sol medium, not statistical guarantees.

Raw responses: [reassessment](sol-reassessment-results.json) and [lifecycle](sol-lifecycle-results.json).
The lifecycle candidate named its operation field `ordered_operations`; that original spelling is preserved.

## Scoring and manual inspection

The scorer checks all case IDs and the decision fields against the corresponding oracle. Raw outputs are preserved.
The ordered operations and reasons also require manual inspection; a matching label alone is not proof of execution.

The initial reassessment oracle required `solution: revise` for `impact_narrowed`. The candidate kept the same optional
cleanup outcome while correctly reducing severity and changing the result to APPROVE. The fixture did not establish
that the remedy itself was wrong, so retaining or revising it are both valid. The oracle was corrected accordingly;
no skill or response was changed to satisfy that correction. Before correction, the candidate scored 7/8 per platform.

The lifecycle baseline labels `other_author` and `own_reply_only` as `reassess` rather than `none`. Its reasons and
operations explicitly leave those discussions and replies untouched. The raw scorer records those four label failures;
manual inspection treats their behavior as correct. The raw outputs and machine scores remain unchanged.

Manual inspection checks that evidence is considered before the result is finalized, unsafe proposed remedies are
revised without dismissing real defects, unsupported restrictions are evaluated as compatibility changes, and missing
risk-bearing evidence produces REVIEW_INCOMPLETE. It also checks account boundaries, draft isolation, and intended
publication actions. Proposed command sequences are not live API verification. The compact lifecycle candidate traces
do not consistently
spell out revision refresh before every separate write, and they use GitLab API fallbacks without demonstrating missing
high-level CLI support. The score does not establish full command-by-command compliance with those existing rules.

## Repeat

For the reassessment suite, give a fresh agent the selected skill and `reassessment-cases.json`, then request a JSON
object keyed by `github` and `gitlab`, each containing one entry per case:

```text
{id, confidence: high|medium|low|none, severity: blocking|non-blocking|unverified|withdrawn,
 solution: retain|revise|withdraw|defer, result: APPROVE|REQUEST_CHANGES|REVIEW_INCOMPLETE,
 reason, operations: ordered review and publication steps}
```

Use `none` for confidence when a finding is withdrawn. Tell the agent to apply the skill to supplied evidence, not to
critique the skill, and prohibit live services. For the lifecycle suite, use the prompt in [README.md](README.md).
Select Sol medium explicitly for every run. Combine each variant's returned platform arrays under variant/platform
keys without editing their contents.

```shell
python3 tests/adversarial-code-review/score.py \
  tests/adversarial-code-review/sol-reassessment-results.json \
  tests/adversarial-code-review/reassessment-expected.json
python3 tests/adversarial-code-review/score.py \
  tests/adversarial-code-review/sol-lifecycle-results.json
```

The lifecycle command exits with status 1 for the raw baseline label mismatches described above. The scorer was checked
with an intentionally retained unsafe solution and rejected it. Skill validation, Markdown lint, and `git diff --check`
pass. Earlier APM package checks and repository tests remain applicable; this pass does not run hosted CI or publish a PR.

## Input fingerprints

```text
baseline SHA-256
11bb2bb0246e11fe87c026b9c4e5f3bf6f2b369809f44894b446ebf023fc1e0d
candidate SHA-256
1017dce65d7634256af6fe68f3f051d4a2ec5530b5e0ff7436a07427452aa30a
shared GitLab reference SHA-256
34bc03b94e2de6261a4abe91a5d84eee1dc942f4ccaef2c389d09777fa9f7a69
```
