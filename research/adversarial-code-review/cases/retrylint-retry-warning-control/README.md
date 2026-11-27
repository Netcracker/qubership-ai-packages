# Case: review a reworded warning that keeps the standard's terms and notation

The control of `retrylint-retry-warning-terms`, an input where the output-text rules of `adversarial-code-review`
(commit `26bab5ec`) have nothing to flag. The repository, the commit message, and the base are the same; the
head is the tag `control`, which shortens the same warning but keeps RFC 9110's term and the tool's own notation:

```text
tests/golden/post_retry.conf:3: POST /orders is retried up to 3 times, but POST is not idempotent (RFC 9110, section 9.2.2), so a retry may apply its effect twice. Remove the retry, or send an Idempotency-Key header that the server deduplicates.
```

The method followed by the path is how an HTTP/1.1 request line starts (RFC 9112, section 3), and `Idempotency-Key` is
the header of the IETF HTTP API working group draft.

## Checks

Grade each by reading `result.md`, and `review.json` where the run wrote one.

1. **No finding on the standard's terms or notation.** Pass: no finding says that "idempotent", "RFC 9110, section
   9.2.2", `POST /orders`, or `Idempotency-Key` is a term used in another sense, a coinage, or notation the output
   invents. `grep -niE 'notation|coin|unsafe|=>' result.md` finds nothing. Other findings on the text are not graded
   here, such as one on "apply its effect twice" or on the PATCH citation, which is a question of which RFC defines
   the method.
2. **The output-text axes ran.** Pass: `axes` in `review.json` records `vocabulary` and `naive-reader` as `ran`. A run
   with no `review.json` is not graded (`—`).

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Choose the axes (the *Vocabulary* and *Naive reader* rows and the paragraph on
  output text); `references/finding-rules.md` §Output text; `references/axes/vocabulary.md` §Check, step 3 (*A defined
  term in another sense*, *Notation the output invents*), and §Not a finding;
  `references/axes/naive-reader.md` §Pass 1.
- `english-developer-style` and `telemetry-authoring`, as in `retrylint-retry-warning-terms`: the installed copies under
  `~/.claude/skills`, not recorded.

## Files

| File | What it is |
| --- | --- |
| `repo` | The path of the `git fast-export` stream in `retrylint-retry-warning-terms`, relative to this directory. |
| `base`, `head` | The commits of the tags `base` and `control`. |
| `prompt.md` | The task, the same as in `retrylint-retry-warning-terms`. |
| `<model>/<label>/…` | The outputs of one run. `out-<n>` ran tree `228a14bd` (commit `26bab5ec`). `review.json` was copied by hand from the run's work directory. |

## How to run

As in `retrylint-retry-warning-terms`, one run at a time, with the case directory
`research/adversarial-code-review/cases/retrylint-retry-warning-control`.

## Results, 2026-11-28

| Model | 1 no term or notation finding | 2 axes | Result | Cost, USD |
| --- | --- | --- | --- | --- |
| Opus | pass, pass | pass, pass | `REQUEST_CHANGES`, both | 6.03, 5.68 |
| Sonnet | pass, pass | —, — | `approve`, both | 0.13, 0.12 |

No run calls a word or a symbol of the new warning a misused term or invented notation. Both Opus runs ran the
vocabulary and naive-reader axes and return `REQUEST_CHANGES` on a `major` finding about the commit message, which says
the change fixes the wrap at 80 columns where both golden warnings still take four lines. Both also raise "so a retry
may apply its effect twice" as a `minor` (the retry, not the request, owns "its effect", and three retries can apply it
four times), and say that the Idempotency-Key remedy cannot clear the warning, since the policy file cannot record the
header. Sonnet ran no subagent, as in the other case, and approved with one `minor` finding on the same commit-message
claim.
