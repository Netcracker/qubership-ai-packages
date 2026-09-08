# javadoc-authoring

An APM package that governs **what a doc comment says and in what order**. It is written for Javadoc and holds for the
JVM's other doc-comment dialects, KDoc, Groovydoc, and Scaladoc, which share its tag vocabulary and its summary-table
rendering.

The skill starts from a correction. "Document the why, not the what" is half wrong for a doc comment: an inline `//`
comment carries the why, while a doc comment carries the **contract**: what a caller may rely on, what an implementer
must guarantee, what holds before and after. The test for a sentence is the refactor, not the reader: rewrite the body
so it behaves identically, and every sentence you would then have to edit was implementation.

## What it covers

- The four content slots (summary, contract, rationale, use) and the order they go in, with the obligated party as the
  subject of every stated obligation.
- The summary-fragment rule for the first sentence, including the terminating period that `e.g.` cuts short, and the
  first sentence a reader could reconstruct from the member's name.
- What belongs in a class comment, in a member comment, and in the PR description instead; the history a comment may
  not narrate, and the one exception for the comment on a regression test.
- The counterfactual: a comment that describes what the code would do on a path it refuses, and the test that catches
  it.
- The three cases of an override (obeys the inherited contract, picks a behavior it left open, breaks it), and why a
  tag written on an override replaces the inherited one rather than adding to it.
- `{@link}` and `{@code}` versus positional references such as "see below", how far doclint's checking reaches, and why
  an issue number is an address rather than a definition.
- When `@param`, `@return`, and `@throws` earn their line, and when they are noise a checkstyle rule demands.
- Comments a tool rather than a human reads (`CHECKSTYLE:OFF`, `@formatter:off`, `$NON-NLS-`) and the two ways a
  reflow silently breaks one.
- Why a list of members should usually be the rule that defines them, and the one question that decides which.
- What changes when the comment ships as documentation: published javadoc pages, or a description a generator lifts
  into an OpenAPI spec.
- How far a rewrite may grow, how to compare two versions without being sold by the newer one, and how to prove a
  comment-only sweep moved no code.
- The extra rules for test classes, including the four things that make a failing test read as a bug report, and for
  `package-info.java`.

## Scope

The JVM family only. Other languages need their own rules rather than a translation of these: Python's PEP 257 asks
for the imperative `Return that` where Javadoc asks for `Returns that`, and Rust, TypeScript, and JavaScript each have
reference and tag machinery this skill does not describe. Each of them has its own package:
[`pythondoc-authoring`](../pythondoc-authoring/), [`rustdoc-authoring`](../rustdoc-authoring/), and
[`jsdoc-authoring`](../jsdoc-authoring/).

## Contents

- `.apm/instructions/javadoc-authoring.instructions.md`: the trigger merged into `AGENTS.md` / `CLAUDE.md` by
  `apm compile`.
- `.apm/skills/javadoc-authoring/SKILL.md`: the on-demand rules, a review checklist, and two worked examples that pull
  in opposite directions.

## Pairs with

- [`english-developer-style`](../english-developer-style/) owns wording, tone, sentence length, and dialect. This
  package picks the slots; that one writes the sentences. Install both.
- [`godoc-authoring`](../godoc-authoring/), [`pythondoc-authoring`](../pythondoc-authoring/),
  [`rustdoc-authoring`](../rustdoc-authoring/), and [`jsdoc-authoring`](../jsdoc-authoring/) are the Go, Python, Rust,
  and JavaScript and TypeScript equivalents. All keep the same section numbering, so a review that cites "§7b" means
  the same rubric in any of the five.

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
