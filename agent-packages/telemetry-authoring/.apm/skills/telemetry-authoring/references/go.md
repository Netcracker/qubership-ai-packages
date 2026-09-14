# Go mechanics

Read with `SKILL.md`. This file carries what Go answers differently; the rules themselves are in the body.

## What the host sees when it has configured nothing

**Output on standard error.** `slog.Default()` formats the record and passes it to the `log` package, which writes to
standard error at info level and above. Nothing a library can call makes that silent: the discard handler exists, but
only the host can install it. So a Go library that reaches for the default logger prints into a host that asked for
nothing, and "leave a silent host silent" is not a promise a Go library can keep.

This is why the acquisition rule matters more in Go than elsewhere.

## Deciding where output goes (§6)

Routing is **by value**, so the deciding call is an acquisition rather than a configuration.

| Detection | What it looks like |
| --- | --- |
| Acquiring a logger the caller did not supply | `slog.Default()`, `log.Printf` and friends, a package-level `var logger` |
| Configuring the process | `slog.SetDefault`, installing a handler at package init |
| Gaming | A logger injected once into a package variable and then used as a global. Check that the call site takes the logger from a parameter or a receiver, not from package scope |

The idiom is that a library is handed a logger by its caller, or carries one on the struct it was constructed with,
and uses that. Kubernetes states this directly for shared libraries.

## Authoritative silence

Neither the standard library nor the `log/slog` proposal says anything about what a library should do. The position
above comes from project conventions and from a linter, not from the Go team. Where a Go repository has its own
convention, that convention wins and this file is the fallback.

## Arguments are always evaluated

The arguments to a log call are evaluated even when the record is discarded, by documented design, and Go has no lazy
placeholder form. The guard rule is therefore stronger here than on the JVM or in Python: wrap an expensive argument
in `Logger.Enabled`, or pass a value type whose formatting is deferred.

## Structured fields

`slog.LogAttrs` and the `slog.Attr` constructors are the typed form; the variadic `slog.Info(msg, "key", value)` form
is the one that drops a value when the key-value pairs do not balance.

## Errors

Wrap and return: `fmt.Errorf("...: %w", err)`. A library that logs an error and also returns it produces two records
for one condition and takes a decision that belongs to the caller. The Go style guidance and the logr documentation
both state the rule as: log it only if you are not returning it.

## Context

`context.Context` is an explicit first parameter and nothing is ambient, so the failure is a **missing argument** and
it is visible in the diff: a goroutine started without the context, or a call that takes `ctx` and passes
`context.Background()` onward. There is no stale-context failure, because there is no ambient map to go stale.

## Levels

Kubernetes and logr define verbosity numerically rather than by adjective, with per-level meanings published by the
project (roughly: default operational output, extended output, debugging, trace, the level nobody enables in
production). **This is an example of a project-owned ladder, not a recommendation.** The skill's position stands: the
repository's convention owns the ladder, and the check is agreement with the neighboring calls.

logr's two-kind API (informational records with a verbosity number, plus error records reserved for an error you are
not returning) is the shape that follows from the log-or-return rule.

## Linters and what a clean verdict does not establish

- **`sloglint`**: `no-global` reports the default logger and package-level loggers; `context` reports the
  non-context call variant; `forbidden-keys`, `no-raw-keys`, and the key-value balance checks report field defects.
  A clean `no-global` verdict does **not** establish that the logger came from the caller: a logger injected once
  into a package variable passes.
- **`loggercheck`** reports unbalanced key-value pairs across several logging libraries.
- **`contextcheck`** reports a function that drops an inherited context.
- None of them reports a missing joining identifier, a record that names inputs instead of the branch, or a private
  field name in the message text.
