# Case: review pgjdbc/pgjdbc#3905, a change that later turned out to make `LargeObject.close()` lose buffered output

A missed-defect case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#3905][pr] at `ec7ce5e9`, two commits on
top of `e3ea9a3b`. Its review has five inline comments, about the lock and the nesting in `close()`, and none of them
names the defect below; the suggestion to return early and set `closed = true` first came from that review. Four months
later, [issue #4247][issue] reported the defect, and [pull request #4248][fix] fixed it. The gold answer therefore comes
from a user's report, not from a reviewer or an agent.

The change adds `checkClosed()` to every operation of `LargeObject`, `write` included, and moves `closed = true` in
`close()` ahead of the flush of the output stream. `close()` then calls `os.flush()`, `BlobOutputStream.flush()` calls
`lo.write(...)` for the buffered bytes, and `checkClosed()` throws `This large object has been closed.`. Bytes written
through `getOutputStream()` and not yet flushed are lost, `close()` throws, and `lo_close` is never sent.

The prompt names neither the pull request nor the issue. The pull request was merged in February 2026 and the issue was
filed on June 24, 2026, both before the June 2026 training cutoff of Claude Opus 5.5, so a model that recognized the
change could know of the report.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/3905
[issue]: https://github.com/pgjdbc/pgjdbc/issues/4247
[fix]: https://github.com/pgjdbc/pgjdbc/pull/4248

## What it exercises

Area *Correctness and data integrity*: the paths through state transitions and cleanup. The new guard and the new order
of `close()` are each correct alone; the defect shows only when the reviewer follows `close()` into
`BlobOutputStream.flush()` and back into the guarded `write`.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **Close marks the object closed before it flushes.** Pass: a finding that `LargeObject.close()` sets `closed = true`
   (`LargeObject.java` line 169) before `os.flush()` (line 174), so the flush reaches `LargeObject.write`, whose new
   `checkClosed()` throws; buffered output from `getOutputStream()` is lost and `close()` fails. Partial: the report
   says the order of `closed = true` and the flush in `close()` is risky, or that the flush can fail, without naming
   the `checkClosed()` in `write` that makes it fail every time. Fail: neither.
   `grep -niE 'flush|checkClosed|closed = true|BlobOutputStream' result.md`

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Correctness and data integrity* (state transitions,
  cleanup, data loss)

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `e3ea9a3bfce6330aea67b3ff555cd7c32a755134` (the parent of the pull request's first commit), and `ec7ce5e9f3bc3f09c4a1c53abb7ad3d5282ae539` (the pull request's last commit). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-3905-close-before-flush <model> <label> <rev>
```
