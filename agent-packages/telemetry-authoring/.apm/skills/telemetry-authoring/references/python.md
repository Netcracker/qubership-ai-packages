# Python mechanics

Read with `SKILL.md`. This file carries what Python answers differently; the rules themselves are in the body.

## What the host sees when it has configured nothing

**Warnings and above, on standard error**, through the last-resort handler. The standard library calls this the best
default behavior, and offers the null handler as an **opt-out** for a library that does not want it, not as a rule
every library must follow. Do not frame attaching a null handler as "so a silent host stays silent"; frame it as
choosing to suppress a default the standard library considers correct.

## Deciding where output goes (§6)

Routing is **by name**, so the deciding call is a configuration call.

| Detection | What it looks like |
| --- | --- |
| Configuring from library code | `logging.basicConfig`, `dictConfig`, `fileConfig`, `setLevel` on a logger the library does not own, `addHandler` with anything but `NullHandler` |
| Logging to the root logger | `logging.info(...)` and friends at module level, rather than through a named logger |

The library obtains its logger with `logging.getLogger(__name__)`, so the host configures it by the package path.

**The private null handler.** Three widely used libraries each defined their own null-handler class, so a host could
not find them with an `isinstance` check against the standard library's. Subclass or use
`logging.NullHandler` itself; a private class with the same name is the defect.

**Fork.** Handler locks held across a fork deadlocked the child process; the standard library now reinitializes them
through the at-fork hooks. A library that holds its own lock around emission owes the same treatment.

## The caller's channel

Python is the only one of the three with a first-class channel for a condition the caller can fix. The standard
library's own routing table puts an avoidable issue that the client application should change into
`warnings.warn(..., DeprecationWarning, stacklevel=2)`, and reserves a warning-level log record for when there is
nothing the client application can do about the situation. Set `stacklevel` so the warning points at the caller's
line rather than the library's.

Detection: a warning-level log call in library code whose text tells the caller to change their code. The warnings
registry deduplicates per call site, so the same condition does not need a rate limit.

## Errors

The same table routes reporting an error about a runtime event to raising an exception, and reserves the error and
exception log levels for suppressing an error without raising. `logger.exception` inside a handler attaches the
traceback; `logger.error(str(e))` discards it and duplicates the message.

## Numbers in a message

Neither `%`-formatting nor the format mini-language's `,` and `_` separators are locale-aware; only the `n`
presentation type is, and a logging call does not reach it by accident. Python has no equivalent of the JVM's
formatter trap.

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
- a context variable set and not reset through its token leaks into whatever runs next on the same task.

## Linters and what a clean verdict does not establish

- **Ruff `LOG` family**: root-logger calls, the `getLogger` argument, the private-null-handler and configuration
  shapes.
- **Ruff `G` family**: f-string and `%`-outside-the-call formatting in a log call.
- **Ruff `TRY400` / `TRY401`**: `error` where `exception` belongs, and the exception object duplicated into the
  message text.
- None of them reports a missing joining identifier, a record that names inputs instead of the branch, an unbounded
  metric label, or a private setting name in the message text.
