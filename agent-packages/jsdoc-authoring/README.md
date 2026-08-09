# jsdoc-authoring

An APM package that governs **what a comment says and in what order** in JavaScript and TypeScript —
both a JSDoc or TSDoc block on a declaration and an inline `//` comment beside a statement.

One package covers both languages because they share one comment syntax, one tag vocabulary, one
Markdown body, and one language service behind the editor hover where most readers meet the comment.
TSDoc is the standardized subset API Extractor and TypeDoc read; JSDoc is the older, looser superset.
The skill says which is which wherever they disagree.

It is the JavaScript sibling of [`javadoc-authoring`](../javadoc-authoring/),
[`godoc-authoring`](../godoc-authoring/), and [`rustdoc-authoring`](../rustdoc-authoring/), and keeps their section
numbering, so a review that cites "§7b" means the same rubric in any of the four. The slot model transfers unchanged;
the summary, reference, and tag sections do not.

## The rule that inverts

The skill's §3a is the reason an agent that writes both languages needs it. A type inside a tag is
noise in a `.ts` file and is **code** in a `.js` file the project type-checks:

- in `.ts`, `@param {string} name` restates the signature, and a `@param` naming a parameter that no
  longer exists compiles clean — measured on TypeScript 5.9.3 and 7.0.2;
- in `.js` under `checkJs`, the same tag is the file's type annotation, a mismatched argument is
  `error TS2345`, and a stale `@param` name is `error TS8024`.

So the same edit is a comment-only change in one file and a code change in the next, and a sweep
that does not know the difference is unreviewable.

## What it covers

- The four content slots — summary, contract, rationale, use — and the order they go in.
- Where the summary section ends: at the first block tag, not the first period, so `e.g.` is
  harmless and a missing `@remarks` puts four paragraphs on every index page.
- `{@link}`, backticks, and what actually checks a link — not the compiler, sometimes TypeDoc,
  sometimes API Extractor, always the editor hover.
- Which tags earn their line, in a hover where the type is already three characters away.
- Comments a tool rather than a human reads — `@ts-expect-error`, `eslint-disable-next-line`,
  `/*#__PURE__*/`, `@type` casts, release tags — and the four ways a reflow breaks one.
- Why a list of members should usually be the rule that defines them, and why a union type is the
  exception.
- What changes when the comment ships: a `.d.ts` hover, a TypeDoc page, an API Extractor report, a
  generated OpenAPI description. Including the release tag that deletes a declaration from the
  published types.
- How far a rewrite may grow, how to compare two versions without being sold by the newer one, and
  why the usual strip-the-comments proof is incomplete for checked JavaScript.
- The extra rules for tests, where the `it` string is the comment, and for module documentation.

## Contents

- `.apm/instructions/jsdoc-authoring.instructions.md` — the trigger merged into `AGENTS.md` /
  `CLAUDE.md` by `apm compile`.
- `.apm/skills/jsdoc-authoring/SKILL.md` — the on-demand rules, a review checklist, and two worked
  examples that pull in opposite directions.

## Pairs with

- [`english-developer-style`](../english-developer-style/) owns wording, tone, sentence length, and
  dialect. This package picks the slots; that one writes the sentences. Install both.
- [`javadoc-authoring`](../javadoc-authoring/) covers the JVM family, [`godoc-authoring`](../godoc-authoring/) covers
  Go, [`pythondoc-authoring`](../pythondoc-authoring/) covers Python, and
  [`rustdoc-authoring`](../rustdoc-authoring/) covers Rust. All five share the section numbering.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/jsdoc-authoring
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/jsdoc-authoring@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin, for example `v1.2.0`.

Then run `apm install` and `apm compile` to merge the trigger into your local `AGENTS.md` /
`CLAUDE.md` and deploy the skill body where your agent reads it (`.agents/skills/`,
`.claude/skills/`, `.cursor/`, ...).
