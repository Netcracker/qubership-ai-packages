# Case: render a nit about a name or a comment in one line and a suggestion

A case for `adversarial-code-review` and `review-delivery` on an input where `Problem:` is noise for most findings. The
change is round 2 of uber/NullAway#2080, at head `158d0ff2`: generic method inference for method references, with a
refactoring of `GenericsChecks` that leaves a misnamed helper and several stale comments. At `3e630127` every rendered
finding carried a `Problem:` paragraph, and the review of this head wrote one of 877 characters to say that
`getEnclosingResultExpressionPath` uses the JLS term "result expression" for the expression that contains the results.
Three more nits on comments (a stale step number, an ambiguous "a lambda's declared return type", a summary that omits
a case) ran to 400 to 650 characters each.

The same review found three `major` findings, false positives in lambda returns and lambda arms, whose condition and
impact a reader needs. The checks on majors keep the change from stripping those or letting them grow.

## Checks

Grade each by reading `result.md`, the body of `email.md`.

1. **A nit about a name or a comment is short.** For every `nit` whose claim is about a member name or the text of a
   comment: pass where it has no `Problem:` paragraph and its text, the claim through the end of its last block, is at
   most 60 words. Report the count that pass out of the count of such nits.
2. **A reworded comment comes as code.** Pass where at least one finding from check 1 ends in a code block that holds
   whole replacement lines, with the indentation of the lines it replaces at `158d0ff2`. `grep -c '^```' result.md`
   only finds the candidates.
3. **A code block only where it is the whole fix.** Fail for a code block under a finding whose fix also needs lines
   outside its location, such as a rename whose call sites the block does not cover, and for one under a `major`.
4. **A `major` keeps its condition.** For every `major`: pass where its text names the input that triggers the defect
   (a lambda returned from a lambda, a lambda in a conditional or `switch` arm) and what NullAway reports for it.
5. **A missing test comes with its case.** Pass where the finding on the untested `SwitchExpressionTree` check in
   `getMethodReferenceType` carries a code block with a switch arm that holds a static method reference, and where no
   finding from check 1 carries a reproducer.
6. **Majors and minors do not grow.** Pass where the words of all `major` and `minor` findings together are at most
   110% of the mean of the `base` runs of the same model.

## Skill parts

- `adversarial-code-review`: `references/finding-rules.md` §Content and §Location; `references/verify.md`, the step
  that cuts `problem` and moves replacement text to `suggestion`
- `review-delivery`: `SKILL.md` §Rules for every renderer, *One finding*; §Email; `schema/review.schema.json`, the
  `problem`, `proposed_solution`, `reproducer`, and `suggestion` fields

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The NullAway repository and the base and head of round 2. GitHub keeps the head as `refs/pull/2080/head`. |
| `skills` | The skills the script copies. |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |
| `<model>/<label>/…` | The outputs of one run. `base-<n>` runs the skills at `3e630127`. |

## How to run

From the repository root, once per model, arm, and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/nullaway-2080-r2-short-nits <model> <label> [<rev>]
```

The `skills` file makes the script copy `review-delivery` beside `adversarial-code-review`, so the email renders with
the delivery rules under test.

## Results

Not run yet. The case renders the email only, so it does not reach the GitHub and GitLab suggestion blocks of
`review-delivery/references/`; those have no recorded trial.
