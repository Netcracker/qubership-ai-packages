Title: README install command misspells the package name, so `pip install tidwatch` fails

I tried to install tidewatch by copying the command from the "Installation" section of the README. The command fails, because the package name in it is misspelled (`tidwatch`, without the second `e`).

```text
$ pip install tidwatch
ERROR: Could not find a version that satisfies the requirement tidwatch (from versions: none)
ERROR: No matching distribution found for tidwatch
```

`pip install tidewatch` installs 0.14.2.

## Expected behavior

The command in the README installs the package. The distribution name it gives must be `tidewatch`, the `name` in `pyproject.toml` and the name of the project at https://pypi.org/project/tidewatch/ (0.14.2 is the release listed there). With that name the command is:

```text
pip install tidewatch
```

## Version and environment

- Documentation: `README.md` on `main` at commit `3b9e0d4`, "Installation", line 23.
- Machine: macOS 15.1, Python 3.12.7, pip 24.3.1, zsh.
- The error comes from pip failing to find the name, so I did not test other platforms.

## Where it came from

`git blame` shows line 23 last changed in `81ac2f7` (2026-06-12, "docs: reorganize README"). Before that commit the line read `pip install tidewatch`, so the commit introduced the typo.

The nearest open item is PR #212, "docs: README badges". It touches lines 3 to 8 only, so it does not fix this line.
