# JVM mechanics

Read with `SKILL.md`. This file carries what the JVM answers differently; the rules themselves are in the body.

## What the host sees when it has configured nothing

**A one-time diagnostic, then nothing.** With the SLF4J API on the classpath and no provider, the facade prints a few
lines on standard error saying that no provider was found, then switches to a no-operation implementation that
discards every request. So a library may promise a host that its log records are discarded after that diagnostic. It
may promise complete silence only where the host installs the NOP provider explicitly.

## Deciding where output goes (§6)

Routing is **by name**, so the deciding call is a configuration call.

| Detection | What it looks like |
| --- | --- |
| Configuration call in library code | `BasicConfigurator`, `Configurator.initialize`, `LogManager.readConfiguration`, `setLevel`, `addAppender`, `addHandler` |
| Provider in the build | Any binding or provider artifact at compile or runtime scope. Only `slf4j-api` (or `log4j-api`, or `System.Logger` from `java.base`) belongs at compile scope; the provider belongs at `test` scope |
| `optional` in the build script | Read the **published** POM: an `optional` declaration in Gradle still reaches a host that copies the dependency block |

Obtaining a logger is `LoggerFactory.getLogger(Foo.class)` or `System.Logger` from `java.base`, and it carries no
routing decision: the host configures by the name this produces.

## Metrics from a library

Two shapes, and both are in rule:

- **A no-op-by-default registry.** Micrometer's global registry is a composite whose increments do nothing until the
  host adds a registry to it. The OpenTelemetry metrics API is a no-op without an SDK.
- **A hook the host implements.** HikariCP publishes a metrics-tracker factory interface and ships the Micrometer and
  Dropwizard adapters as separate artifacts. This is the shape to copy where no no-op-by-default API exists.

Picking a concrete registry inside library code is the defect, and a hook published beside a default registration in a
static initializer is the same defect.

## Numbers in a message

`java.util.logging.Logger.log` with an `Object[]` renders through `java.text.MessageFormat`, which groups digits by
locale and treats a single quote as the start of a literal. SLF4J's `{}` placeholders do not go through
`MessageFormat`. The repair is in `english-developer-style` §5: pass the digits as text, and keep apostrophes out of
a pattern.

## Structured fields

SLF4J's `{}` placeholders interpolate into the message; key-value pairs are the field mechanism where the provider
supports them. In a repository that logs structurally, a value the reader filters on goes in a pair, not in the text.

## Guards

The argument expression is evaluated before the call, so wrap an expensive argument in `isDebugEnabled()` or the
equivalent. SLF4J's `{}` form defers the string concatenation but not a method call inside the argument list.

## Context

Two ambient contexts cross thread boundaries here, and each has its own mechanism.

**MDC** is thread-local and has two failures:

- **Not inherited.** Threads managed by `java.util.concurrent.Executors` do not inherit the mapped diagnostic context
  of the submitting thread. Carry it with `getCopyOfContextMap` and `setContextMap` across the boundary.
- **Stale or clobbered.** A pooled thread keeps the previous unit's keys, which leads the reader to the wrong request;
  and a nested scope that overwrites a key the caller set corrupts the caller's later records if it removes the key
  instead of restoring it. The repair is that a `put` saves the previous value and restores it in a `finally` on
  every exit path; `remove` or `clear` is right only at the outermost scope. Detection: a `put` with no restore in a
  `finally`, or a `remove` inside a nested scope.

**The OpenTelemetry context** is separate from MDC: copying the MDC map does not carry the active span. Make a context
current with `try (Scope ignored = context.makeCurrent())`, which restores the previous context when the scope
closes, and wrap executors with `Context.taskWrapping(executor)` or tasks with `Context.current().wrap(runnable)` so
the span crosses the pool. Detection: a `makeCurrent()` outside a try-with-resources, or a task submitted to a pool
without wrapping.

## Linters and what a clean verdict does not establish

- **Sonar S2139** reports logging and rethrowing the same exception. A clean verdict does not establish that the
  handler is adequate, only that it does not duplicate the record.
- Error Prone and SpotBugs carry assorted logging checks; none of them reports a missing identifier, a record that
  names inputs instead of the branch, or a private field name in the message text. Those three stay with the
  reviewer.
