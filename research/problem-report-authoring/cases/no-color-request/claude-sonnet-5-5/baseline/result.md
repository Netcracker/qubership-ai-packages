Title: No way to turn off color for every quarry call in CI: NO_COLOR has no effect

---

## The problem

Our CI runs `quarry` in about a dozen scripts, and the CI log viewer shows raw escape sequences in quarry's table output. We set `NO_COLOR=1` in the CI environment, and the other CLIs in those jobs stop coloring. quarry does not. We want to turn color off once, in the environment, for every `quarry` call in a job.

Observed on v2.4.0 (the latest release, 2026-09-18) in our CI job on 2026-10-30. This is the job log, downloaded and shown with `cat -v`:

```text
$ NO_COLOR=1 quarry head sales.parquet
^[[1m^[[32mregion^[[0m  ^[[1m^[[32mtotal^[[0m
north   1204
```

`docs/cli.md`, section "Output", documents `--color=auto|always|never` with the default `auto`, which colors when stdout is a terminal. Our CI runner allocates a pseudo-terminal, so `auto` colors there. The same step run as `quarry --color=never head sales.parquet` logged no escape sequences. I have not pasted that log here.

Not established: the runner's operating system and how quarry was installed. I did not check the development branch.

## Expected behavior

With `NO_COLOR` set to a non-empty value and no `--color` option, `quarry head sales.parquet` run on a pseudo-terminal writes no ANSI escape sequences, so `cat -v` on its output shows no `^[`. An empty `NO_COLOR` leaves the behavior unchanged.

This rests on the convention at https://no-color.org: "Command-line software which adds ANSI color to its output by default should check for a NO_COLOR environment variable that, when present and not an empty string (regardless of its value), prevents the addition of ANSI color." It rests on that convention and on the other CLIs in our jobs, not on a quarry document.

How `NO_COLOR` interacts with an explicit `--color=always` is for quarry to decide.

## Who else is affected, and the cost

I know of one case, ours. Until this works, the CI logs of every job that calls `quarry` stay unreadable in the log viewer, or we change every call, which we cannot do everywhere (see below). I can't judge the cost of the change on your side.

## Out of scope

This does not ask to change the `--color` option, the meaning of `auto`, or to support other color variables.

## Prior proposals

Searched issues, open and closed, for `NO_COLOR` (no hits) and `color`. The nearest hit is #88 (closed, fixed in v2.1.0), which asked for a flag to disable colors and was resolved by adding `--color`. This request is about turning color off without passing a flag on each call. I did not search pull requests or Discussions.

## Alternatives

Passing `--color=never` to every invocation works in our own scripts, and we want to avoid it for a dozen scripts. Some invocations come from the third-party wrapper `dbt-quarry`, which we cannot edit, so the option cannot reach them.
