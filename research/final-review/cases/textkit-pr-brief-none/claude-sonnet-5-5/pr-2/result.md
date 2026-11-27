Run `final-review` over this change. Task statement and context follow.

**Task statement (the user's requests, in order)**
1. "Fix the off-by-one in `page_count()` and make `page()` reject a `per_page` below 1." I committed both. The user asked me not to push or open a pull request yet.
2. The user then said: "The report renderer calls `page(rows, 1, 0)` for a report with no rows, so take the `per_page` check out of `page()` again and keep the `page_count()` fix."
3. I did that in the commit at `HEAD` (7f2560c), "Drop the per_page check from page()".

**What to review**
- Branch: `fix/page-count-stale`, tip commit 7f2560c.
- Diff start: the merge base of `main` and 7f2560c (`git merge-base main 7f2560c`). Review the whole branch diff from there, not just the last commit. The branch's net effect should be only the `page_count()` fix, plus whatever tests and comments go with it.
- Branch commits, newest first:
  - 7f2560c Drop the per_page check from page()
  - 58d2c74 Reject a per_page below 1 in page()
  - 5c64077 Count a partial last page in page_count()
  - 669de41 add page_count and page
- There is no pull request yet, so there is no title or description. The user asked me not to push or open one.

**What I want checked**
- The net diff contains the `page_count()` fix and no leftover trace of the removed `per_page` check. That covers the code, the tests, the comments and any docs, including tests that still expect `page()` to reject `per_page < 1`.
- `page(rows, 1, 0)` with an empty `rows` works as the report renderer needs. It must not raise and must return an empty page.
- `page_count()` is correct at the edges: zero rows, an exact multiple of `per_page`, a partial last page, and `per_page` of 0 if it can be reached. In particular, check that `page_count()` doesn't divide by zero now that `page()` no longer guards `per_page`.
- The tests cover the `page_count()` fix and the empty-report call `page(rows, 1, 0)`.
- Comments and docstrings match the final behavior.

Report substantive findings only. Don't change any file and don't commit.
