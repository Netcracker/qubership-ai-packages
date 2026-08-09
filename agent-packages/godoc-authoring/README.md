# godoc-authoring

An APM package that governs **what a Go comment says and in what order** — both a doc comment on a declaration and an
inline `//` comment inside a function.

It is the Go sibling of [`javadoc-authoring`](../javadoc-authoring/) and keeps its section numbering, so a review that
cites "§7b" means the same rubric in either language. The slot model transfers unchanged; the reference and tag
sections do not, because Go puts the identifier's name in the first sentence, replaces `{@link}` with an unchecked
bracket syntax, and has no tags at all.

## What it covers

- The four content slots — summary, contract, rationale, use — and the order they go in.
- Why the first sentence begins with the name being declared, and why a Kubernetes API field opens with its JSON name
  instead.
- Doc links (`[Client.Do]`) versus bare names, and the fact that nothing fails the build when a doc link does not
  resolve.
- What replaces Javadoc's tags: named results, errors named in prose, and the `Deprecated:` paragraph that tooling
  actually reads.
- Why a list of members should usually be the rule that defines them, and the wider vocabulary exception for a comment
  that ships to users.
- Comments a tool rather than a human reads — `//go:`, `//nolint`, `+kubebuilder` — including the blank line that
  silently detaches a marker from its field.
- How far a rewrite may grow, and how to compare two versions of a comment without being sold by the newer one.
- The extra rules for tests, package comments, and CRD field descriptions that reach users through `kubectl explain`.

## Contents

- `.apm/instructions/godoc-authoring.instructions.md` — the trigger merged into `AGENTS.md` / `CLAUDE.md` by
  `apm compile`.
- `.apm/skills/godoc-authoring/SKILL.md` — the on-demand rules, a review checklist, and two worked examples that pull
  in opposite directions.

## Pairs with

- [`english-developer-style`](../english-developer-style/) owns wording, tone, sentence length, and dialect. This
  package picks the slots; that one writes the sentences. Install both.
- [`javadoc-authoring`](../javadoc-authoring/) covers the JVM family — Javadoc, KDoc, Groovydoc, and Scaladoc.
- [`rustdoc-authoring`](../rustdoc-authoring/) covers Rust, where doc examples compile and run as tests.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/godoc-authoring
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/godoc-authoring@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin, for example `v1.2.0`.

Then run `apm install` and `apm compile` to merge the trigger into your local `AGENTS.md` / `CLAUDE.md` and deploy the
skill body where your agent reads it (`.agents/skills/`, `.claude/skills/`, `.cursor/`, ...).
