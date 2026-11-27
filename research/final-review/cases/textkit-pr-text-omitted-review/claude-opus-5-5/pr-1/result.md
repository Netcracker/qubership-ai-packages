# Final review: `page_range()` and the `textkit-pages` command

**How the inputs were read.** There was no task statement, so the claimed cases come only from the commit message. The diff was read against `HEAD` (5c64077), together with the untracked `src/textkit/cli.py`. For the pull request I used the saved `gh/pr-view.json`: the PR is open, its title is "Count a partial last page in page_count()", and its base is `main`. With no network, the fetch could not run, so the PR target is the remote-tracking ref `origin/main` at 669de41, which matches the PR's `baseRefOid`. `git merge-base origin/main HEAD` is 669de41, so once this change is pushed the PR will show 669de41 → working tree. The drift script printed nothing, because it only parses Java, Kotlin, Groovy and Scala; I found the members by hand: `page_range` (comment added), `cli` module (comment added) and `cli.main` (comment added).

## Item 1: comments consistent with the code and with each other

**1a. The `page_range` docstring gives a false range for a partial or past-the-end page** (`src/textkit/paginate.py:28`). It says the function returns "the indexes of the first and the last item on page `number`". But `page_range` never sees the item count, so it returns `start + per_page - 1` every time.
- With 11 items at 5 per page, the page 3 this repo's own PR fixes, it returns `(10, 14)`. The page holds only index 10.
- A page past the end returns indexes that hold no item at all.
- The sibling `page()` docstring (`:19`) documents its past-the-end outcome; this one does not.

A reader would use 14 as a valid index. **Request:** either take `total` and clamp the last index (and say what an empty page returns), or reword the docstring to say the range is the slots page `number` would hold if full, and that the last index can lie past the end of the sequence. *Substantive.*

**1b. The `Raises` list does not match the other comment in the same file** (`src/textkit/paginate.py:30`). `page_count`'s docstring (`:7`) treats `per_page < 1` as invalid. `page_range` does not check `per_page`: `page_range(1, 0)` returns `(0, -1)`, and `page_range(2, -3)` returns `(-3, -7)`. Its docstring lists only the `number` check, so a reader of the file gets two different contracts for the same parameter. **Request:** reject `per_page < 1` with the same message `page_count` uses, and add that to the `Raises` sentence. *Substantive.*

