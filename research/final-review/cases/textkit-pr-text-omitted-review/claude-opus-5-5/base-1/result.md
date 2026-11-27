The change has one blocking problem: the `textkit-pages` command the commit message promises can't be run at all. Two smaller problems in `page_range` follow from the same gap, and none of the new code has a single test.

`comment-drift.py` only parses Java, Kotlin, Groovy and Scala. It printed nothing for this Python change, so I listed the changed members by hand from `git diff HEAD` and the untracked file:
- `paginate.page_range(number, per_page)` at `src/textkit/paginate.py:27`: comment-added.
- The `cli` module docstring at `src/textkit/cli.py:1`: comment-added.
- `cli.main(argv)` at `src/textkit/cli.py:8`: comment-added.

There was no task statement, so item 2 works from the commit message and the PR title and description. The test file has no class comments.

### Item 1: comments consistent with the code and with each other

**1a. Substantive. `src/textkit/paginate.py:28`, first sentence of `page_range`.** It says the function returns "the indexes of the first and the last item on page `number`". That is false for a partial last page and for a page past the end. The function never sees the item count, so `page_range(3, 5)` returns `(10, 14)` whether there are 15 items or 11.
- With 11 items, which is the PR's own example, item 14 doesn't exist and the last item is 10.
- A reader would use the second index as an inclusive bound and read past the end.
- The sibling `page()` docstring (`paginate.py:19-21`) states its past-the-end behavior; this one doesn't.
- **Request:** either take `total` and clamp the last index to `total - 1`, saying what a page past the end returns, or rewrite the sentence to describe the actual result. For example: "Return the index of the first item on page `number` and the index `per_page - 1` after it; the second index can lie past the last item of the sequence."

**1b. Substantive. `src/textkit/paginate.py:30`, the Raises sentence.** It says `page_range` raises `ValueError` only when `number` is less than 1. `per_page` is never checked:
- `page_range(1, 0)` returns `(0, -1)`.
- `page_range(1, -5)` returns `(0, -6)`.

`page_count` in the same file rejects `per_page < 1` (`paginate.py:7,9-10`). A reader who sees both docstrings concludes `page_range` accepts any `per_page`. **Request:** add the same `per_page < 1` check with the same error text as `page_count`, and list it in the Raises sentence.

**1c. Substantive. `src/textkit/cli.py:1` and `:9`.** Both docstrings call the module "the `textkit-pages` command". No command by that name exists:
- `pyproject.toml` has no `[project.scripts]` entry.
- Nothing calls `main()`: the module has no `if __name__ == "__main__"` block, so `python -m textkit.cli` does nothing.
- The value `main` returns (0) never reaches an exit status.

**Request:** add `[project.scripts] textkit-pages = "textkit.cli:main"` to `pyproject.toml`. That entry point passes `main()`'s return value to `sys.exit`, so the 0 becomes the exit status. Alternatively, stop calling the module a command.

**Terms:**
- The change adds "indexes". The field defines this word (sequence indexes), so it isn't a coinage.
- "count of items" (`cli.py:1`) is ordinary English and matches the `total` parameter.
- The change coins no terms.
- No comment narrates the change.

### Item 2: claimed cases covered

Cases claimed by the commit message, each with the test that covers it:

| Claimed case | Test |
| --- | --- |
| `page_range(number, per_page)` returns the first and last index of a page | none |
| `page_range` raises `ValueError` for `number < 1` (claimed in the docstring) | none |
| `textkit-pages` prints `page_count()` for two integers | none |

`tests/test_paginate.py` doesn't import `page_range`, and no test imports `textkit.cli`.
- **Request:** add `test_page_range_*` cases next to the `page` tests: one full page, the partial last page, `number=0`, and `per_page=0` once 1b is fixed.
- **Request:** add a `main([...])` test using `capsys`, for example `main(["11", "5"])` printing `3`.

