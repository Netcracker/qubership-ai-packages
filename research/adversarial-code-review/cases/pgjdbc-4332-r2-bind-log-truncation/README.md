# Case: review pgjdbc/pgjdbc#4332 at 925a4385, a log-length limit that cuts mid-value and tests that miss it

A review-finding case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#4332][pr] at `925a4385`, four commits
on top of `87474525`, one of them a merge from the main branch. The gold answer comes from the reviewer's inline
comments on that commit, the second round of review: 17 comments, of which the author replied in the thread or changed
the code near eight, and this case keeps seven of those eight. The review was written in 2026, and reviews from 2025 on
may be agent-assisted. Findings from the first round are not given to the model; an earlier finding that is still
unfixed at `925a4385` and is reported again is not counted against the run.

The change adds the connection property `maxLogMessageLength` and makes the FINEST `FE=> Bind(...)` trace respect it, so
that a statement with many or large parameters cannot allocate an unbounded string while logging. `BindLog.format`
appends each parameter as `,$i=<value>,type=NAME`, picks a placeholder or a cut prefix when a value does not fit, and
ends with `LogMessageUtils.truncate`. The diff adds 723 lines and removes 10. The first round asked for a truncation
marker whenever a parameter is left out and for a prefix of a long string; this round shows that the reworked loop still
appends past the limit and lets the final `truncate` cut wherever it lands, that the size estimate is wrong in the
opposite direction, and that the new tests assert too little to notice either.

The prompt names neither the pull request nor its issue.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/4332

## What it exercises

- Area *Correctness and data integrity*, boundary and limit values: the line at a limit one character below its full
  length, a cut inside a run of doubled quotes, a size estimate that disagrees with what `quoteAndCast` writes.
- Area *Verification and documentation*: tests that would pass on an incorrect implementation, a test whose setup never
  reaches the branch it is named after, and missing boundary cases of `LogMessageUtils.appendBounded`.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial. Line numbers are at `925a4385`.

1. **The final `truncate` cuts the line mid-parameter.** Pass: a finding that `BindLog.format` appends a value and its
   `>,type=…` without reserving room for them, so the closing `LogMessageUtils.truncate` (`BindLog.java` line 131) cuts
   the line inside `,$i=<`, inside a value, or inside `>,type=…`, and can drop the clean `...` ending that
   `appendQuotedStringPrefix` built (a lone high surrogate, or a cut after `'ab'` that looks like a complete value); or
   that a line exactly one character too long loses its closing `)` and gets no marker, because the `)` is appended only
   when `sbuf.length() < maxLogMessageLength` (lines 128-130) and `truncate` then has nothing to cut. Partial: the
   report says the trace can exceed or be cut at the limit without naming where the cut lands or what it loses. Fail:
   neither.
   `grep -niE 'truncate|mid-value|>,type|closing|surrogate|dangling|reserve' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4332#discussion_r4267444373))
2. **The string size estimate counts a cast that is never written.** Pass: a finding that the check at `BindLog.java`
   lines 93-97 adds `castExtra` for every type name, but `SimpleParameterList.toString` passes no cast to `quoteAndCast`
   for `VARCHAR` or `TEXT` (its `switch` falls to `type = null`), and assumes every character doubles, so a string whose
   literal fits is shown cut with `...`. Partial: the report says the estimate is approximate or pessimistic without
   saying that values which fit are cut. Fail: neither.
   `grep -niE 'castExtra|estimat|::varchar|VARCHAR|quoteAndCast|overestimat|over-count' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4332#discussion_r4267444384))
3. **The prefix cut splits an escaped pair.** Pass: a finding that `LogMessageUtils.appendQuotedStringPrefix` (lines
   152-162) checks only the two characters around the cut, so in a run of quotes it can end after the first quote of a
   doubled pair (for example `''''` gives `(''...`), and a doubled backslash under `standard_conforming_strings=off` is
   not checked at all. The parameter `type` being unused and the empty `if` at lines 138-143 are supporting detail, not
   enough alone. Partial: the report names only the unused `type` parameter or the empty `if`. Fail: neither.
   `grep -niE "appendQuotedStringPrefix|doubled|quote|backslash|escape|type.*unused|empty" result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4332#discussion_r4267444389))
4. **The dangling-prefix test never reaches its branch.** Pass: a finding that
   `budgetExhaustionDoesNotLeaveDanglingParameterPrefix` (`BindLogTest.java` line 139), at `maxLen = 80`, cuts the first
   value and stops the loop at the `sbuf.length() >= maxLogMessageLength` check (`BindLog.java` line 43), so the
   `remainingForPrefix <= prefix.length()` branch at lines 49-55 is never run, and that its assertions accept `,$2` or
   `,$2=` endings and a marker anywhere in the line. Partial: the report says this test is weak without saying it misses
   the branch. Fail: neither.
   `grep -niE 'budgetExhaustion|dangling|remainingForPrefix|maxLen = 80|80' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4332#discussion_r4267444397))
5. **Fragment assertions where the whole line is known.** Pass: a finding that `smallBindIsNotTruncated` (line 43) or
   `unlimitedKeepsFullDump` (line 178) checks only `startsWith`, `contains("$1=<")`, and `endsWith(")")`, so it passes
   when `,type=…` is dropped or every `$i` shows the wrong value, where an `assertEquals` on the full expected line
   would not; or that `contains("...")` at line 87 and `endsWith(...) || contains(...)` at lines 152-153 and 166-167
   accept a marker anywhere. Partial: the report asks for stronger assertions in `BindLogTest` without naming a test or
   what the current assertions miss. Fail: neither.
   `grep -niE 'smallBindIsNotTruncated|unlimitedKeepsFullDump|assertEquals|contains\(|exact|whole line' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4332#discussion_r4267444406))
6. **The unknown-type test cannot detect materialization.** Pass: a finding that in
   `unknownValueTypeIsNotFullyMaterialized` (line 106) `assertFalse(log.contains(huge))` cannot fail, because the line
   above already limits the log to 256 characters, so a formatter that calls `toString` on the 500000-character value,
   or builds the whole literal, and then discards it still passes; the same holds at line 85 of
   `hugeSingleValueKeepsReadablePrefix`. Partial: the report says the test does not prove the value is not rendered,
   without the reason. Fail: neither.
   `grep -niE 'unknownValueType|materializ|toString|unestimated|hugeSingleValue' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4332#discussion_r4267444415))
7. **`appendBounded` boundaries are untested.** Pass: a finding that `LogMessageUtilsTest` has no case for a value that
   exactly fills the room left, for room shorter than `TRUNCATION_SUFFIX`, or for no room at all, the branches at
   `LogMessageUtils.java` lines 71-80 that `BindLog.format` reaches when the limit is almost used up. Naming one of the
   three passes. Partial: the report says `LogMessageUtils` needs more tests without naming a boundary. Fail: neither.
   `grep -niE 'appendBounded|exact(ly)? fit|TRUNCATION_SUFFIX|no room|boundar' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/4332#discussion_r4267444430))

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity*, boundary and limit values
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation*, tests that would catch an
  incorrect implementation

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `874745258455be18708d91a24cc98a0ae5ae85a3` (the main-branch commit the pull request last merged, so that `base..head` lists only its own commits), and `925a438557e6fc64cb330ff814b397e1dd303161` (the commit the second round reviewed). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-4332-r2-bind-log-truncation <model> <label> <rev>
```
