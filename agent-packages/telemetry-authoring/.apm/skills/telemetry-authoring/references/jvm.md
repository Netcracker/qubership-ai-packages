# JVM mechanics

Read with `SKILL.md`. This file carries what the JVM answers differently; the rules themselves are in the body.

## What the host sees when it has configured nothing

**Nothing.** With the SLF4J API on the classpath and no provider, the facade falls back to a no-operation
implementation: one warning on startup, and every subsequent request discarded. The JVM is the only one of the three
ecosystems where "a library that logs leaves a silent host silent" is true, so it is also the only one where a
library may promise it.

## Deciding where output goes (§6)

Routing is **by name**, so the deciding call is a configuration call.

| Detection | What it looks like |
| --- | --- |
| Configuration call in library code | `BasicConfigurator`, `Configurator.initialize`, `LogManager.readConfiguration`, `setLevel`, `addAppender`, `addHandler` |
| Provider in the build | Any binding or provider artifact at compile or runtime scope. Only `slf4j-api` (or `log4j-api`, or `System.Logger` from `java.base`) belongs at compile scope; the provider belongs at `test` scope |
| Gaming: `optional` | Read the **published** POM, not the build DSL: an `optional` declaration in Gradle still reaches a host that copies the dependency block |

Obtaining a logger is `LoggerFactory.getLogger(Foo.class)` or `System.Logger` from `java.base`, and it carries no
routing decision: the host configures by the name this produces.

## Metrics from a library

Two shapes, and both are in rule:

- **A no-op-by-default registry.** Micrometer's global registry is a composite whose increments do nothing until the
  host adds a registry to it, which satisfies "emit only through an API whose default is a no-op".
- **A hook the host implements.** HikariCP publishes a metrics-tracker factory interface and ships the Micrometer and
  Dropwizard adapters as separate artifacts. This is the shape to copy where no no-op-by-default API exists.

Picking a concrete registry inside library code is the defect. Naming a hook and also registering a default in a
static initializer satisfies the letter; the registration call is the evidence.

## Numbers in a message

`java.util.logging.Logger.log` with an `Object[]` renders through `java.text.MessageFormat` whenever the message
contains `{` followed by a digit, and `MessageFormat` formats numeric arguments through the locale's number format.
`103887667` prints as `103,887,667` under `en-US` and `103 887 667` under `fr`, so neither string matches the source,
the configuration file, or the other reader's bug report.

Pass the digits as text at the call site: `String.valueOf(n)`, `Long.toString(n)`, `Long.toUnsignedString(n)` for a
value the signed type cannot hold. Where the argument has to stay numeric, `{0,number,#}` suppresses grouping. SLF4J's
`{}` placeholders do not go through `MessageFormat` and are not affected.

The same formatter treats a single quote as opening a quoted literal, so an apostrophe in the message text stops the
placeholders after it from being substituted. The developer-style skill of the language the message is written in
covers the wording repair (`english-developer-style` §5 for English).

## Structured fields

SLF4J's `{}` placeholders interpolate into the message; key-value pairs are the field mechanism where the provider
supports them. In a repository that logs structurally, a value the reader filters on goes in a pair, not in the text.

## Guards

The argument expression is evaluated before the call, so wrap an expensive argument in `isDebugEnabled()` or the
equivalent. SLF4J's `{}` form avoids the string concatenation but not a method call inside the argument list.

## Context

`MDC` is ambient and thread-local, and it has **two** failures, not one:

- **Not inherited.** A copy of the mapped diagnostic context is not always inherited by worker threads from the
  initiating thread, and `java.util.concurrent.Executors`-managed threads are the documented case. Carry it with
  `getCopyOfContextMap` and `setContextMap` across the boundary.
- **Stale.** A pooled thread keeps the previous unit's keys, which leads the reader to the wrong request. This is
  worse than an empty context, and the repair is that a `put` is balanced by a `remove` or a `clear` on every exit
  path. Detection: a `put` with no matching removal in a `finally`.

## Linters and what a clean verdict does not establish

- **Sonar S2139** reports logging and rethrowing the same exception. A clean verdict does not establish that the
  handler is adequate, only that it does not duplicate the record.
- Error Prone and SpotBugs carry assorted logging checks; none of them reports a missing identifier, a record that
  names inputs instead of the branch, or a private field name in the message text. Those three stay with the
  reviewer, and both recorded failures behind this skill were of exactly that kind.
