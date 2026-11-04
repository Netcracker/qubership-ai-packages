# Case: review pgjdbc/pgjdbc#2829 at `9e39f461`, a copied-in cleaner whose units and API leak into the driver

A coverage case for `adversarial-code-review` on a change too large to read in one pass. The input is
[pgjdbc/pgjdbc#2829][pr] at `9e39f461`, 14 commits and 446 changed lines on top of `05b129fe`. The change replaces
`finalize()` in `PgConnection` and `StreamWrapper` with `LazyCleaner`, a phantom-reference cleaner copied into
`org.postgresql.util`, and starts one shared instance from `Driver`. The gold answer is the reviewer's inline comments
on that commit, the third review round: four comments, which this case counts as three checks because two of them are
about the same `null` cleaning action. The author replied in the thread or changed the code near each of them. The
review is from March 2023, before agent-assisted reviews.

Earlier rounds, by the same reviewer and another one, are not given to the model, so the run starts with no previous
findings. A finding from an earlier round that is still unfixed at `9e39f461` and that the model reports again is not
counted against the run. The prompt names neither the pull request nor its title.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/2829

## What it exercises

- *Correctness and data integrity*: a constructor argument whose unit the caller and the callee read differently.
- *Compatibility and evolution*: a new public method on the driver's public `Driver` class that exposes an internal
  helper.
- *Architecture and maintainability*: a nullable parameter on a public method that exists for one internal caller.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **The cleaner thread TTL is 10 milliseconds.** Pass: a finding that `Driver.java` line 71 creates
   `new LazyCleaner(10, "Cleaner")`, and `LazyCleaner` passes `threadTtl` to `ReferenceQueue.remove(long)` (line 122),
   which takes milliseconds; so the cleanup thread wakes every 10 ms while any object is registered, exits 10 ms after
   the last one is removed, and `add` starts a new thread for the next registration. A finding that names the
   millisecond unit and asks for a longer default passes without describing the thread's behavior, and so does a
   suggestion to take a `java.time.Duration` instead of a `long` when it also names the 10 ms value. Partial: the
   report says the TTL has no unit in its name or Javadoc, but not that 10 ms is far too short. Fail: neither.
   [Original comment][c4].
   `grep -niE 'ttl|threadTtl|millisecond|LazyCleaner\(10|Duration' result.md`
2. **`Driver.getCleanerInstance()` adds a public API for an internal helper.** Pass: a finding that the public
   `Driver.getCleanerInstance()` (line 802), added so that `PgConnection` and `StreamWrapper` reach the shared cleaner,
   puts an internal class on the public `java.sql.Driver` implementation, and that the default instance belongs in
   `LazyCleaner` itself (for example `LazyCleaner.getInstance()`), which also makes clear that `LazyCleaner` is
   internal to the driver. Partial: the report says only that `LazyCleaner` is public or that the shared instance
   should live elsewhere, without naming the new method on `Driver`. Fail: neither. [Original comment][c1].
   `grep -niE 'getCleanerInstance|getInstance|public API|Driver\.java' result.md`
3. **A `null` cleaning action has no purpose.** Pass: a finding that `LazyCleaner.register(Object, @Nullable
   CleaningAction)` (line 83) accepts `null`, and `Node.onClean` skips a `null` action (line 187), so a registration
   with no action is queued only to do nothing; the one caller that passes `null` is `setKeepThreadAlive` (lines 67-81),
   which no main code calls, and removing it or passing a no-op action would let `@Nullable` and the check go. Partial:
   the report questions the `@Nullable` parameter or the null check, but does not connect either to
   `setKeepThreadAlive` or to the action being pointless. Fail: neither. [Original comments][c2] and [the related
   one][c3].
   `grep -niE 'Nullable|null action|setKeepThreadAlive|keepAlive|register\(' result.md`

[c1]: https://github.com/pgjdbc/pgjdbc/pull/2829#discussion_r1126755069
[c2]: https://github.com/pgjdbc/pgjdbc/pull/2829#discussion_r1126772414
[c3]: https://github.com/pgjdbc/pgjdbc/pull/2829#discussion_r1126774539
[c4]: https://github.com/pgjdbc/pgjdbc/pull/2829#discussion_r1126788869

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity*, limit values (check 1)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Reliability, operability, and observability*, resource
  cleanup (check 1)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Compatibility and evolution*, bullet *Contracts* (check 2)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Architecture and maintainability*, ownership and explicit
  type boundaries (checks 2 and 3)
- `adversarial-code-review`: `SKILL.md` §Reassess previous findings, a later round with no previous findings given

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `05b129fedd866afc7fd41c6d8a266d231fbca1f4` (the parent of the pull request's first commit), and `9e39f4618a4d7f779e119f6a8bdf5fbfc35f34c0` (the commit the third review round was on). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-2829-r3-lazycleaner-phantom-refs <model> <label> <rev>
```
