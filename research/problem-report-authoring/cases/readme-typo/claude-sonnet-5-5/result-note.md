# Hand-over note for the person filing

Nothing was filed or sent. `draft.md` holds the title on its first line and the body below it. Split them before filing.

## Filing

Save the body (everything after the title line and the blank line) to a file, for example `body.md`, then run:

```bash
gh issue create --repo fernlabs/tidewatch \
  --title 'README install command says `tidwatch`; the package is `tidewatch`' \
  --body-file body.md \
  --label documentation
```

Check that `--label documentation` is accepted. Your notes say the label exists, but labels may be restricted to maintainers.

## Evidence

Every observation in the report comes from your notes of 2026-10-30. I ran nothing, and I had no checkout or network. Please confirm before filing:

- `README.md` line 23 still reads `pip install tidwatch` on current `main`. The report names `3b9e0d4`, so if `main` has moved, check that the line is unchanged.
- PyPI still lists `tidewatch` at 0.14.2. If a newer release is out, update the version in the report or drop it.

## Left out of the report

These answer no triager question, so they are here and not in the report.

- **History:** `git blame` shows line 23 changed in `81ac2f7` (2026-06-12, "docs: reorganize README"). The line read `pip install tidewatch` before that commit.
- **Search:** issues, open and closed, for `tidwatch`, `pip install`, and `README install` returned nothing. Open pull request #212 ("docs: README badges") touches lines 3 to 8 only, so it does not overlap line 23.
- **Environment:** macOS 15.1, Python 3.12.7, pip 24.3.1, zsh. The failure does not depend on any of these, because pip cannot find a name that does not exist on PyPI.

## Questions for you

- **A pull request instead of an issue?** The fix is one word. The project has no contribution guide, so a pull request that changes line 23 may serve better than an issue. If you file the issue anyway, you could offer the pull request in a comment. Pull request #212 touches other lines, so the two should not conflict.
- **Disclosure:** the project has no AI policy and no issue template, so nothing is asked of the report. Decide whether you want to mention that it was drafted with a tool.
