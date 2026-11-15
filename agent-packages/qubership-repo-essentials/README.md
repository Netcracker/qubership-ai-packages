# qubership-repo-essentials

APM package with the baseline agent setup for new Netcracker/Qubership repository installations. Depend on this one
package and the agent picks up the shared conventions through the package's backward-compatibility rule and
transitive APM dependencies.

The deprecated [`qubership-essentials`](../qubership-essentials/) package
remains available with its original dependency set for existing consumers.
This package states the repository installation scope explicitly and excludes
`codex-review`; depend on [`codex-review`](../codex-review/) directly if your
repository wants agent-run Codex reviews.

## What it includes

The package tells the agent to keep released contracts backward compatible: a contract present in a release tag keeps
working, and a removal needs a deprecation at least 3 years old and a new major version. This rule applies in a
repository and is not part of `qubership-user-essentials`, which a developer installs for every repository on the
machine.

Everything else comes from [`qubership-common-essentials`](../qubership-common-essentials/), the base shared with
`qubership-user-essentials`: Conventional Commits with an `Assisted-by:` trailer, `apm-authoring`,
`english-us-developer-style`, `markdown-line-length-120`, `change-description-authoring`, `docs-page-authoring`, and
`qubership-workflow-hub-usage`.

## Adding a package to the bundle

A package that belongs on a developer machine too goes to `qubership-common-essentials`. A package for repositories
only goes here: add the dependency to `apm.yml` and bump the version. Consumers pick up the new member on their next
`apm update`.
