# Hand-over note for the person filing (not part of the issue)

Draft is `draft.md`; the title is its first line. Nothing was filed or run. I had no network and no checkout.

## Evidence I did not produce

- The `NO_COLOR=1` log, the `--color=never` result, and the claim that the other CLIs stop coloring under `NO_COLOR` all come from your notes of the CI job. The issue words them as observed in your CI job and does not present them as my run. I did not see the `--color=never` output itself, only your statement that it has no escape sequences. If you have that log, paste it beside the first one.
- The `docs/cli.md` "Output" section and the no-color.org quote are copied from your notes. Nobody fetched them. Check both sentences against the page at the v2.4.0 tag before filing.

## Gaps the issue does not state (nothing in it rests on them)

- The runner OS, and how it allocates the pseudo-terminal. I left them out because the notes do not say. Add them if a maintainer will need them to reproduce.
- Whether `dbt-quarry` passes `--color` itself or forwards the environment. The issue only says you cannot edit it. Check before sending, since a maintainer may ask.
- Whether v2.4.0 is still the latest release at filing time.

## Lookups to repeat

- Search queries run in your notes, with closed items included: `NO_COLOR` (no hits), `color` (#88), `ansi` (#140, Windows console code page, unrelated). The issue cites only #88. I did not repeat them. Also try `no-color` and `environment variable` on issues and on open pull requests.
- `CONTRIBUTING.md` asks for an issue describing the use case before any PR, so the issue offers no patch. No AI policy was found, so the issue carries no disclosure. Confirm that nothing in the repository's `.github` directory or its README says otherwise.

## Decisions for you

- I wrote this as a feature request, not a bug, because quarry never documents `NO_COLOR`. The grounding is the convention and your CI use, and the issue says so. If you think the maintainers will see it as a defect, say that in your own words.
- The wording about `--color=always` precedence leaves the choice to the project. Change it if you have a position.
- No names were changed. `sales.parquet`, the `region` and `total` columns, and `dbt-quarry` are public or generic. Check that the log lines carry nothing else from your CI.
