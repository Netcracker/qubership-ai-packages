**Title:** Colored output can't be turned off from the environment: `NO_COLOR` is ignored

---

We run `quarry` from about a dozen CI scripts, and we need its table output to reach the CI log without ANSI escape sequences. Some of those calls come from `dbt-quarry`, a third-party wrapper we can't edit, so we need a way to turn color off that doesn't depend on the command line. We set `NO_COLOR=1` in the CI environment for this, and quarry v2.4.0 still colors its output.

## What quarry v2.4.0 does

This is the step from our CI job, with the job's log downloaded and shown through `cat -v job.log`. Each `^[` is an ESC byte.

```text
$ NO_COLOR=1 quarry head sales.parquet
^[[1m^[[32mregion^[[0m  ^[[1m^[[32mtotal^[[0m
north   1204
```

`sales.parquet` is one of our files, with the columns `region` and `total`.

`docs/cli.md`, section "Output", documents `--color=auto|always|never` with the default `auto`, which colors when stdout is a terminal. Our CI runner allocates a pseudo-terminal, so `auto` colors there.

Environment: quarry v2.4.0, the latest release, in a CI job. Not established: the runner's OS and image, and whether the same happens in a local terminal; we have only run it in CI.

## What we're asking for

When `NO_COLOR` is set to a non-empty value and no `--color` flag is given, quarry adds no ANSI color to its output, even when stdout is a terminal. A check for this: run `NO_COLOR=1 quarry head <file>` under a pseudo-terminal, and the output contains no ESC byte (`0x1B`). With `NO_COLOR` unset or empty, the output stays as it is today.

This follows the convention at https://no-color.org: "Command-line software which adds ANSI color to its output by default should check for a NO_COLOR environment variable that, when present and not an empty string (regardless of its value), prevents the addition of ANSI color." quarry doesn't claim to follow it. We cite it because it's the variable our CI already sets, and because an environment variable set on the job also applies to the quarry processes the wrapper starts, unless the wrapper clears the environment (we haven't checked that).

What we need is the case without a flag. Whether an explicit `--color=always` overrides `NO_COLOR` is yours to choose; no-color.org allows either.

We're the only case we know of.

## Out of scope

What `--color=auto` does when `NO_COLOR` is unset, and the colors quarry uses.

## Earlier issues

We searched open and closed issues. `NO_COLOR` returned nothing. `color` found #88, "add a flag to disable colors", closed when v2.1.0 added `--color`. This request is for the cases where we can't pass that flag.

## Alternatives

With `quarry --color=never head sales.parquet` in the same CI step, the log has no escape sequences. We'd rather not add the flag to every invocation in our own scripts, and we can't add it to the calls `dbt-quarry` makes.
