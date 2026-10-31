# Hand-over note: `NO_COLOR` request for brightwell/quarry

`draft.md` holds the title on its first line and the issue body from line 3. I wrote it with no network and no checkout, from the notes in `prompt.md` alone. Nothing has been filed.

## Filing

The project has no issue templates, so the body is plain GitHub Markdown with no form fields. `CONTRIBUTING.md` asks for feature requests to start as an issue describing the use case, so this is filed as an issue. It also says not to open a PR before a maintainer agrees, so the draft doesn't offer one.

```bash
tail -n +3 draft.md > body.md
gh issue create --repo brightwell/quarry \
  --title 'No way to turn off colored output from the environment: `NO_COLOR` is ignored' \
  --body-file body.md
```

## Lookups I could not make

- **Duplicate search.** These are the queries from the notes, re-run with closed items included, plus a few more: `NO_COLOR`, `no-color`, `color`, `ansi`, and `NO_COLOR` across pull requests and Discussions (`gh search issues --repo brightwell/quarry --include-prs "NO_COLOR"`). If an open item or PR already asks for this, it's your call whether a comment there would work better than a new issue.
- **Currency.** Check that v2.4.0 is still the latest release. Also check that `main` hasn't added `NO_COLOR` since 2026-09-18: read `CHANGELOG.md` and run `git log -S NO_COLOR` on a fresh clone.
- **Channel.** Check that `.github/ISSUE_TEMPLATE/` is still absent, including `config.yml` with contact links, and that no AI policy has been added since the notes were taken.
- **Precedence.** The no-color.org FAQ discusses how command-line flags interact with `NO_COLOR`. I didn't quote it because the notes don't contain it. The draft leaves that choice to the maintainers.

## Evidence the draft rests on

- The log excerpt and the `--color=never` result come from your CI job, not from a run in this session. If the pasted lines were cut from a longer log, add "trimmed to this step" above the block.
- No local run was made. To add one, run this in a terminal: `script -q /dev/null env NO_COLOR=1 quarry head sales.parquet | cat -v` on macOS, or `script -qc 'NO_COLOR=1 quarry head sales.parquet' /dev/null | cat -v` on Linux.
- The draft says "the other CLIs in those jobs" without naming them. Naming two or three that honor `NO_COLOR` in the same job would make the grounding stronger.
- "We are the only affected user we know of" is your statement to confirm or replace. If you know of other `dbt-quarry` users who hit this, name them.

## For you to decide

- The project has no AI policy, so nothing requires disclosure. Whether to mention that a tool drafted the issue, and whether the project would welcome an agent-drafted report, is up to you.
