# Case: a library rejecting a negative argument

The input is `HttpClientBuilder.connectTimeout(long millis)` rejecting `millis < 0` with an `IllegalArgumentException`.
The fix is to pass a non-negative value, which a message naming the parameter and the value already says, and the call
stops at the exception. The case is the negative control for the subsection on what a message on the caller's channel
carries: before 1.2.0 its rows had no condition, and every run added why the check exists and a way out.

## Skill parts

- `SKILL.md`: §2 (What a message on the caller's channel carries)
- `english-developer-style`: §7 (Error and log messages)

## Checks

1. **Names the parameter and the value** (`names_parameter_and_value`): `connectTimeout` and `millis` in the expression.
1. **One sentence** (`one_sentence`). No clause on why the check exists, no remedy beyond the valid range, and no
   consequence such as `the builder is unchanged`. A clause that says what `0` means describes the valid range and
   passes; `check.py` counts it as a second sentence, so grade this check by reading.
1. **Short** (`message_at_most_15_words`), counting the words in the string literals.

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort. The new arm ran on skill tree `f3764558`
(`<model>/skill-tree`), the baseline on `9d2eab7`.

| Run | Names (1) | One sentence (2) | Short (3) |
| --- | --- | --- | --- |
| Opus r1, r2 | passes | passes; r1 adds `; 0 means no timeout`, r2 puts `0 (no timeout)` in the range | passes (13, 13 words) |
| Sonnet r1, r2 | passes | passes; r1 puts `0 (no timeout)` in the range, r2 adds `(0 means no timeout)` | passes (10, 12 words) |
| Opus baseline r1, r2 | passes | fails: why (`a negative value has no meaning`) and an example value (`such as 10000`) | fails (43, 44 words) |
| Sonnet baseline r1, r2 | passes | fails: why, and the consequence `The builder keeps its previous connect timeout` | fails (39, 43 words) |

On a draft of 1.2.0 whose opening sentence did not name the accepted values, all four runs appended a clause on `0`
(`; use 0 for no timeout`); with the values named, two of four fold `0` into the range.
