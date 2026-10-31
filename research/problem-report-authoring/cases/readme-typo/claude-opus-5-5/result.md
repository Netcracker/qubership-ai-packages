README install command names `tidwatch`; the PyPI package is `tidewatch`

The "Installation" section of [`README.md`](https://github.com/fernlabs/tidewatch/blob/3b9e0d4/README.md#L23) (line 23 at `3b9e0d4`) tells you to run `pip install tidwatch`, and pip finds no such package:

```text
$ pip install tidwatch
ERROR: Could not find a version that satisfies the requirement tidwatch (from versions: none)
ERROR: No matching distribution found for tidwatch
```

`pip install tidewatch` installs 0.14.2, and `tidewatch` is the `name` in `pyproject.toml`.

The open pull request #212 changes README lines 3 to 8 only and leaves this line as it is.
