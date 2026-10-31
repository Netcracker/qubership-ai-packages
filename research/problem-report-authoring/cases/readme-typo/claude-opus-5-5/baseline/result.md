# Title

README install command `pip install tidwatch` fails with "No matching distribution found"

# Body

Running the install command from the README's "Installation" section fails, because the README spells the package name `tidwatch`. The package on PyPI is `tidewatch`.

`README.md` on `main` at commit `3b9e0d4`, line 23 ([link](https://github.com/fernlabs/tidewatch/blob/3b9e0d4/README.md#L23)):

```text
pip install tidwatch
```

Running it on 2026-10-30:

```text
$ pip install tidwatch
ERROR: Could not find a version that satisfies the requirement tidwatch (from versions: none)
ERROR: No matching distribution found for tidwatch
```

### Expected

Line 23 reads `pip install tidewatch`, and running it installs the package. `pyproject.toml` declares `name = "tidewatch"`, and https://pypi.org/project/tidewatch/ lists 0.14.2.

The line read `pip install tidewatch` until `81ac2f7` ("docs: reorganize README", 2026-06-12), the commit that last changed it according to `git blame`.

### Environment

macOS 15.1, Python 3.12.7, pip 24.3.1, zsh.

### Workaround

`pip install tidewatch` installs 0.14.2 with the same pip.

### Duplicates

I searched open and closed issues for `tidwatch`, `pip install`, and `README install` and found no matches. The open pull request #212 ("docs: README badges") edits README lines 3 to 8 only.
