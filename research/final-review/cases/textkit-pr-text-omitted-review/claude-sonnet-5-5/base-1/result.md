# Final review: `page_range()` and the `textkit-pages` command

Skills loaded: `final-review`, `test-authoring` and `english-developer-style`, all from the given directory. No `pythondoc-authoring` skill was supplied, so item 1 applies the doc-comment questions from `final-review` and `english-developer-style`.

Inputs: the working tree and the untracked `src/textkit/cli.py` against `669de41`. The task statement is the commit message, the PR title and the PR description. The change owes no tests that I ran; I ran none, as instructed.

Drift script: it ran and printed nothing, because it parses only Java, Kotlin, Groovy and Scala files. I did the check by hand. The members that moved are `page_range` (comment added), `main` (comment added, new file) and the module docstring of `cli.py`. No existing member's code changed, so no `code-changed, comment-unchanged` rows exist.

No previous report exists.

## Item 1: Comments consistent with the code and with each other

**1a. `page_range` first sentence (`paginate.py:28`), substantive.** It says "the indexes of the first and the last item on page `number`". The function never sees the items or `total`. For a partial last page it returns an index that holds no item. `page_range(3, 5)` is `(10, 14)` for 11 items, but item 11 is the last one. Past the end it returns indexes of items that do not exist, where `page()` returns `[]`. A caller who slices or indexes with the upper bound would read past the sequence.
Request: say that the result is the 0-based, inclusive start and end indexes of a full page, as a tuple, and that the last index can lie past the end of a sequence with fewer items. The "counting pages from 1" tail can stay.

**1b. `page_range` "Raises" sentence (`paginate.py:30`), substantive.** It lists only `number < 1`. `per_page` is not checked, so `page_range(1, 0)` returns `(0, -1)` and a negative `per_page` returns a reversed range. The sibling `page_count` rejects `per_page < 1` and its docstring says so. Either validate `per_page` with the same message and list it, or state what an out-of-range `per_page` returns. See also item 3.

**1c. `cli.py:1`, substantive.** "The `textkit-pages` command" names a command that does not exist. `pyproject.toml` has no `[project.scripts]` entry, and `cli.py` has no `if __name__ == "__main__"` block. Nothing can run `textkit-pages`. Request: add the entry point `textkit-pages = "textkit.cli:main"`, or reword the docstring to say what the module is.

**1d. `main` docstring (`cli.py:9`), substantive.** The first sentence defines the function through another member's name: "Print `page_count(total, per_page)`". It also omits the following:
- The `argv` parameter.
- The return value 0.
- That a wrong argument count, a non-integer, or a value `page_count` rejects raises `ValueError`.

Request: "Print the number of pages that `total` items take at `per_page` to a page, and return 0." Then add one sentence on the exceptions.

Terms: none coined. "indexes", "first", "last" and "page" all have sources in the base. There is no narration of the change and no sentence needing a second parse.

## Item 2: Claimed cases covered

| Claim | Test |
| --- | --- |
| `page_range(number, per_page)` returns the first index | **none** |
| `page_range(number, per_page)` returns the last index | **none** |
| `page_range` raises for `number < 1` (docstring) | **none** |
| `textkit-pages` prints `page_count()` for two integers | **none** |

None of the four claims has a test. `tests/test_paginate.py` is unchanged and there is no `tests/test_cli.py`. This is a substantive finding. The request is the tests named under item 3.

**Commands the change tells someone to run:** `textkit-pages <total> <per_page>`, which prints the page count. No script, build target or CI job runs it. The outcome depends on a console-script entry point, which the configuration lacks. There is also no `python -m textkit.cli` form, since there is no `__main__` block and no `__main__.py`. As it stands, the command cannot run in any supported Python version. Substantive. The request is the entry point in `pyproject.toml` plus a run of the installed command (`textkit-pages 11 5` should print `3`), or the claim removed.

**Claims read the other way:** the PR title and description claim only the `page_count` rounding fix, which `test_page_count_counts_partial_last_page` covers. The diff from the given base also carries `page_range` and `cli.py`, which neither text claims. Only the commit message claims them. Substantive. The request is to update the PR title and description to claim the new function and the command, or to split them into their own change.

