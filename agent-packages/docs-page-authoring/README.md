# docs-page-authoring

An APM package that governs **what a documentation page says, for whom, in what order, and what it may not claim**: a
README, a reference or options page, a feature page or how-to, a tutorial, a troubleshooting page, a migration guide.

The rules are organized by reader. A page is not read; a section is, by someone who arrived with a question and leaves
when it is answered. The skill fixes seven such readers, each holding one thing and asking one question: the evaluator
with a requirement, the first-time integrator with an empty project, the task-doer with a goal, the configurer with a
config file, the troubleshooter with an error message, the upgrader with two versions, and the contributor with a clone.
Every rule names the reader whose question it answers.

## What it covers

- The seven readers, what each one holds, which page each one opens, and what each one asks.
- The slots of a section (claim, contract, rationale, use) and of an option entry (name and default with its unit, what
  it controls, values, scope, what happens at the limit, interactions, when to change it, version), in the order that
  serves the reader who arrives mid-page.
- The promise rather than the code: the refactoring test that separates a contract from a description of the current
  implementation, and the three places history may live (a changelog, a migration guide, a named version marker).
- Where a reader enters a page, why the first paragraph of every section has to stand alone, and when a topic earns a
  heading, a table row, or a table.
- One primary purpose per section, the failure mode of each genre, and where a fact lives when a docs set carries it in
  several places: one copy is the record, the others summarize and link.
- Headings as URL anchors, and why a heading rename is a separate change with its redirect.
- Claims a machine could check: names, numbers, quoted errors, and fenced examples, with the doctest harnesses that turn
  a fence into a test.
- What a change owes the documentation: a scan table from the kind of change in the diff to the reader and the page it
  owes an entry.
- The two editing modes (a prose pass and a structural revision), how far a rewrite may grow, and how to compare two
  versions of a page without being sold by the newer one.

## Contents

- `.apm/instructions/docs-page-authoring.instructions.md`: the trigger merged into `AGENTS.md` / `CLAUDE.md` by
  `apm compile`.
- `.apm/skills/docs-page-authoring/SKILL.md`: the on-demand rules, a review checklist, and a worked example of an option
  entry. It carries no citations; the evidence stays in the research directory below.

## Pairs with

- [`english-developer-style`](../english-developer-style/) owns wording, tone, sentence length, and dialect. This
  package decides which sections and sentences exist and for whom; that one writes them. Install both.
- [`change-description-authoring`](../change-description-authoring/) owns the changelog entry and the pull request
  description, which are written from the reference entry this package governs and link back to it.
- [`javadoc-authoring`](../javadoc-authoring/) and its siblings govern the doc comment, which often ships as the
  generated reference a page links to rather than repeats.

## Research

The rules were synthesized from genre frameworks (Diátaxis), the structure chapters of editorial style guides, project
contribution guides (Kubernetes, PostgreSQL, OpenStack, Rust, Go), the normative-versus-informative discipline of
standards bodies, doctest tooling, and the research literature on how developers find and read documentation, then
tested twice on a real branch that added connection properties and error messages to a JDBC driver. The evidence, the
sources with URLs, and the conflicts between them are in
[`research/docs-page-authoring/`](../../research/docs-page-authoring/README.md).

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/docs-page-authoring
```

Or add it to your `apm.yml` by hand:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/docs-page-authoring@<ref>
```

Replace `<ref>` with the release tag, branch, or commit SHA you want to pin, for example `v1.2.0`.

Then run `apm install` and `apm compile` to merge the trigger into your local `AGENTS.md` / `CLAUDE.md` and deploy the
skill body where your agent reads it (`.agents/skills/`, `.claude/skills/`, `.cursor/`, ...).
