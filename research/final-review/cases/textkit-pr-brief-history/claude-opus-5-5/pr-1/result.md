Please run `final-review` on the change below. Review it before it becomes final.

**Task statement**

The user first asked for two things: fix the off-by-one in `page_count()`, and make `page()` reject a `per_page` below 1. Both were committed, pushed on branch `fix/page-count-stale`, and opened as a pull request into `main`. The user then said, in their words: "The report renderer calls `page(rows, 1, 0)` for a report with no rows, so take the `per_page` check out of `page()` again and keep the `page_count()` fix." The commit at `HEAD` does that.

**Repository:** `/private/var/folders/c1/c191w0fd7xb7947_1fnbyq080000gn/T/tmp.Sll9rzQLBi/repo`

**The change under review:** the commit at `HEAD`, `7f2560c36bbcc985a5b3b230a0dfa0e5ede55051` "Drop the per_page check from page()". It touches `src/textkit/paginate.py` and `tests/test_paginate.py`.

**Pull request:** https://github.com/example/textkit/pull/12, from `fix/page-count-stale` into `main`. Its title and description are below as they stand now. They were written before the `HEAD` commit and have not been edited since.

Title:

```text
Count a partial last page in page_count() and reject a per_page below 1 in page()
```

Description (`pr.md`):

```text
`page_count(11, 5)` returned 2, so the eleventh item was on no page: the integer division dropped the remainder. It now rounds the quotient up and returns 3.

`page(items, 1, 0)` returned an empty list for every page number, so a caller that passed 0 by mistake rendered an empty report with no error. It now raises `ValueError: per_page must be at least 1, got 0`, as `page_count()` already does.
```

**Diff range for the PR:** the diff runs from the merge base to `7f2560c36bbcc985a5b3b230a0dfa0e5ede55051` (the commit that will be pushed). There's no `main` ref or `origin` remote in this checkout, so I couldn't compute the merge base against the tip of `main`. The branch was built on `669de41a8a448f4c8ad18155519c5c1782c3d9b5` ("add page_count and page"), so use that as the merge base. If you can reach the tip of `main`, check it first. The commits in that range are:

- `5c64077` Count a partial last page in page_count()
- `58d2c74` Reject a per_page below 1 in page()
- `7f2560c` Drop the per_page check from page()

Review both the `HEAD` commit and the PR's net diff from the merge base, against the task statement. Also check the PR's title and description against that diff. Report substantive findings with file and line, and leave out style nits.
