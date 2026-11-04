# Case: review pgjdbc/pgjdbc#3968, a change that later turned out to break multi-host connect timeouts

A missed-defect case for `adversarial-code-review`. The input is [pgjdbc/pgjdbc#3968][pr] at `40cc9392`, two commits on
top of `e78c293f`. The pull request was merged without a review. Seven months later, [issue #4514][issue] reported a
defect the change had introduced, and [pull request #4515][fix], still open, proposes a fix. The gold answer therefore
comes from a user's report, not from a reviewer or an agent.

The change makes `connectTimeout` a deadline for the whole connection attempt, so that the non-SSL fallback after an
SSL timeout does not get a fresh `connectTimeout` of its own. `openConnectionImpl` reads the start time once, before the
loop over the hosts of a multi-host URL. When the first host is unreachable and uses up the timeout, the next host is
given what is left, down to the 1 ms floor of `remainingConnectTimeout`. A reachable second host then fails as well.

The prompt names neither the pull request nor the issue. The issue was filed in November 2026, after the June 2026
training cutoff of Claude Opus 5.5, but the pull request is older, and a model that recognized it could look for its
follow-ups.

[pr]: https://github.com/pgjdbc/pgjdbc/pull/3968
[issue]: https://github.com/pgjdbc/pgjdbc/issues/4514
[fix]: https://github.com/pgjdbc/pgjdbc/pull/4515

## What it exercises

The paragraph on limits in area *Reliability, operability, and observability*: the limit the change sets on one
connection attempt sits inside the loop over hosts, and the time the earlier hosts spend is taken from its budget.

## Checks

Grade by reading `result.md`; the grep only finds the candidates. A finding passes as `blocking` or `non-blocking`; a
defect named only in a question under *Needed to complete the review* is partial.

1. **One deadline shared by every host.** Pass: a finding that the start time (`startNanos`) is taken once in
   `openConnectionImpl`, before the loop over the hosts, so with a multi-host URL a host tried after a slow or
   unreachable one gets only the rest of `connectTimeout`, down to 1 ms. Partial: the report says the deadline spans
   the SSL fallback and the retries but does not name the hosts. Fail: neither.
   `grep -niE 'host|startNanos|remainingConnectTimeout' result.md`

## Skill parts

- `adversarial-code-review`: `SKILL.md` §Review areas, area *Reliability, operability, and observability*, the
  paragraph on the other limits on the same work

## Files

| File | What it is |
| --- | --- |
| `repo`, `base`, `head` | The repository, `e78c293fcdc6ccacdf37190bd9ed297891437ab5` (the parent of the pull request's first commit), and `40cc939247af2cbacb61ee9e49cf48cabbe646e3` (the pull request's last commit). |
| `prompt.md` | The task, with `<skills>`, `<base>`, and `<head>` replaced by `run-review-case.sh`. |

## How to run

From the repository root, once per model and run:

```bash
research/adversarial-code-review/cases/run-review-case.sh research/adversarial-code-review/cases/pgjdbc-3968-shared-connect-timeout <model> <label> <rev>
```
