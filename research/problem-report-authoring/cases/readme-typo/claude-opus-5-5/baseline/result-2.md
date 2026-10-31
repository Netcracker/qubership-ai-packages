Title: README install command fails: `pip install tidwatch` finds no package on PyPI

The Installation section of the README tells users to run `pip install tidwatch`, and pip finds no package by that name. The package is published as `tidewatch`.

The line is [`README.md` line 23 at `3b9e0d4`](https://github.com/fernlabs/tidewatch/blob/3b9e0d4/README.md#L23) on `main`:

```bash
pip install tidwatch
```

## What I ran and what I saw

I ran the README command on October 30, 2026:

```text
$ pip install tidwatch
ERROR: Could not find a version that satisfies the requirement tidwatch (from versions: none)
ERROR: No matching distribution found for tidwatch
```

The same pip, with the name spelled `pip install tidewatch`, installs 0.14.2.

## Expected

Line 23 reads `pip install tidewatch`. That is the name in `pyproject.toml` (`name = "tidewatch"`) and the project listed at https://pypi.org/project/tidewatch/.

The line read `pip install tidewatch` until `81ac2f7` ("docs: reorganize README", June 12, 2026), which is the commit that last changed it.

## Environment

macOS 15.1, Python 3.12.7, pip 24.3.1, zsh. README at `3b9e0d4` on `main`.

I searched open and closed issues for `tidwatch`, `pip install`, and `README install` and found no report of this.
