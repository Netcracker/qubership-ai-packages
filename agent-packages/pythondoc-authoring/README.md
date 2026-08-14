# pythondoc-authoring

An APM package that governs **what a Python comment says and in what order** — both a docstring on a module, class, or
function and an inline `#` comment beside a statement.

It is the Python member of the doc-comment family listed under *Pairs with* and keeps its section numbering, so a
review that cites "§7b" means the same rubric in any of them. The slot model transfers unchanged; the summary,
reference, and section rules do not, because Python argues with itself about the mood of the first line, has no
cross-reference syntax of its own, and offers three competing section dialects instead of one set of tags.

## What it covers

- The four content slots — summary, contract, rationale, use — and the order they go in.
- The one-line summary, and the imperative-versus-descriptive dispute between PEP 257 and Google's style guide,
  including which ruff convention takes which side.
- Why a docstring must be the first statement, and the three ways it stops being one: an f-string, a line above it,
  and `python -OO`.
- What the type annotations already say, so a parameter line has to add a unit, a range, a `None` rule, or nothing.
- The three section dialects — reStructuredText, Google, NumPy — and why mixing them fails silently.
- Sphinx roles and mkdocstrings references, and the fact that nothing resolves either one outside nitpicky mode.
- `Raises:` as the only record of what a caller must catch, and `Yields:` as the place laziness gets stated.
- Doctest examples, which are executable tests hiding inside prose.
- Comments a tool rather than a human reads — `# type: ignore`, `# noqa`, `# fmt: off`, `# pragma: no cover` —
  including the module docstring that silently un-silences a whole file for mypy.
- How far a rewrite may grow, and how to compare two versions without being sold by the newer one.
- The extra rules for tests, packages, and a docstring that ships as `--help` text or an OpenAPI description.

## Contents

- `.apm/instructions/pythondoc-authoring.instructions.md` — the trigger merged into `AGENTS.md` / `CLAUDE.md` by
  `apm compile`.
- `.apm/skills/pythondoc-authoring/SKILL.md` — the on-demand rules, a review checklist, and two worked examples that
  pull in opposite directions.

## Pairs with

- [`english-developer-style`](../english-developer-style/) owns wording, tone, sentence length, and dialect. This
  package picks the slots; that one writes the sentences. Install both.
- [`javadoc-authoring`](../javadoc-authoring/) covers the JVM family — Javadoc, KDoc, Groovydoc, and Scaladoc.
- [`godoc-authoring`](../godoc-authoring/) covers Go doc comments and inline comments.
- [`rustdoc-authoring`](../rustdoc-authoring/) covers Rust, where doc examples compile and run as tests.
- [`jsdoc-authoring`](../jsdoc-authoring/) covers JavaScript and TypeScript, where a type in a tag is noise in one and
  code in the other.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/pythondoc-authoring
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/pythondoc-authoring@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin, for example `v1.2.0`.

Then run `apm install` and `apm compile` to merge the trigger into your local `AGENTS.md` / `CLAUDE.md` and deploy the
skill body where your agent reads it (`.agents/skills/`, `.claude/skills/`, `.cursor/`, ...).