## Item 3: Boundaries, partitions, and the negative control

No test exists for either new member, so every partition below is missing. Substantive. Request, as tests:
- `page_range(1, 5) == (0, 4)`, the lower boundary.
- `page_range(2, 5) == (5, 9)`, a later page.
- `number=0` and `number=-1` each raise `ValueError`, with 1 as the neighbor that does not. These invalid cases are tested alone, and `number=0` is the boundary.
- `per_page=1`, where the first and last index are equal.
- The behaviour for `per_page=0`, per 1b.
- For `main`: `["11", "5"]` prints `3`, and `["0", "5"]` prints `0`. Failure inputs: `per_page` 0, one argument, three arguments, and a non-integer such as `["a", "5"]`. Each must fail in a way the docstring states, and as it stands each ends in a raw traceback with no usage text. Decide whether that is intended.
- The test for 1a: a partial last page, for example 11 items at 5 per page, showing that the last index `page_range(3, 5)[1]` is 14 and is not the index of item 11.

Pre-existing state, changed limits and replaced mechanisms: none apply.

## Item 3a: Level, placement, and the environment

`page_range` is observable in one process, so its tests belong in `tests/test_paginate.py`, beside the `page` and `page_count` tests. `main(argv)` takes an argument list and prints to stdout, so an in-process test with `capsys` observes it. No subprocess or installed command is needed for the behavior. The entry-point wiring needs one run of the installed command, which item 2 requests.

## Item 4: Names by content, not by position

None. No test, name or comment in the change uses an ordinal or a position.

## Item 5: The failure report

None, because the change adds no assertions. For the tests requested above, use equality assertions on tuples and on captured output so the failure report prints the operands.

## Item 6: What the writer says it verified

None stated. The change carries no red run and no mutation verdict, and it carries no tests that could fail.

## Item 7: Siblings of the change

- **Helper call sites:** `git grep` shows `page_count`, `page` and `per_page` are used only in `paginate.py`, `README.md` and the tests. The new `page_range` repeats the `number < 1` check and the `(number - 1) * per_page` arithmetic from `page` (`paginate.py:22-23`). `page` has the same unvalidated `per_page`: `page(items, 1, 0)` returns `[]`, and a negative `per_page` slices from the end. `page_range` therefore agrees with `page` and disagrees with `page_count`. Decide one policy for `per_page` across the three functions, and fix it in this change or name it as follow-up in the description. Substantive.
- **Set growth:** `README.md:20-23` lists `page_count` and `page` as the usage. It has no line for `page_range` and no mention of the command. It lists the other members and not the new ones. Substantive: add both.
- **Set size in prose:** no sentence counts the members.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| `page_range` first sentence says "the last item", but the function returns the last slot of a full page, which can lie past the end | Substantive | `src/textkit/paginate.py:28` | 1 |
| `page_range` does not validate `per_page`, and its Raises sentence omits it; `page_count` validates | Substantive | `src/textkit/paginate.py:30` | 1, 7 |
| The module docstring names a `textkit-pages` command, but no entry point or `__main__` block exists | Substantive | `src/textkit/cli.py:1`, `pyproject.toml` | 1, 2 |
| The `main` docstring defines the function through `page_count`'s name and omits `argv`, the return value and the raised `ValueError` | Substantive | `src/textkit/cli.py:9` | 1 |
| No test for `page_range` or for `main`; no boundary, invalid-partition or error case | Substantive | `tests/test_paginate.py`, no `tests/test_cli.py` | 2, 3 |
| The documented command `textkit-pages` has no runnable form in the configuration | Substantive | `pyproject.toml` | 2 |
| PR title and description claim only the `page_count` fix, not `page_range` or the command | Substantive | PR title and description | 2 |
| README usage lists neither `page_range` nor the command | Substantive | `README.md:20-23` | 7 |
| `per_page` policy differs between `page`, `page_range` and `page_count` | Substantive | `src/textkit/paginate.py:16-35` | 7 |
| No red-run or mutation evidence stated | Substantive | change as a whole | 6 |

Checks not done: I did not run `textkit-pages`, since building and running were barred. I cannot say whether `pip install` would expose the command, only that the configuration has no entry for it.
