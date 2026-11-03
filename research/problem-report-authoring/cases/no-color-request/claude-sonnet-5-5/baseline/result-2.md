Title: No way to turn off color for every quarry call in a CI job: NO_COLOR is not honored

---

Our CI runs `quarry` in a dozen scripts, and the CI log viewer shows raw escape sequences in quarry's table output. We want to turn color off once, for the whole job, and not in each invocation. We set `NO_COLOR=1` in the job environment and the other CLIs in those jobs stop coloring. `quarry` does not.

## What v2.4.0 does today

Seen in our CI job on quarry v2.4.0 on October 30, 2026, and not re-run locally. The job log, downloaded and shown with `cat -v job.log`:

```text
$ NO_COLOR=1 quarry head sales.parquet
^[[1m^[[32mregion^[[0m  ^[[1m^[[32mtotal^[[0m
north   1204
```

The same step run as `quarry --color=never head sales.parquet` logs no escape sequences. `docs/cli.md`, section "Output", documents `--color=auto|always|never` with `auto` as the default, and says `auto` colors when stdout is a terminal. Our CI runner allocates a pseudo-terminal, so `auto` colors there. Nothing in `docs/cli.md` mentions `NO_COLOR`.

## What would count as fixed

With `NO_COLOR` set to a non-empty value, no `--color` flag, and stdout a terminal, `quarry head sales.parquet` writes no ANSI escape sequences. When `NO_COLOR` is unset or empty, behavior stays as it is today.

This follows https://no-color.org: "Command-line software which adds ANSI color to its output by default should check for a NO_COLOR environment variable that, when present and not an empty string (regardless of its value), prevents the addition of ANSI color." quarry does not claim to implement that convention, so the expectation rests on the convention and on what the other CLIs in our jobs do.

## Who is affected

We are the only case I know of. Some of our invocations come from a third-party wrapper, `dbt-quarry`, which we cannot edit. A command-line flag cannot reach those calls, and an environment variable can.

## Out of scope

How `NO_COLOR` ranks against an explicit `--color=always` is for the maintainers to decide. This request does not ask for other color settings, such as a config file key.

## Earlier discussion

Searching issues, open and closed, for `NO_COLOR` finds nothing. #88 (closed) asked for a way to disable colors, and v2.1.0 added `--color` for it. This request is about turning color off without a flag on each call. #140 is about the Windows console code page and is unrelated.

## Alternative

Adding `--color=never` to every invocation avoids the escape sequences in our scripts. We want to avoid that across a dozen scripts, and it cannot be done for the `dbt-quarry` calls.
