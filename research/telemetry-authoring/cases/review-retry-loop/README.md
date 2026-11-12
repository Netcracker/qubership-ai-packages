# Case: a review of a retry loop

The input is a diff to a Spring Boot service: a retry loop that logs a warning on every timed-out attempt, and on the
last one logs an error and throws. The service's HTTP client already records a timer with an `exception` tag and a span
for every call. Two findings are owed: the log-and-throw on the last attempt (§2 step 2), and the warning per attempt
inside one unit (§3 cost, §7 level). The case is the negative control for the review checklist and for the items that
had no condition before 1.2.0: a `none` line for every checklist item, a stack line proposed for `AGENTS.md` where the
imports settle the stack, a counter for every recurring logged condition, and the caller's-message rows on an error
whose limit is a private constant.

## Skill parts

- `SKILL.md`: §0 (Which reference to open), §2 (Which signal the fact owes; What a message on the caller's channel
  carries), §3 (Cost), §4 (The instrument), §7 (Severity), §9 (Review checklist)
- `references/jvm.md`: the log-and-throw linter rule
- `english-developer-style`: §7 (Review replies)

## Checks

1. **Log-and-throw named** (`log_and_throw_named`): the `log.error` before the throw goes.
1. **Per-attempt warning named** (`per_attempt_warn_named`): the warning fires per attempt, at a level for a condition
   the code recovers from.
1. **No stack line** (`no_stack_line_proposal`): no request to add a logging line to `AGENTS.md`; the imports and the
   prompt settle SLF4J and Micrometer.
1. **No per-item checklist** (`no_per_item_none`): the review reports its findings and at most one line naming what it
   checked; no item answered with `none`.
1. **No counter for a covered fact** (`no_new_instrument`): `http.client.requests` already counts every timed-out
   attempt by its `exception` tag, so a review that asks for a counter of timeouts or retries fails. An observation
   around the whole loop, which §5 admits as a parent span over an instrumented call, passes when the review ties it to
   a question it answers.
1. **No rows for a private constant** (`no_rows_for_a_private_constant`): the review does not ask the `PaymentException`
   text to say why `MAX_ATTEMPTS` exists or where to change it. A question about whether the gateway deduplicates a
   retried charge is a correctness point and does not count against this check.
1. **Short** (`at_most_500_words`).

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort. The new arm ran on skill tree `f3764558`
(`<model>/skill-tree`), the baseline on `9d2eab7`.

| Run | Findings (1, 2) | No stack line (3) | No per-item checklist (4) | No counter (5) | No rows (6) | Short (7) |
| --- | --- | --- | --- | --- | --- | --- |
| Opus r1, r2 | pass | pass | pass: one line | pass: r1 says none is needed; r2 an optional observation, tied to a question | pass; r1 warns against suggesting a raised `MAX_ATTEMPTS` | fails (554, 600 words) |
| Sonnet r1, r2 | pass | pass | pass: one line | pass: says none is needed | pass | r1 passes (474); r2 fails (505) |
| Opus baseline r1, r2 | pass | fails: proposes a logging line for `AGENTS.md` | fails: a `None` line per item | pass: a `payment.charge` observation | r1 passes; r2 fails: name a property for `MAX_ATTEMPTS` | fails (922, 1087 words) |
| Sonnet baseline r1, r2 | pass | r1 notes the missing line, r2 passes | fails: a bullet per checked item, four in each | pass | fails: r1 asks for why, where to change it, and a way out; r2 a property for `MAX_ATTEMPTS` | fails (589, 627 words) |

The case does not reach the deleted rule that counted every recurring logged condition: no run in either arm asked for
a counter of the timeouts, because the prompt names the timer that already counts them. Every run in both arms raised
whether `gateway.charge` is idempotent, a correctness point the case does not grade, and most of what keeps the reviews
over 500 words is that point: a suggested message per answer, or the method rewritten around the new text.
