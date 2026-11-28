# Review: Shorten the retry warning

Result: REQUEST_CHANGES (2 major, 1 minor, 0 nit)
Revision: 8587e4889ee71695aa734e9355ead5e8d75b64a0...4578588101d4a5af2876d0940d0bdad9252d621b
Held until the code is settled: 1 finding (F2, in the ledger)

## Main problems

1. **The reworded warning keeps clauses that the check can't back (major).** The rewrite shortened the old sentence one clause at a time. It kept a consequence clause and a remedy, and those keep the warning too long to fix the wrapping. They also don't match what the check counts and what it accepts as a fix. This covers F1, F3 and F4.

## Findings

- **F1 major** `retrylint/messages.py:6-8`: the shorter warning still wraps over four lines in an 80-column terminal, the same as the old one. So the change doesn't remove the wrapping its commit body sets out to fix.
  - On `post_retry` the line went from 303 to 245 characters, and on `patch_retry` from 309 to 251. Both are 4 lines at 80 columns, before and after.
  - The commit body says the old warning took three lines; it took four.
  - The ledger has a checked rewrite that fits in 3 lines and also resolves F3 and F4.
- **F2 major** `retrylint/messages.py:6-7`: this one is about the commit message, not the code. It is held until the code is settled.
  - The commit body says the endpoint and the retry count sat in the middle of the warning and are now first. Both already came right after the `file:line` prefix, and they haven't moved.
  - The body doesn't mention the edits the commit actually makes: it drops the word `endpoint`, the quotation marks around `METHOD /path`, and the "such as creating a second resource" example.
- **F3 minor** `retrylint/messages.py:7`: "so a retry may apply its effect twice" makes the effect belong to the retry and caps it at two. An endpoint retried up to 3 times can have its request processed 4 times.
- **F4 minor, pre-existing** `retrylint/messages.py:8`: the warning suggests "send an Idempotency-Key header that the server deduplicates". A user who does that still gets the warning and exit status 1, because the check reads only the method and the retry count. It's older than this change, but the change rewrites the line, so it can be fixed here.
- **F7 nit, pre-existing** `retrylint/messages.py:6`: a retry count of 1 prints "retried up to 1 times".

## Older than this change

- **F5 minor, pre-existing** `retrylint/messages.py:7`: the warning cites RFC 9110, section 9.2.2 for every method outside the six it lists as idempotent. That includes PATCH (defined in RFC 5789), PROPFIND (which RFC 4918 defines as idempotent), and an unknown or mistyped method. Follow-up issue: not filed.
- **F6 minor, pre-existing** `tests/test_golden.py:13-20`, outside the diff: when a golden case fails, unittest hides both texts behind "Diff is 984 characters long. Set self.maxDiff to None to see it." Setting `maxDiff = None` on `GoldenTest` fixes it. Follow-up issue: not filed.

## Notes

- **Not run:**
  - Diff and mutation coverage were skipped: this Python repository has no coverage or mutation tool.
  - The comments, security, reliability, performance and formats checks didn't apply to this change, so they didn't run.
- **One decision changed:** the verifier left the result at the placeholder `approve`. I changed it to `request_changes` because F1 and F2 are major findings in this change.
- **F2's location:** it is about the commit message, but the verifier anchored it to the warning lines. I passed it through as written.
- **Workspace:** no file in the repository changed, nothing was published, and the extra worktrees made for the review are removed.

Files:
- `/Users/vlsi/.cache/adversarial-code-review/local-repo-45785881/round-1-45785881/review.json`
- `/Users/vlsi/.cache/adversarial-code-review/local-repo-45785881/round-1-45785881/ledger.md`
