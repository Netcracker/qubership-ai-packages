Run `final-review` over this change. It is not yet committed as final, so please review it as it stands.

**Task statement**

On branch `fix/page-count-stale`, the user first asked me to do two things:
1. Fix the off-by-one in `page_count()`.
2. Make `page()` reject a `per_page` below 1.

I committed both, pushed the branch, and opened PR #12 into `main`: https://github.com/example/textkit/pull/12

The user then said: "The report renderer calls `page(rows, 1, 0)` for a report with no rows, so take the `per_page` check out of `page()` again and keep the `page_count()` fix."

I did that in the commit at `HEAD`, 7f2560c, "Drop the per_page check from page()". That commit is the change to review, and it is about to be final. Check whether it does what the user asked and nothing else:
- `page()` no longer raises on `per_page` below 1, and `page(items, 1, 0)` behaves as it did before the check was added.
- The `page_count()` fix is intact.
- Tests and comments match the final behavior. In particular, look for a leftover test or comment that still expects `page()` to raise, or that is now wrong.
- `page_count()` still raises on a `per_page` below 1. The user did not ask to change that.

**Diff range**

The diff starts at the merge base of the tip of `main` and the commit I will push, `HEAD` (7f2560c). Get it with `git merge-base main HEAD` (or `origin/main` if `main` is stale locally). Then review `git diff <merge-base>..HEAD`.

The branch history contains these commits: 669de41 "add page_count and page", 5c64077 "Count a partial last page in page_count()", 58d2c74 "Reject a per_page below 1 in page()", and 7f2560c "Drop the per_page check from page()". The net diff against the merge base should therefore contain only the `page_count()` fix, with no `per_page` check in `page()`.

**PR title, as it stands**

Count a partial last page in page_count() and reject a per_page below 1 in page()

**PR description (`pr.md`), as it stands**

`page_count(11, 5)` returned 2, so the eleventh item was on no page: the integer division dropped the remainder. It now rounds the quotient up and returns 3.

`page(items, 1, 0)` returned an empty list for every page number, so a caller that passed 0 by mistake rendered an empty report with no error. It now raises `ValueError: per_page must be at least 1, got 0`, as `page_count()` already does.

**Known concern to check**

The PR title and description were written before the last commit. They still say `page()` now raises `ValueError` for a `per_page` below 1, which the final diff no longer does. Say whether they are stale against the net diff and what they should say instead. The PR text has not been updated yet, and the review should not edit it.

Report substantive findings only. Do not change any file and do not commit.
