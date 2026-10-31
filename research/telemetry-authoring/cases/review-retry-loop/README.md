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

Runs of 2026-10-31 on the skill at `9d2eab7` are under `<model>/baseline/`; the results of the skill these checks
test come with it.
