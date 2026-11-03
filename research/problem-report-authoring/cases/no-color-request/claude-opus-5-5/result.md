Color output can't be turned off from the environment: `NO_COLOR` is ignored

We run `quarry` from a dozen CI scripts, and the CI log viewer shows raw escape sequences in its table output. We need to turn color off for every quarry invocation in a job from the environment, because some invocations come from `dbt-quarry`, a third-party wrapper whose command lines we can't edit. The job sets `NO_COLOR=1`, and quarry v2.4.0 still colors its output. The step's log, downloaded and shown with `cat -v job.log`:

```text
$ NO_COLOR=1 quarry head sales.parquet
^[[1m^[[32mregion^[[0m  ^[[1m^[[32mtotal^[[0m
north   1204
```

The "Output" section of `docs/cli.md` documents `--color=auto|always|never`, default `auto`, where `auto` colors when stdout is a terminal. Our CI runner allocates a pseudo-terminal, so `auto` colors there. The same step run as `quarry --color=never head sales.parquet` logs no escape sequences, but the flag has to go on each invocation, and we can't add it to the ones `dbt-quarry` makes.

quarry doesn't claim to follow https://no-color.org, so this request rests on that convention and on our CI setup. The convention reads: "Command-line software which adds ANSI color to its output by default should check for a NO_COLOR environment variable that, when present and not an empty string (regardless of its value), prevents the addition of ANSI color."

How to tell it works: with `NO_COLOR=1` set and stdout a terminal, `quarry head sales.parquet` writes no ANSI escape sequences; with `NO_COLOR` unset or set to an empty string, it colors as v2.4.0 does.

One possible shape is to treat a non-empty `NO_COLOR` like `--color=never` when `--color` is `auto`. What we need is a variable that every invocation inherits from the environment. Whether an explicit `--color=always` overrides it is yours to decide, and a quarry-specific variable would also work for us.

#88 asked for a way to disable colors and was closed by the `--color` flag in v2.1.0. This request is for invocations whose arguments we don't control. We know of no affected users outside our own CI.
