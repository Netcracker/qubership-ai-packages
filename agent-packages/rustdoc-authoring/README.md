# rustdoc-authoring

An APM package that governs **what a Rust comment says and in what order** — a `///` or `//!` doc comment, an inline
`//` comment, and the `// SAFETY:` comment above an `unsafe` block.

It is the Rust sibling of [`javadoc-authoring`](../javadoc-authoring/) and [`godoc-authoring`](../godoc-authoring/) and
keeps their section numbering, so a review that cites "§7b" means the same rubric in any of the three. The slot model
transfers unchanged. Three things do not, and they are why this package exists: Rust's type system carries much of what
a Java or Go comment states in prose, a doc example compiles and runs as a test, and no stable formatter touches a doc
comment.

## What it covers

- The four content slots — summary, contract, rationale, use — and the order they go in.
- Why the summary boundary is a blank `///` line rather than a period, so `e.g.` costs nothing and a second sentence
  costs the whole item-table row.
- What `Option`, `Result`, `&mut`, and a trait bound already say, so the comment does not — and the list of contract
  facts that survives that cut: panics, error meanings, cancellation safety, laziness, complexity, `Drop`.
- `# Errors`, `# Panics`, `# Safety`, and `# Examples` — the conventional headings that replace Javadoc's tags, and
  which of them a lint actually enforces.
- `# Safety` on an `unsafe fn` (the caller's obligations) versus on an `unsafe trait` (the implementer's), and the
  `// SAFETY:` comment that argues one call site satisfies them.
- Doc examples as tests: the untagged fence and the four-space-indented block that get compiled as Rust by accident,
  `?` in an example, hidden `#` lines, why `ignore` rots, and the two surprises about which doctests run at all.
- Intra-doc links, the disambiguators a language with same-named structs and functions needs, and the rustdoc lints
  that check them — the one place Rust is stricter than Go.
- What a trait comment owes implementers it will never see.
- How far a rewrite may grow, why a comment-only edit can still break a Rust build, and how to prove a sweep moved no
  code.
- The extra rules for tests, module and crate comments, and docs that ship to docs.rs.

Every mechanical claim in the skill was measured on rustc / cargo 1.92.0, clippy 0.1.92, and rustfmt 1.8.0.

## Contents

- `.apm/instructions/rustdoc-authoring.instructions.md` — the trigger merged into `AGENTS.md` / `CLAUDE.md` by
  `apm compile`.
- `.apm/skills/rustdoc-authoring/SKILL.md` — the on-demand rules, a review checklist, and two worked examples
  that pull in opposite directions.

## Pairs with

- [`english-developer-style`](../english-developer-style/) owns wording, tone, sentence length, and dialect. This
  package picks the slots; that one writes the sentences. Install both.
- [`javadoc-authoring`](../javadoc-authoring/) covers the JVM family — Javadoc, KDoc, Groovydoc, and Scaladoc.
- [`godoc-authoring`](../godoc-authoring/) covers Go.
- [`pythondoc-authoring`](../pythondoc-authoring/) covers Python, where the docstring is a runtime object and two style
  guides disagree about the mood of its first line.
- [`jsdoc-authoring`](../jsdoc-authoring/) covers JavaScript and TypeScript, where a type in a tag is noise in one and
  code in the other.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/rustdoc-authoring
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/rustdoc-authoring@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin, for example `v1.2.0`.

Then run `apm install` and `apm compile` to merge the trigger into your local `AGENTS.md` / `CLAUDE.md` and deploy the
skill body where your agent reads it (`.agents/skills/`, `.claude/skills/`, `.cursor/`, ...).
