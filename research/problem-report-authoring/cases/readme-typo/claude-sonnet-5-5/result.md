Title: README install command says `tidwatch`; the package is `tidewatch`

The "Installation" section of `README.md` (line 23, at `3b9e0d4` on `main`) tells you to run `pip install tidwatch`. That command fails:

```text
$ pip install tidwatch
ERROR: Could not find a version that satisfies the requirement tidwatch (from versions: none)
ERROR: No matching distribution found for tidwatch
```

The package is named `tidewatch`: `pyproject.toml` has `name = "tidewatch"`, and https://pypi.org/project/tidewatch/ lists 0.14.2. `pip install tidewatch` installs 0.14.2. The README line should read `pip install tidewatch`.
