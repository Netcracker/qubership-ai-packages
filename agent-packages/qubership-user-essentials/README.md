# qubership-user-essentials

Umbrella APM package with the Qubership agent setup for a global user workspace. Install it once per developer machine
so your agent uses the same baseline across repositories.

Use this package for new user-workspace installations. The deprecated
[`qubership-global-essentials`](../qubership-global-essentials/) package remains available for existing consumers.
This package nests [`qubership-repo-essentials`](../qubership-repo-essentials/) and adds
the packages that only make sense user-wide. Through the repository baseline it also carries
`qubership-workflow-hub-usage`.

## Install

Register the marketplace first:

```sh
apm marketplace add Netcracker/qubership-ai-packages
```

Then choose the agent harnesses you use and install the package globally. This example uses the default Qubership
targets; replace `--target` with the harnesses you use:

```sh
apm install qubership-user-essentials@qubership-ai-packages --target claude,codex,cursor -g
apm compile -g
```

`apm install -g` does not write user-scope root context files. Run `apm compile -g` after installing this package so
global instructions reach targets that read files such as `~/.codex/AGENTS.md` or `~/.claude/CLAUDE.md`. See the
[APM compile guide](https://microsoft.github.io/apm/producer/compile/) and the placement discussion in
[microsoft/apm#1807](https://github.com/microsoft/apm/issues/1807).

## What it pulls in

- [`qubership-repo-essentials`](../qubership-repo-essentials/) — the per-repository baseline: `apm-authoring`,
  `english-us-developer-style`, `markdown-line-length-120`, and `qubership-workflow-hub-usage`.
- [`qubership-agent-support-pr`](../qubership-agent-support-pr/) — create a PR that adds Qubership baseline agent
  support to a repository.
- [`triage-dependency-prs`](../triage-dependency-prs/) — triage failing checks on Renovate and Dependabot PRs.
- [`enable-renovate-automerge`](../enable-renovate-automerge/) — enable Renovate automerge behind a real required
  check.
- [`adr-authoring`](../adr-authoring/) — write Architecture Decision Records that follow the Qubership ADR contract.
- [`javadoc-authoring`](../javadoc-authoring/) — what a doc comment says, and in which order, in Java, Kotlin,
  Groovy, and Scala.
- [`jsdoc-authoring`](../jsdoc-authoring/) — the same for JSDoc and TSDoc comments in JavaScript and TypeScript.
- [`godoc-authoring`](../godoc-authoring/) — the same for Go doc comments and inline comments.
- [`rustdoc-authoring`](../rustdoc-authoring/) — the same for Rust doc comments and inline comments.
- [`pythondoc-authoring`](../pythondoc-authoring/) — the same for Python docstrings and inline comments.
- [`problem-report-authoring`](../problem-report-authoring/) — what a bug report, a feature request, or a problem
  message to a colleague establishes and says, before anyone else has to act on it.
- [`telemetry-authoring`](../telemetry-authoring/) — which signal an event owes (a log record, a metric, a span, or
  nothing), what it carries, and what a library may not decide for its host; and what the text of an error tells a
  reader who holds nothing else.
- [`test-authoring`](../test-authoring/) — which tests a change owes, at which level, and how each is shown able to
  fail.
- [`final-review`](../final-review/) — a fresh-context check of a finished change before the commit: comments
  against code, claimed cases against named tests.

## Adding a package to the bundle

Add the dependency to `apm.yml` and bump the version. Consumers pick up the new member on their next `apm update`.
