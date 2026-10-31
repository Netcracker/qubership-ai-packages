# Hand-over note: quarry `NO_COLOR` request

Nothing was filed or sent. The body is in `draft.md`; the title is its first line, so strip that line before using `--body-file`. Suggested command:

```bash
gh issue create --repo brightwell/quarry \
  --title "No environment-level way to turn off color in table output (NO_COLOR is ignored)" \
  --body-file body.md
```

## Genre

I wrote this as a feature request, not a bug. The only documentation I have (`docs/cli.md`, "Output") promises `--color` with `auto` on a terminal and says nothing I can see about `NO_COLOR`, so the expectation rests on no-color.org and on your setup. `CONTRIBUTING.md` asks for an issue before any PR, so none is offered.

## What I did not do or establish

- I ran nothing. The log, the `--color=never` result, and "other CLIs stop coloring" all come from your CI notes. The draft presents them as your job's results.
- Not established: that `docs/cli.md` never mentions `NO_COLOR`. The notes only say the issue search had no hits. Please grep the docs at v2.4.0 and the README. If a mention exists, the draft sentence "The project documents no such variable that I know of" must change.
- Not established: that the notes' `docs/cli.md` text matches v2.4.0 and not `main`.
- Not tested: an empty `NO_COLOR`, `NO_COLOR` together with `--color=always`, or non-pseudo-terminal output.
- Not checked: open pull requests or recent `main` commits that already add `NO_COLOR` support. Run `gh pr list --repo brightwell/quarry --state all --search NO_COLOR`.
- I did not check the repository for issue templates beyond your note that none exist, or for `SECURITY.md`. This is not a vulnerability.

## Searches

Your queries, kept out of the body: `NO_COLOR` (no hits); `color` (#88 closed, fixed in v2.1.0 by `--color`); `ansi` (#140, open, Windows console code page, unrelated). The body names #88 only. Please confirm all three included closed items. Also try `no-color` and `colour`, since trackers match titles and wording.

## Questions for you

- Can you explain and defend this issue without me? No AI policy was found, so I added no disclosure.
- The draft says "the only known case here is ours". If others use `dbt-quarry` with this setup, naming them would strengthen it.
- Check before filing that `dbt-quarry` really calls `quarry` with no way to inject flags, since the draft relies on it. It is your claim, not mine.
- Names such as `sales.parquet` and `dbt-quarry` are public or generic, and nothing secret was in the log. Please look at the full job log before you paste any more of it.