Other checks found nothing:
- There are no added inline comments and no comments that narrate the change.
- No added sentence has an over-compressed shape (`english-developer-style` §4).
- Terms: "indexes" is the ordinary Python word for a position in a sequence (§4a, the field's word), and "counting pages from 1" reuses `page()`'s wording. Nothing is coined.
- `cli.main`'s docstring is true of its body.

## Item 2: claimed cases covered

Claims taken from the commit message only, since there was no task statement:

| Claimed case | Test |
| --- | --- |
| `page_range` returns the first and last index of a page | none |
| `page_range` raises `ValueError` for `number < 1` (the docstring's claim) | none |
| `textkit-pages` prints `page_count()` for its two integers | none |

**2a. Nothing that this change adds has a test.** `tests/test_paginate.py` is unchanged and still imports only `page` and `page_count` (`tests/test_paginate.py:3`). **Request:** tests for the claimed `page_range` outcome and its error, and an in-process test that calls `main([...])` and captures stdout (`test-authoring` §3). *Substantive.*

**2b. The `textkit-pages` command cannot be run.**
- The command line it promises is `textkit-pages <total> <per_page>`, printing `page_count(total, per_page)`.
- No script, build target or CI job runs it.
- `pyproject.toml` has no `[project.scripts]` entry, so installing the package creates no `textkit-pages` executable.
- `cli.py` has no `if __name__ == "__main__":` guard, so `python -m textkit.cli 11 5` prints nothing.

The command the commit message claims does not exist in any form. **Request:** add `[project.scripts] textkit-pages = "textkit.cli:main"` (wrapping the call in `sys.exit(main())` if the exit code matters), and show a run of the installed command. *Substantive.*

**2c. The PR title and description will no longer describe the diff** (PR title and body). The PR's diff (669de41 → working tree) will contain the `page_count` fix plus `page_range` and the new CLI module. The title and body mention only the `page_count` fix, so the `page_range` hunk (`paginate.py:27-35`) and the new `src/textkit/cli.py` are claimed by no sentence of the PR. **Request:** either put this change on its own branch and PR, or retitle the PR (for example "Count a partial last page in page_count(); add page_range() and textkit-pages") and add a sentence to the description for each addition. *Substantive.*

Reading the claims the other way over the commit itself: every hunk is claimed by the commit message, so there is nothing more here.

## Item 3: boundaries, partitions, and the negative control

**3a. No boundaries or invalid inputs are tested.** Nothing tests these values:
- `page_range`: `number = 1` (the boundary), `number = 0` (just outside it), `per_page = 0` or negative (see 1b), and the partial last page (see 1a).
- The CLI, invalid inputs:
  - the wrong number of arguments: zero or three arguments raise an unpacking `ValueError` with a traceback;
  - a non-integer argument raises a traceback from `int()`;
  - `per_page = 0` raises a traceback from `page_count`.

**Request:** tests for each of these, plus a decision on whether the CLI should print a usage message and exit non-zero instead of crashing with a traceback (`test-authoring` §4). *Substantive.*

No pre-existing state, pass-through setting, replaced mechanism or limit is involved.

## Item 3a: level, placement, and the environment

none. All of the new behavior can be seen in one process. The tests 2a asks for belong in `tests/test_paginate.py` for `page_range`, and in a new `tests/test_cli.py` that calls `main(argv)` for the CLI, which needs no subprocess. Nothing optional has to be skipped.

## Item 4: names by content, not by position

none. The new names (`page_range`, `main`, `textkit-pages`) and the docstrings refer to nothing by position or ordinal.

## Item 5: the failure report

none. There are no new assertions. The existing tests use plain pytest `assert ==`, which prints both operands.

## Item 6: what the writer says it verified

No evidence is stated, either a red run on the base commit or a mutation verdict, and there are no new tests that could supply it.

## Item 7: siblings of the change

**7a. `page()` has the same missing `per_page` check** (`src/textkit/paginate.py:16`). `page_range` copies the `number` check from `page()` and inherits its gap: `page(items, 1, 0)` silently returns `[]`. **Request:** fix `page()` in the same change as 1b, or name it as follow-up in the description. *Substantive.*

**7b. The README does not list the new members** (`README.md:20-23`). The Usage section lists the module's public functions (`page_count`, `page`) but neither `page_range` nor the `textkit-pages` command. **Request:** add a usage line for each. *Substantive.*

Call sites: `page_count(` is called from `cli.py:12` and the tests only. The CLI passes user input to it unchecked, which is covered in 3a.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The docstring's "last item on page" is false for a partial or past-the-end page | Substantive | `src/textkit/paginate.py:28` | 1 |
| `per_page < 1` is neither rejected nor listed under Raises, unlike `page_count` | Substantive | `src/textkit/paginate.py:30` | 1 |
| No test for `page_range` or the CLI | Substantive | `tests/test_paginate.py:3` | 2 |
| `textkit-pages` has no entry point and `cli.py` no `__main__` guard, so the command cannot be run | Substantive | `pyproject.toml:1`, `src/textkit/cli.py:8` | 2 |
| The PR title and description don't claim `page_range` or the CLI | Substantive | PR title and body | 2 |
| No boundary or invalid-input tests; the CLI crashes with a traceback on bad arguments | Substantive | `src/textkit/cli.py:11` | 3 |
| `page()` has the same missing `per_page` check | Substantive | `src/textkit/paginate.py:16` | 7 |
| README Usage leaves out `page_range` and `textkit-pages` | Substantive | `README.md:20` | 7 |

The drift script does not parse Python, so the drift tags were assigned by hand from the diff. The PR target tip could not be fetched without a network, so `origin/main` (669de41) was used in its place.
