README install command names `tidwatch`; the package on PyPI is `tidewatch`

The "Installation" section of `README.md` ([line 23 at `3b9e0d4`](https://github.com/fernlabs/tidewatch/blob/3b9e0d4/README.md#L23)) tells you to run `pip install tidwatch`. That command fails:

```text
$ pip install tidwatch
ERROR: Could not find a version that satisfies the requirement tidwatch (from versions: none)
ERROR: No matching distribution found for tidwatch
```

`pip install tidewatch` installs 0.14.2, and `tidewatch` is the `name` in `pyproject.toml`.
