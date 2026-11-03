Title: Can't turn off color for every invocation from the environment: `NO_COLOR` is ignored

Our CI runs `quarry` in about a dozen scripts, and the CI log viewer shows raw escape sequences in its table output. We set `NO_COLOR=1` in the CI environment, and the other CLIs in those jobs stop coloring. `quarry` does not.

We need one setting in the environment that turns color off for every `quarry` process. Adding `--color=never` to each invocation is not an option for us, because some invocations come from `dbt-quarry`, a third-party wrapper we cannot edit.

Seen on quarry v2.4.0 (the latest release, 2026-09-18) in our CI job on 2026-10-30. This is the step from the job log, downloaded and shown with `cat -v job.log`:

```text
$ NO_COLOR=1 quarry head sales.parquet
^[[1m^[[32mregion^[[0m  ^[[1m^[[32mtotal^[[0m
north   1204
```

`docs/cli.md`, section "Output", documents `--color=auto|always|never` with the default `auto`, which colors when stdout is a terminal. Our CI runner allocates a pseudo-terminal, so `auto` colors there.

**How we would know it worked.** With `NO_COLOR` set to a non-empty value and stdout a pseudo-terminal, `quarry head sales.parquet` writes no escape sequences, and `cat -v` on the job log shows no `^[`. An empty `NO_COLOR` changes nothing.

**What this rests on.** The quarry documentation does not mention `NO_COLOR`. The request rests on the convention at https://no-color.org, which says: "Command-line software which adds ANSI color to its output by default should check for a NO_COLOR environment variable that, when present and not an empty string (regardless of its value), prevents the addition of ANSI color." The other CLIs in our CI jobs follow it, and quarry is the one that does not.

**Scope.** We are not asking to change the `auto` default or to add a quarry-specific variable. How `NO_COLOR` ranks against an explicit `--color=always` is the project's choice. Ours is the only affected setup we know of.

**Related issue.** #88 (closed) asked for a flag to disable colors and was fixed in v2.1.0 by `--color`. This request is for the environment-level counterpart of that flag, for callers that cannot pass it.

**Workaround.** The same step run as `quarry --color=never head sales.parquet` logs no escape sequences in our job. That covers the invocations we write, and not the ones `dbt-quarry` makes.
