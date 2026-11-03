No way to turn off colored output from the environment: `NO_COLOR` is ignored

Our CI runs quarry in about a dozen scripts, and the CI log viewer shows quarry's table output with raw escape sequences. We set `NO_COLOR=1` in the CI environment to get plain logs. The other CLIs in those jobs stop coloring, and quarry v2.4.0 keeps coloring.

The step `NO_COLOR=1 quarry head sales.parquet` in the CI job, from the downloaded job log shown with `cat -v job.log`:

```text
$ NO_COLOR=1 quarry head sales.parquet
^[[1m^[[32mregion^[[0m  ^[[1m^[[32mtotal^[[0m
north   1204
```

The runner allocates a pseudo-terminal, so the default `--color=auto` colors there, as the "Output" section of `docs/cli.md` describes.

The same step with `quarry --color=never head sales.parquet` logs no escape sequences. That flag has to be added to every invocation, though, and some of our invocations come from `dbt-quarry`, a third-party wrapper we cannot edit. We are the only affected user we know of.

What we need: when `NO_COLOR` is set to a non-empty value and no `--color` flag is given, quarry adds no ANSI color, whether or not stdout is a terminal. A test for it: under a pseudo-terminal, `NO_COLOR=1 quarry head sales.parquet` writes no ESC byte (`0x1b`), and with `NO_COLOR` unset or empty the output stays as it is in v2.4.0. Whether an explicit `--color=always` overrides `NO_COLOR` is yours to choose.

Nothing in quarry's documentation promises this. The request rests on the convention at https://no-color.org, which the other CLIs in our jobs follow:

> Command-line software which adds ANSI color to its output by default should check for a NO_COLOR environment variable that, when present and not an empty string (regardless of its value), prevents the addition of ANSI color.

#88 asked for a way to disable colors and was fixed in v2.1.0 by `--color`. This request is for a switch that needs no change to the command line.
