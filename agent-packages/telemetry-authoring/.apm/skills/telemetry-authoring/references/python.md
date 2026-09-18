# Python mechanics

Read with `SKILL.md`. This file carries what Python answers differently; the rules themselves are in the body.

## What the host sees when it has configured nothing

**Warnings and above, on standard error**, through the last-resort handler. The standard library calls this the best
default behavior, and offers the null handler as an **opt-out** for a library that does not want it, not as a rule
every library must follow. Attaching a `NullHandler` is a choice to suppress a default the standard library considers
correct, and the library's documentation says so.

## Deciding where output goes (§6)

Routing is **by name**, so the deciding call is a configuration call.

| Detection | What it looks like |
| --- | --- |
| Configuring from library code | `logging.basicConfig`, `dictConfig`, `fileConfig`, `setLevel` on a logger the library does not own, `addHandler` with anything but `NullHandler` |
| Logging to the root logger | `logging.info(...)` and friends at module level, rather than through a named logger |

The library obtains its logger with `logging.getLogger(__name__)`, so the host configures it by the package path.

**The null handler is the standard library's.** Use `logging.NullHandler` itself or a subclass; a private class with
the same name defeats a host's `isinstance` check.

## The caller's channel

Python has a first-class channel for a condition the caller can fix: the standard library's routing table sends an
avoidable issue that the client application should change to `warnings.warn(...)`, and reserves a warning-level log
record for when there is nothing the client application can do about the situation.

The category names the condition. `DeprecationWarning` is for a deprecation, and Python hides it by default outside
`__main__`, so a runtime or configuration problem raised under it is invisible to most callers. Use `UserWarning` for
a condition the caller's code should change and `RuntimeWarning` for a dubious runtime condition, or a category the
library defines. Set `stacklevel=2` so the warning points at the caller's line rather than the library's.

Detection: a warning-level log call in library code whose text tells the caller to change their code; a
`DeprecationWarning` on a condition that is not a deprecation. The warnings registry deduplicates per call site, so
the same condition does not need a rate limit.

## Errors

The same table routes reporting an error about a runtime event to raising an exception, and reserves the error and
exception log levels for suppressing an error without raising. `logger.exception` inside a handler attaches the
traceback; `logger.error(str(e))` discards it and duplicates the message. No Ruff rule reports a log followed by a
raise; the reviewer reads the path.

## Numbers in a message

Neither `%`-formatting nor the format mini-language's `,` and `_` separators are locale-aware; only the `n`
presentation type is, and a logging call does not reach it by accident.

## Structured fields

`extra=` on the call, or a structured-logging library's bound key-value pairs. A value the reader filters on goes
there, not into an f-string in the message.

## Guards

The `%`-style arguments are formatted lazily, so `logger.debug("x=%s", expensive())` still evaluates `expensive()`
but avoids the formatting; an f-string evaluates and formats unconditionally. Guard an expensive argument with
`logger.isEnabledFor`.

## Context

`contextvars` is ambient, and the failures are narrower than the JVM's:

- `asyncio` tasks **copy** the current context when created, and `asyncio.to_thread` propagates it, so the common
  async paths are already correct;
- a hand-rolled `ThreadPoolExecutor.submit` does **not** propagate, and that is the case to check;
- a context variable set and not reset through its token leaks into whatever runs next on the same task. Reset
  through the token in a `finally`; the token restores the previous value, so a nested scope is safe.

## Linters and what a clean verdict does not establish

- **Ruff `LOG` family**: root-logger calls, the `getLogger` argument, and `exc_info` misuse. No Ruff rule reports
  a configuration call in library code or a private null-handler class; the reviewer reads for them.
- **Ruff `G` family**: f-string and `%`-outside-the-call formatting in a log call.
- **Ruff `TRY400` / `TRY401`**: `error` where `exception` belongs, and the exception object duplicated into the
  message text. Neither reports a log followed by a raise.
- Most of the `G` and `TRY` families are off in Ruff's default rule set, so a passing `ruff check` says nothing about
  them unless the project selected them.
- None of them reports a missing joining identifier, a record that names inputs instead of the branch, an unbounded
  metric label, or a private setting name in the message text.
