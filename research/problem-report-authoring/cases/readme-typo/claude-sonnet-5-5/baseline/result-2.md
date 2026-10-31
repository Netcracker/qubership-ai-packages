Title: README install command misspells the package name: `pip install tidwatch` finds no distribution

## What happened

I tried to install tidewatch by copying the command from the "Installation" section of `README.md` (line 23 at commit `3b9e0d4` on `main`). pip fails:

```text
$ pip install tidwatch
ERROR: Could not find a version that satisfies the requirement tidwatch (from versions: none)
ERROR: No matching distribution found for tidwatch
```

The README spells the name `tidwatch`, without the second `e`. The package on PyPI is `tidewatch`, and `pip install tidewatch` installs 0.14.2.

## Expected

The command in the README installs the library, so it should read:

```text
pip install tidewatch
```

This rests on `pyproject.toml` (`name = "tidewatch"`) and on https://pypi.org/project/tidewatch/, which lists 0.14.2.

## Environment

- README: `README.md` at `3b9e0d4`, section "Installation", line 23.
- macOS 15.1, zsh, Python 3.12.7, pip 24.3.1.
- PyPI page checked on 2026-10-30.

## Additional information

`git blame` shows that line 23 last changed in `81ac2f7` (2026-06-12, "docs: reorganize README"). Before that commit the line read `pip install tidewatch`.

I searched open and closed issues and found no report of this. The nearest item is the open pull request #212 ("docs: README badges"), which touches lines 3 to 8 only, so it does not overlap with line 23.
