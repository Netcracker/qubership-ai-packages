Title: No environment-level way to turn off color in table output (`NO_COLOR` is ignored)

Our CI runs `quarry` from a dozen scripts, and the CI log viewer shows raw escape sequences in its table output. We want to turn color off for the whole job in one place, without editing each invocation. Some invocations come from `dbt-quarry`, a third-party wrapper we cannot edit.

Other CLIs in those jobs stop coloring when we set `NO_COLOR=1` in the CI environment, but `quarry` still colors. This is the job log of that step on v2.4.0 (the latest release, 2026-09-18), downloaded and shown with `cat -v`:

```text
$ NO_COLOR=1 quarry head sales.parquet
^[[1m^[[32mregion^[[0m  ^[[1m^[[32mtotal^[[0m
north   1204
```

Our runner allocates a pseudo-terminal. `docs/cli.md`, section "Output", documents `--color=auto|always|never` with a default of `auto`, where `auto` colors when stdout is a terminal. The log above comes from our CI job, not from a local run.

## What we need

When `NO_COLOR` is set to a non-empty value and no `--color` flag is given, `quarry` writes no ANSI color sequences, so the log of `NO_COLOR=1 quarry head sales.parquet` on a pseudo-terminal contains no `^[` under `cat -v`.

This is the convention at https://no-color.org: "Command-line software which adds ANSI color to its output by default should check for a NO_COLOR environment variable that, when present and not an empty string (regardless of its value), prevents the addition of ANSI color." The project documents no such variable that I know of (see the hand-over note), so this request rests on that convention and on our setup.

Which of `--color` and `NO_COLOR` wins when both are present is for the project to decide. We do not need a change to the default or support for any other environment variable.

## Related issue

#88 (closed) added `--color` in v2.1.0. This request leaves the flag as it is and asks for the environment to feed the same decision where the flag is absent. I found no issue that mentions `NO_COLOR`.

## What we tried

`quarry --color=never head sales.parquet` logs no escape sequences in our job. That works for the scripts we own and does not reach the `dbt-quarry` invocations, which is why it does not solve this for us. The only known case here is ours.
