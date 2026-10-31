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

Runs of 2026-10-31 on the skill at `9d2eab7` are under `<model>/baseline/`; the results of the skill these checks
test come with it.