**Command lines:**
- `textkit-pages <total> <per_page>`, promised to print the page count. No script, target or CI job runs it, because the command isn't installed (see 1c). Whether the console script exists depends only on the packaging configuration, and right now no version of pip or any other installer would create it. This is **substantive**. **Request:** add the entry point and run `textkit-pages 11 5` after `pip install -e .`, expecting `3`.

**Reading the claims the other way:**
- Every hunk is claimed by the commit message, and no versions or dependencies move.
- **Taste:** the PR title and description still describe only the `page_count` fix. After this commit the PR also adds a public function and a CLI. Either update the description or put this commit in its own PR.

### Item 3: boundaries, partitions, and the negative control

There are no tests, so no boundaries are covered. The suite misses everything, not just one corner. Owed:

`page_range`:
- `number=1`, the minimum.
- `number=0`, just outside it.
- `per_page=1`.
- `per_page=0`, which is invalid on its own.
- A partial last page.
- A page past the end.

`main`:
- Wrong argument count (zero, one, three arguments), which currently surfaces as an unpacking `ValueError` traceback.
- A non-integer argument, which raises a bare `int()` `ValueError`.
- `per_page=0`, which passes `page_count`'s `ValueError` through as a traceback.

What the command should do for each error case (a usage message and a non-zero exit, or a traceback) is undecided. Either way it needs one test per case.

No persisted state is replaced and no limit is moved, so those parts of the item don't apply.

### Item 3a: level, placement, and the environment

Both behaviors can be observed in one process: `page_range` directly, and `main(argv)` through `capsys`. Small tests in `tests/test_paginate.py`, next to the `page` tests, are owed. The CLI test can go in a new `tests/test_cli.py`, since no existing CLI tests share a fixture with it. No optional services are involved.

### Item 4: names by content, not by position

Nothing to report. The new names (`page_range`, `main`) and the docstrings refer to things by content.

### Item 5: the failure report

Nothing to report: the change adds no assertions. The existing tests use pytest's plain `assert ==`, which prints both operands.

### Item 6: what the writer says it verified

The change states no evidence that its tests can fail, either a red run on the base or a mutation verdict. It also adds no tests that could fail.

### Item 7: siblings of the change

- `page_range` repeats the `number < 1` check and the `start` arithmetic of `page()` (`paginate.py:21-23`). That's consistent with `page()`, and no defect carries over. `page()` doesn't check `per_page` either: `page(items, 1, 0)` returns `[]`. That predates this change; name it as a follow-up alongside 1b.
- **Substantive. `README.md:21-27`.** The Usage section lists `page_count` and `page` but not the new `page_range`, and the README doesn't document the command. **Request:** add `page_range(2, 5)` to the Usage block, plus a line on `textkit-pages` once it is installable.
- `pyproject.toml` has no scripts table for the new command to join. That gap is the finding in 1c.

### Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The `page_range` docstring promises the last item's index; a partial last page and a page past the end get an index past the last item | Substantive | `src/textkit/paginate.py:28` | 1 |
| `page_range` doesn't reject `per_page < 1`, unlike `page_count`; the Raises sentence lists only `number` | Substantive | `src/textkit/paginate.py:30` | 1 |
| `textkit-pages` isn't installed: no `[project.scripts]` entry, no `__main__` block | Substantive | `src/textkit/cli.py:1`, `pyproject.toml` | 1, 2 |
| `page_range` has no tests | Substantive | `tests/test_paginate.py` | 2, 3 |
| `textkit-pages` / `main` has no tests, and the documented command has never been run | Substantive | `src/textkit/cli.py:8` | 2, 3 |
| No boundary or invalid-input cases for `page_range` or the CLI's arguments | Substantive | `src/textkit/paginate.py:27`, `src/textkit/cli.py:11` | 3 |
| No red run or mutation verdict stated | Substantive | (change) | 6 |
| The README's Usage section omits `page_range` and the command | Substantive | `README.md:21-27` | 7 |
| The PR title and description cover only the `page_count` fix | Taste | (PR description) | 2 |
