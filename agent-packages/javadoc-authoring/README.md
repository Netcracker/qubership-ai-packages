# javadoc-authoring

An APM package that governs **what a doc comment says and in what order**. It is written for Javadoc and holds for the
JVM's other doc-comment dialects — KDoc, Groovydoc, and Scaladoc — which share its tag vocabulary and its
summary-table rendering.

The skill starts from a correction. "Document the why, not the what" is half wrong for a doc comment: an inline `//`
comment carries the why, while a doc comment carries the **contract** — what a caller may rely on, what an implementer
owes, what holds before and after.

## What it covers

- The four content slots — summary, contract, rationale, use — and the order they go in.
- The summary-fragment rule for the first sentence, including the terminating period that `e.g.` cuts short.
- What belongs in a class comment, in a member comment, and in the PR description instead.
- `{@link}` and `{@code}` versus positional references such as "see below", and how far doclint's checking actually
  reaches.
- When `@param`, `@return`, and `@throws` earn their line, and when they are noise a checkstyle rule demands.
- Comments a tool rather than a human reads — `CHECKSTYLE:OFF`, `@formatter:off`, `$NON-NLS-` — and the two ways a
  reflow silently breaks one.
- Why a list of members should usually be the rule that defines them, and the two cases where the list stays.
- What changes when the comment ships as documentation: published javadoc pages, or a description a generator lifts
  into an OpenAPI spec.
- How far a rewrite may grow, how to compare two versions without being sold by the newer one, and how to prove a
  comment-only sweep moved no code.
- The extra rules for test classes and `package-info.java`.

## Scope

The JVM family only. Other languages need their own rules rather than a translation of these — Python inverts the
first-sentence rule outright (PEP 257 asks for the imperative `Return that`), and Rust, TypeScript, and JavaScript
each have reference and tag machinery this skill does not describe.

## Contents

- `.apm/instructions/javadoc-authoring.instructions.md` — the trigger merged into `AGENTS.md` / `CLAUDE.md` by
  `apm compile`.
- `.apm/skills/javadoc-authoring/SKILL.md` — the on-demand rules, a review checklist, and two worked examples that
  pull in opposite directions.

## Pairs with

- [`english-developer-style`](../english-developer-style/) owns wording, tone, sentence length, and dialect. This
  package picks the slots; that one writes the sentences. Install both.
- [`godoc-authoring`](../godoc-authoring/) is the Go equivalent. It keeps the same section numbering, so a review that
  cites "§7b" means the same rubric in either language.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/javadoc-authoring
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/javadoc-authoring@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin, for example `v1.2.0`.

Then run `apm install` and `apm compile` to merge the trigger into your local `AGENTS.md` / `CLAUDE.md` and deploy the
skill body where your agent reads it (`.agents/skills/`, `.claude/skills/`, `.cursor/`, ...).
