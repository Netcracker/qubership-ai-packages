README install command says `tidwatch`; the package is `tidewatch`

The "Installation" section of `README.md` (at `3b9e0d4`, line 23) tells you to run `pip install tidwatch`. That name does not exist on PyPI, so the command fails:

```text
$ pip install tidwatch
ERROR: Could not find a version that satisfies the requirement tidwatch (from versions: none)
ERROR: No matching distribution found for tidwatch
```

The package is `tidewatch`: `pyproject.toml` has `name = "tidewatch"`, and `pip install tidewatch` installs 0.14.2, the version https://pypi.org/project/tidewatch/ lists. The README line should read `pip install tidewatch`.

Run on macOS 15.1 with Python 3.12.7 and pip 24.3.1.
