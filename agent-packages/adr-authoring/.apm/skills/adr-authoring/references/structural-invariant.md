# Keep the `core` projects free of dependencies on the `web` projects and on HTTP servers

## Status

Accepted

### Date

2026-03-02

### Owner

`example-architect`

### Participants and approvers

- Architect, `example-architect`: approves R1 to R3.
- Build maintainer, `example-build-maintainer`: approves the check under **Confirmation**.

## Context

The repository builds one service from Gradle projects under `core/` and `web/`. The `core` projects hold the billing
rules, and the `web` projects hold the HTTP API, built on Ktor. Two classes in `core/billing` import Ktor's
`HttpStatusCode`, so `core/billing` declares a dependency on `web/http`. A change to the HTTP stack recompiles and
retests the billing rules, and the nightly batch job, which runs without an HTTP server, cannot use `core/billing`
without pulling Ktor in.

## Decision

We will keep every `core` project free of dependencies on the `web` projects and on libraries that provide an HTTP
server.

### Terms

- **core project**: a Gradle project whose directory is under `core/`.
- **web project**: a Gradle project whose directory is under `web/`.
- **depends on**: a Gradle project depends on another project or on a library when its build file declares it in any
  configuration, or when a project or a library it depends on does.
- **core-allowed-libraries**: the libraries listed in `gradle/core-allowed-libraries.txt`. R3 states what a library
  needs to join.

### Rules

#### Dependencies of the core projects

- **R1** (`core`). No core project depends on a web project.
- **R2** (`core`). A core project depends on a library from outside the repository only where the library is in
  core-allowed-libraries.

#### The allowed libraries

- **R3** (`build`). A library joins core-allowed-libraries only where no artifact on its runtime classpath provides an
  HTTP server, and the owner of this record approves the pull request that adds it.

### Confirmation

- **R1**: the Gradle task `:build-logic:verifyCoreDependencies`, which `./gradlew check` runs on every pull request,
  fails when the resolved dependencies of a core project include a web project.
- **R2**: the same task fails when they include a library that `gradle/core-allowed-libraries.txt` does not list.

### Implementation notes

Adds no requirement. Replace the two uses of `HttpStatusCode` in `core/billing` with a result type of `core/billing`
itself, and let `web/api` map that type to a status code. Then remove the dependency on `web/http` from
`core/billing/build.gradle.kts`, and list the libraries the core projects use today in
`gradle/core-allowed-libraries.txt`.

### Justification

The batch job can use the billing rules only if no core project brings an HTTP server with it (R1, R2). A list in a
file lets a library join in one pull request, where a list in this record would take a new record for each library
(R2, R3).

### Alternatives considered

- **A1. Let a core project declare a web project as long as no core class imports from it.** Rejected by R1: the
  declaration still puts the web project, and Ktor with it, on the core project's classpath.
- **A2. Merge the `core` and `web` projects into one project with a package per layer.** The batch job would then
  build and ship the HTTP stack.

## Consequences

Positive:

- A core project can be published as a library for other services, since it brings no HTTP server with it.

Negative:

- A library that brings an HTTP server on its runtime classpath, such as a client SDK with an embedded callback server,
  cannot be used in a core project (R3).

Follow-ups:

- Map `gradle/core-allowed-libraries.txt` to the `build` layer in the reading guide.
