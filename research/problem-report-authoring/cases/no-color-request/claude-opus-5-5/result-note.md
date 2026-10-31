# Hand-over note: quarry `NO_COLOR` request

The draft is a feature request, not a bug report: `docs/cli.md` documents that `auto` colors on a terminal, so quarry behaves as documented, and nothing in the project promises `NO_COLOR` support. The first line of `draft.md` is the title; the rest is the body.

Filing (after removing the title line into a separate body file):

```bash
tail -n +3 out/draft.md > body.md
gh issue create --repo brightwell/quarry \
  --title 'Color output can'"'"'t be turned off from the environment: `NO_COLOR` is ignored' \
  --body-file body.md
```

The repository has no issue templates, so the body uses plain GitHub Markdown with no form headings. `CONTRIBUTING.md` asks for a use-case issue before any pull request, so the draft offers no patch. Don't open a PR until a maintainer agrees.

## What I did not do

I had no network access and no checkout, so I ran nothing and looked nothing up. Everything in the draft comes from your notes of 2026-10-30.

- **The `--color=never` run.** The draft says it logs no escape sequences, but your notes contain no transcript for it. If you have that job log, paste the `cat -v` excerpt next to the first one.
- **Pseudo-terminal claim.** The draft states that the runner allocates a pseudo-terminal. To confirm it, run `test -t 1 && echo tty` as a step in the same job.
- **Unreleased work.** Look at `main` and open PRs for `NO_COLOR` handling that hasn't shipped yet: `gh search prs --repo brightwell/quarry NO_COLOR`, and `git log -S NO_COLOR` in a clone.
- **Other color controls.** Make sure `docs/cli.md` (or a config file reference) has no existing environment variable or config key for color, such as `QUARRY_COLOR`. If one exists, the request changes or goes away.
- **`dbt-quarry`.** Find out whether the wrapper has its own way to pass `--color`. A maintainer will suggest that first. If it has one, add a sentence saying why it doesn't serve you, or drop the request. If the wrapper is public, link it. If it's an internal name, replace it before you file, because this is a public tracker.
- **CI system.** The draft doesn't name the CI system or runner. Add them if you think the terminal detection depends on them.

## Search

These queries are from your notes. The draft cites #88 as the nearest hit and doesn't mention the queries.

- `NO_COLOR`, open and closed: no hits.
- `color`: #88, closed, fixed in v2.1.0 by `--color`.
- `ansi`: #140, open, about the Windows console code page, unrelated.

Before filing, also search closed PRs and Discussions for `NO_COLOR` and `environment variable color`.

## For you to decide

- The project has no AI policy, so no disclosure is required. Whether to mention that a tool drafted the issue is up to you.
- The draft says you know of no affected users outside your own CI. If you know of other `dbt-quarry` users who are affected, name them; it strengthens the request.
