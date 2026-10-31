# Hand-over note for the issue "NO_COLOR has no effect"

Nothing was filed or sent. `draft.md` has the title on its first line and the body after the `---` line. Split them before filing, for example:

```bash
gh issue create --repo brightwell/quarry --title "No way to turn off color for every quarry call in CI: NO_COLOR has no effect" --body-file body.md
```

where `body.md` is the part of `draft.md` below the `---` line.

## Why it is a request, not a bug

quarry documents `--color` and says `auto` colors on a terminal. The notes show no document that promises `NO_COLOR` support, so the only grounding is the no-color.org convention (a standard quarry does not claim to implement) and your other CLIs. The report says so in plain words. If you know a quarry document or release note that mentions `NO_COLOR`, add it to the Expected behavior section: it would be stronger grounding.

## Open questions for you

- Do you want to file at all, given the grounding is a convention and your own case? `CONTRIBUTING.md` asks for the use case first and no PR before a maintainer agrees, which the issue follows.
- Is "about a dozen scripts" accurate, and can you name another party affected (a `dbt-quarry` user, for example)? The report says you are the only known case.

## Not established, to close before or after filing

- The `--color=never` run: the notes say it logged no escape sequences, but no log was provided. Paste the `cat -v` output of that step into "The problem" if you have it.
- The runner OS and how quarry was installed (release binary, package manager, container). The notes do not record either.
- Pull requests and Discussions were not searched. Run `NO_COLOR`, `color`, and `ansi` against both. The issue search for `ansi` found only #140 (open, Windows console code page, unrelated), so it is not in the report.
- Whether `docs/cli.md` or the changelog mentions `NO_COLOR` anywhere, and whether the development branch already handles it. No checkout or network was available.
- The notes give no timezone for the 2026-10-30 observation. It is not needed for a release version, so the report omits it.

## Checks done

- No AI policy is listed in the notes, so the report carries no disclosure. Check the repository for one before filing.
- Redaction: the pasted log has no secrets, and `sales.parquet` and `dbt-quarry` are not private names (`dbt-quarry` is a public third-party wrapper). Read the full downloaded `job.log` before attaching anything else from it.
- Attribution: the log and the CI observations are yours from the CI job. The report presents them as observed there, not as a run in this session.
