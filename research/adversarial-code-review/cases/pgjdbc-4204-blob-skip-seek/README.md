# Case: review pgjdbc/pgjdbc#4204, a change that later turned out to make `BlobInputStream.skip` abort the transaction

A missed-defect case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#4204][pr] at `070636d8`, three commits
on top of `40b6b071`. The pull request was merged without a review. Two months later, [pull request #4361][fix], still
open, reported two defects the change had introduced and proposes a fix. The gold answer therefore comes from a later
report, not from a reviewer or an agent.

The change overrides `BlobInputStream.skip(long)` to seek with `lo_lseek` or `lo_lseek64` instead of reading and
discarding the bytes, as the inherited `InputStream.skip` did. It clamps the target only to the stream limit, which is
`Long.MAX_VALUE` unless the caller passed one. The server refuses a large object seek past its maximum size, so
`skip(Long.MAX_VALUE)` on an ordinary stream fails with `IOException`, and the failed fastpath call aborts the
transaction: every later statement fails with SQLState `25P02` until rollback. The test `skipPastMax` asserts exactly
that, as intended behavior. Separately, `skip` calls `seek64` for any target past `Integer.MAX_VALUE` without checking
`supports64BitOffsets()`, which the same change added and uses for `tell64`, so on a server older than 9.3 such a skip
fails with `The fastpath function lo_lseek64 is unknown.`. Before the change, both cases read to the end of the object
and returned the count of bytes skipped.

The prompt names neither the pull request nor the report. The pull request was merged on June 26, 2026, at the June 2026
training cutoff of Claude Opus 5.5, and the report was filed in August 2026, after it.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/4204
[fix]: https://github.com/pgjdbc/pgjdbc/pull/4361

## What it exercises

Area *Compatibility and evolution* together with area *Correctness and data integrity*: an override that replaces
inherited behavior must keep what callers of the old behavior relied on (`skip(Long.MAX_VALUE)` to skip to the end)
across the supported server versions, and its boundary inputs (the largest `n`, a target past the 32-bit range) must not
leave the connection unusable. The defect is visible in the diff, and a test in the diff asserts it.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **A large skip seeks past the server maximum and aborts the transaction.** Pass: a finding that `skip` clamps the
   target only to `limit` (`BlobInputStream.java` line 383), which is `Long.MAX_VALUE` without a caller limit (line
   430), so a large `n`, such as `skip(Long.MAX_VALUE)`, sends a seek the server refuses; the `IOException` comes with
   an aborted transaction, or the finding calls it a regression against the inherited `InputStream.skip`, which stopped
   at the end of the object. Partial: the report says a large skip throws, or questions the behavior `skipPastMax`
   asserts, but names neither the aborted transaction nor the regression. Fail: neither.
   `grep -niE 'skip|Long.MAX_VALUE|abort|25P02|skipPastMax|seek target' result.md`
2. **`lo_lseek64` on servers older than 9.3.** Pass: a finding that `skip` calls `lo.seek64` for a target past
   `Integer.MAX_VALUE` (line 397) without checking `supports64BitOffsets()`, so on a server older than 9.3 the skip
   fails where the old read-based skip stopped at the end of the object. Partial: the report notes that the pre-9.3
   path of `skip` is untested (`skipPastMax` runs only on 9.3 and later) without naming the `seek64` call. Fail:
   neither. `grep -niE '9\.3|seek64|lseek64|supports64BitOffsets|older server' result.md`

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Compatibility and evolution* (the *Baseline* and
  *Contracts* bullets)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity* (limit values, boundary
  paths)
- `adversarial-code-review`: `SKILL.md` §Review areas, area *Verification and documentation* (a test that asserts the
  defect)

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `40b6b0718410c09ef6316d9c66dfa490d9126d8e` (the parent of the pull request's first commit), and `070636d8653a912265d9d403d959eb659cfecc45` (the pull request's last commit). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-4204-blob-skip-seek <model> <label> <rev>
```
