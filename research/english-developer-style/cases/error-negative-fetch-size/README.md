# Case: a trivial validation error

The input is `PgStatement.setFetchSize(int rows)` rejecting `rows < 0`, with the `MessageFormat` placeholder for the
value. The fix is to pass a non-negative value, which the message already says, and the call stops at the exception.
The case is the negative control for §7 *Error and log messages*: before 2.2.0 the module asked for reason, action,
and consequence in every message.

## Skill parts

- `SKILL.md`: §7 (Error and log messages); §5 (an apostrophe inside a format pattern)

## Checks

1. **One sentence** (`one_sentence`). No `Use 0 to fetch all rows` and no `the fetch size is unchanged`.
2. **Short** (`at_most_12_words`).
3. **The placeholder stays** (`placeholder_kept`).
4. **No apostrophe** (`no_apostrophe`). A single quote would turn `{0}` into a literal.

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort. The new arm ran on skill tree `0f6d7512`
(`<model>/skill-tree`), the baseline on `9d2eab7`.

| Run | One sentence (1) | Short (2) | Placeholder (3) | No apostrophe (4) |
| --- | --- | --- | --- | --- |
| Opus r1, r2 | passes | passes (9, 12 words) | passes | passes |
| Sonnet r1, r2 | passes | passes (12, 9 words) | passes | passes |
| Opus baseline r1, r2 | fails: an action, r2 also a consequence | fails (18, 23 words) | passes | passes |
| Sonnet baseline r1, r2 | fails: r1 a consequence, r2 an action | fails (20, 18 words) | passes | passes |

A draft of 2.2.0 used `fetchSize must be >= 0, got -1` as the module's example, and every run copied it; the example
now validates a port, so these results do not rest on a copy.
