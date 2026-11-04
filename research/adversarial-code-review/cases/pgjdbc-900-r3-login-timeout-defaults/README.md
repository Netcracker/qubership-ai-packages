# Case: review pgjdbc/pgjdbc#900 at ede2da18, a short change with a lost-defaults bug, an overflow, and empty tests

A review-finding case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#900][pr] at `ede2da18`, seven commits
on top of `fd86e660`. The gold answer comes from the maintainer's inline comments on that commit, the third round of
review: four comments, and the author replied in the thread or changed the code near each of them. On the two about the
tests the author disagreed, pointing at existing tests in the file that have no assertions either, and neither test
gained one by the last commit of the pull request. The review was written by hand in 2017. Findings from the two earlier
rounds are not given to the model; an earlier finding that is still unfixed at `ede2da18` and is reported again is not
counted against the run.

The change makes the driver fall back to `DriverManager.getLoginTimeout()` when the connection properties carry no
`loginTimeout`. To tell an absent property from a default one, `Driver.parseURL` now copies its `defaults` argument with
`putAll` instead of chaining it as the parent of a new `Properties`. `putAll` copies only the entries the object itself
holds, so the defaults chained behind it are dropped. The diff adds 63 lines and removes 10, and it carries a
compatibility defect, an arithmetic regression, and two tests that cannot fail.

The pull request was closed without being merged. The prompt names neither the pull request nor its issue.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/900

## What it exercises

- Area *Compatibility and evolution*, contracts and defaults: the change to `parseURL` drops the properties that callers
  pass through the parent chain of a `Properties` object, including `driverconfig.properties` and the `user.name`
  default.
- Area *Correctness and data integrity*, limit values: `DriverManager.getLoginTimeout() * 1000` is computed in `int`
  before the cast to `long`, where the old code cast first.
- Area *Verification and documentation*: two new tests have no assertion and would pass on an incorrect implementation.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **`putAll` drops the defaults chain.** Pass: a finding that `parseURL` (`Driver.java` lines 528-532) copies
   `defaults` with `putAll`, which ignores the parent `Properties`, so the defaults that `connect` chains in at line 220
   (`new Properties(defaults)`, from `getDefaultProperties()`) are lost when it calls `parseURL(url, props)` at line
   235; or that `getPropertyInfo` loses `info` the same way at lines 484-485. Partial: the report says the `parseURL`
   change alters which properties are visible but names neither the parent chain nor the lost defaults. Fail: neither.
   `grep -niE 'putAll|parent|defaults|chain|getDefaultProperties|driverconfig' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/900#discussion_r139321542))
2. **`int` overflow in the `DriverManager` timeout.** Pass: a finding that `timeout()` at `Driver.java` line 653
   computes `(long) (DriverManager.getLoginTimeout() * 1000)`, multiplying in `int` before the cast, so a login timeout
   above 2147483 seconds (about 25 days) overflows; the fix is `1000L` or a cast before the multiplication, as the
   removed line had it. Partial: the report flags the expression as fragile or asks about large values without naming
   the overflow. Fail: neither.
   `grep -niE 'overflow|1000L|getLoginTimeout|int ' result.md`
   ([original comment](https://github.com/pgjdbc/pgjdbc/pull/900#discussion_r139321580))
3. **Tests that cannot fail.** Pass: a finding that `testUseDriverManagerLoginTimout` and
   `testUseDriverManagerLoginTimout2` in `LoginTimeoutTest.java` (lines 94 and 107) only open and close a connection and
   assert nothing, so neither would fail if the `DriverManager` fallback or the override by `loginTimeout=0` were
   broken. Naming one of the two passes when the finding says the problem is the missing assertion. Partial: the report
   says the change is under-tested without naming these tests or the missing assertion. Fail: neither.
   `grep -niE 'LoginTimeoutTest|testUseDriverManager|assert' result.md`
   ([first comment](https://github.com/pgjdbc/pgjdbc/pull/900#discussion_r139321599),
   [second comment](https://github.com/pgjdbc/pgjdbc/pull/900#discussion_r139321606))

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Compatibility and evolution*, the **Contracts** bullet
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity*, limit values
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation*, tests that would catch an
  incorrect implementation

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `fd86e66007c4fa1fdefde29600f157b1cd5238a4` (the parent of the pull request's first commit), and `ede2da1898aee4e503e1041c133dbf95322fa4a8` (the commit the third round reviewed). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-900-r3-login-timeout-defaults <model> <label> <rev>
```
