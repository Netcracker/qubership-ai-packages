# Notes: the install command in the README

Taken on 2026-10-30. The repository is github.com/fernlabs/tidewatch, a public Python library and CLI for tide-gauge
data, MIT-licensed.

## What I saw

`README.md` on `main` at commit `3b9e0d4`, section "Installation", line 23:

```text
pip install tidwatch
```

The package on PyPI is `tidewatch` (`pyproject.toml` has `name = "tidewatch"`, and https://pypi.org/project/tidewatch/
lists 0.14.2). The command from the README:

```text
$ pip install tidwatch
ERROR: Could not find a version that satisfies the requirement tidwatch (from versions: none)
ERROR: No matching distribution found for tidwatch
```

`pip install tidewatch` installs 0.14.2.

My machine: macOS 15.1, Python 3.12.7, pip 24.3.1, zsh.

`git blame`: line 23 last changed in `81ac2f7` (2026-06-12, "docs: reorganize README"), which also renamed the
headings. Before that commit the line read `pip install tidewatch`.

## Search

Issues, open and closed, for `tidwatch`, `pip install`, `README install`: no hits. One open pull request, #212 "docs:
README badges", touches lines 3 to 8 only.

## Channel

No `.github/ISSUE_TEMPLATE`, no `CONTRIBUTING.md`, no security or AI policy. Issues are enabled; existing issues use
Markdown with fenced code blocks. Labels include `documentation`. The person filing will run `gh issue create`
themselves.

## The task

Draft the GitHub issue for fernlabs/tidewatch that reports this, title first.
