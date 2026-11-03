# Notes: quarry ignores NO_COLOR

Taken on 2026-10-30. The tool is `quarry`, a CLI that queries Parquet files, github.com/brightwell/quarry,
Apache-2.0. Latest release v2.4.0 (2026-09-18).

## What we need

Our CI runs `quarry` in a dozen scripts, and the CI log viewer shows raw escape sequences in quarry's table output. We
set `NO_COLOR=1` in the CI environment, and the other CLIs in those jobs stop coloring; quarry does not.

On v2.4.0, in the CI job, the step `NO_COLOR=1 quarry head sales.parquet`. The job's log, downloaded and shown with
`cat -v job.log`:

```text
$ NO_COLOR=1 quarry head sales.parquet
^[[1m^[[32mregion^[[0m  ^[[1m^[[32mtotal^[[0m
north   1204
```

The same step with `quarry --color=never head sales.parquet` logs no escape sequences. Adding `--color=never` to every
invocation is what we want to avoid, and some invocations come from a third-party wrapper, `dbt-quarry`, that we
cannot edit.

`docs/cli.md`, section "Output", documents `--color=auto|always|never`, default `auto`, where `auto` colors when stdout
is a terminal. Our CI runner allocates a pseudo-terminal, which is why `auto` colors there.

https://no-color.org: "Command-line software which adds ANSI color to its output by default should check for a
NO_COLOR environment variable that, when present and not an empty string (regardless of its value), prevents the
addition of ANSI color."

## Search

Issues, open and closed: `NO_COLOR` (no hits); `color` (#88, closed, "add a flag to disable colors", fixed in v2.1.0 by
`--color`); `ansi` (#140, open, about the Windows console code page, unrelated).

## Channel

No issue templates. `CONTRIBUTING.md`: "Feature requests: open an issue describing the use case first; please do not
open a PR before a maintainer agrees." No AI policy.

## The task

Draft the GitHub issue for brightwell/quarry, title first.
