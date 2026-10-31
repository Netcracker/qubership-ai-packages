Title: No way to turn off colored output from the environment: NO_COLOR is ignored

---

## Problem

We run `quarry` in about a dozen CI scripts, and our CI log viewer shows quarry's table output with raw escape
sequences in it. To keep color out of CI logs, we set `NO_COLOR=1` in the CI environment. The other CLIs in those jobs
stop coloring, but quarry v2.4.0 keeps coloring.

This is the step `NO_COLOR=1 quarry head sales.parquet` from one of our CI jobs, with the job log downloaded and shown
with `cat -v job.log`:

```text
$ NO_COLOR=1 quarry head sales.parquet
^[[1m^[[32mregion^[[0m  ^[[1m^[[32mtotal^[[0m
north   1204
```

quarry behaves as documented here. `docs/cli.md`, section "Output", documents `--color=auto|always|never` with the
default `auto`, and `auto` colors when stdout is a terminal. Our CI runner allocates a pseudo-terminal, so stdout is a
terminal in these steps. This is a feature request, not a bug report.

Some of our quarry invocations come from a third-party wrapper, `dbt-quarry`, which we can't edit. We are the only
case of this we know of.

## What we're asking for

When `NO_COLOR` is set to a non-empty value, quarry should write no ANSI color sequences, even when stdout is a
terminal. This is the convention at https://no-color.org:

> Command-line software which adds ANSI color to its output by default should check for a NO_COLOR environment
> variable that, when present and not an empty string (regardless of its value), prevents the addition of ANSI color.

quarry's documentation doesn't say it follows that convention. The request rests on the convention and on the CI case
above.

**Acceptance criterion:** with `NO_COLOR=1`, no `--color` flag, and stdout on a terminal, `quarry head sales.parquet`
writes no ESC byte (`0x1b`). With `NO_COLOR` unset or empty, the output is the same as in v2.4.0.

**Out of scope:** how `NO_COLOR` interacts with an explicit `--color=always` is yours to decide; our invocations pass
no `--color` flag. We aren't asking to change the default of `--color` or how `auto` detects a terminal.

## Prior issues

We searched issues, open and closed, for `NO_COLOR` (no results) and for `color`. The nearest is #88, "add a flag to
disable colors", closed as fixed in v2.1.0 by `--color`. That flag works for commands we can edit. This request is for
a way to turn color off without changing the command line.

## Alternatives

`--color=never` works for the commands we control: in the same CI job, `quarry --color=never head sales.parquet` logs
no escape sequences. We ruled it out because it means editing every invocation, and it can't reach the invocations
that `dbt-quarry` makes.

## Environment

- quarry v2.4.0, the latest release (September 18, 2026)
- CI: `<CI system and runner version>`, `<runner OS and version>`
