# Hand-over note: README install command issue

`draft.md` holds the title on its first line, then a blank line, then the body. To file it, copy the first line into `--title` and the rest into a body file, for example:

```bash
gh issue create --repo fernlabs/tidewatch \
  --title 'README install command says `tidwatch`; the package is `tidewatch`' \
  --body-file body.md
```

Nothing was filed or sent.

## Left out of the report on purpose

- **Search.** The issues search (open and closed) for `tidwatch`, `pip install`, and `README install` had no hits, per your notes. The report has no slot for it, so it is only here. Open PR #212 "docs: README badges" touches lines 3 to 8 only, so it does not overlap line 23.
- **History.** `git blame` shows line 23 last changed in `81ac2f7` (2026-06-12, "docs: reorganize README"). Before that commit it read `pip install tidewatch`. A maintainer does not need this to fix one word, so I cut it. Add it if you want the cause on record.
- **Channel.** The repository has no issue template, `CONTRIBUTING.md`, security policy, or AI policy, so there is no disclosure to answer. Existing issues use Markdown with fenced code blocks, which the draft follows.

## Not established

- I did not run anything. The pip output, the 0.14.2 install, and the blame result are all from your notes of 2026-10-30. The report states them as your run, in first person with no label.
- Not checked: whether `README.md` has changed since `3b9e0d4`. Before filing, run `git fetch && git diff 3b9e0d4 origin/main -- README.md` and update the commit if line 23 moved.
- Not checked: whether `tidwatch` was ever registered on PyPI. If you want that stated, check https://pypi.org/project/tidwatch/ (a 404 supports the "does not exist" wording).

## Open for you

- The fix is a one-character edit. If you want to contribute it, a pull request may serve better than an issue. Say so and I will reword the draft as a pull request description.
