# Hand-over note: README install command issue for fernlabs/tidewatch

`draft.md` has the title on its first line and the issue body below it. Nothing has been filed.

## Filing

Copy everything after the title line into a body file, then run the command:

```bash
tail -n +3 draft.md > body.md
gh issue create --repo fernlabs/tidewatch \
  --title 'README install command names `tidwatch`; the package on PyPI is `tidewatch`' \
  --label documentation \
  --body-file body.md
```

The repository has no issue templates, so the body follows no form. It is short on purpose: the misspelled
name next to the correct one shows what is expected, so it needs no extra sections.

## What I did not do

- I did not run anything. The `pip` transcript, the `pip install tidewatch` result, the PyPI listing, and the
  issue search all come from your notes of 2026-10-30. If you want to check that `main` still has the typo
  before filing, run:

  ```bash
  curl -s https://raw.githubusercontent.com/fernlabs/tidewatch/main/README.md | grep -n 'pip install'
  ```

- Duplicate search, from your notes: issues, open and closed, for `tidwatch`, `pip install`, and
  `README install`, with no hits. The issue doesn't mention the search, because it found nothing and the
  repository has no template field to record a search in. The one open pull request, #212 "docs: README
  badges", changes lines 3 to 8 only, so it doesn't fix line 23 and the issue doesn't mention it either.
- I left out the history from your notes: line 23 last changed in `81ac2f7` (2026-06-12, "docs: reorganize
  README"), and before that commit it read `pip install tidewatch`. A maintainer doesn't need it to fix
  one word. If you open a pull request instead, the commit message is a good place for it.

## Decisions for you

- Issue or pull request: the fix is one word on one line. A pull request that changes `tidwatch` to
  `tidewatch`, with this text as its description, might get merged faster than an issue.
- Disclosure: the repository has no AI policy and no contribution guide, so nothing requires a statement
  that a tool drafted this. Whether to add one anyway is up to you.
