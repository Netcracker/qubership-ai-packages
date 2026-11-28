Run `final-review` on the change below.

**Task statement (the user's words, in order)**

1. "Fix the off-by-one in `page_count()` and make `page()` reject a `per_page` below 1."
2. After those were committed, pushed, and opened as a PR: "The report renderer calls `page(rows, 1, 0)` for a report with no rows, so take the `per_page` check out of `page()` again and keep the `page_count()` fix."

**Repository and commits**

- Repo: `/private/var/folders/c1/c191w0fd7xb7947_1fnbyq080000gn/T/tmp.9xejaX7i89/repo`, branch `fix/page-count-stale`. The checkout is a detached HEAD at `7f2560c`.
- The commit to be pushed is `7f2560c36bbcc985a5b3b230a0dfa0e5ede55051`, "Drop the per_page check from page()".
- Branch commits on top of the base:
  - `5c64077` Count a partial last page in page_count()
  - `58d2c74` Reject a per_page below 1 in page()
  - `7f2560c` Drop the per_page check from page()
- Merge base with `main`: `669de41a8a448f4c8ad18155519c5c1782c3d9b5` ("add page_count and page"). I couldn't compute this with `git merge-base`. There's no local `main` ref and fetching from `origin` failed. It's inferred: it's the root commit and the branch's only commit before the fix. Review the diff `669de41..7f2560c`, and check the tip of `main` on GitHub if you can reach it.
- Files touched: `src/textkit/paginate.py` and `tests/test_paginate.py`.

**Pull request**

- https://github.com/example/textkit/pull/12, into `main`.
- The title and description below are as they stand on the PR now. They were written before the last commit and haven't been updated since.

Title:

> Count a partial last page in page_count() and reject a per_page below 1 in page()

Description (from `pr.md`, which is no longer in the working tree):

> `page_count(11, 5)` returned 2, so the eleventh item was on no page: the integer division dropped the remainder. It now rounds the quotient up and returns 3.
>
> `page(items, 1, 0)` returned an empty list for every page number, so a caller that passed 0 by mistake rendered an empty report with no error. It now raises `ValueError: per_page must be at least 1, got 0`, as `page_count()` already does.

**What to review**

Review the whole branch diff against the base, plus the PR title and description, against the task statement. Report substantive findings, including anything the change, its tests, its commit messages, or the PR text leave out or get wrong.
