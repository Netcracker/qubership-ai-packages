# Axis: API usability — for humans and for agents

Finding prefix: `UX`.

Two readers with the same handicap: neither has read the source. A developer has an IDE, the docs, and autocomplete;
an AI agent has the signatures, the doc comments, the `--help` output, or the tool schema. Both must be able to use
this thing correctly on the first attempt, and both must be able to tell a mistake from a failure.

Judge the surface, not the implementation. Every finding here is about what the caller sees.

**Surface packs come first.** This file holds what is true of every API form. The conventions, the normative source,
and the tooling for a *particular* form live in `references/surfaces/<form>.md`, and where a pack exists it wins over
anything below — including the CLI and MCP sections, which stay here only until packs replace them. The pack also
carries an ownership table: on the Kubernetes surface, for example, the condition vocabulary belongs to `error-model`
and CRD versioning to `api-compatibility`, however much they feel like API usability. Do not report those here.

## Naming and shape

- Does each name say what the thing does, in the vocabulary of the domain, and does the same concept carry the same
  name everywhere? Two names for one concept, or one name for two concepts, is the most expensive defect on this axis.
- Do names match the ecosystem's expectations — the conventions of the standard library and of the frameworks a caller
  already knows? A method called `get` that blocks, a `create` that is idempotent, or a `close` that does not release
  will be misused.
- Boolean parameters and long positional lists: at a call site, can a reader tell what `f(x, true, false, null)`
  means? Are there overloads that differ only by a type a caller can get wrong silently?
- Is the type system doing the work it could — distinct types instead of strings, enums instead of magic values,
  required arguments instead of validated-at-runtime nulls?
- Is the obvious path the correct path? Rate the API by what a caller does when they do not read the docs: if the
  natural call leaks a resource, skips validation, or blocks the wrong thread, the API is the defect.

## Discoverability

- Can a caller find the entry point from the package or module listing alone? Is there one obvious way in, or five
  plausible ones?
- Do doc comments state the contract — units, nullability, thread-safety, ownership, what is retained, what throws —
  or do they restate the signature?
- Are examples present, current, and compilable? A README example that no longer compiles is a finding.

## CLI surface (when there is one)

`references/surfaces/cli.md` owns this surface — read it instead of the summary below, which stays only as a reminder
of what the pack covers: `--help` on the root and on every subcommand, with every option the subcommand accepts shown
there; each option documented with its default, its unit, and its allowed values; consistent flag and placeholder
names across the whole tree; `--version`; a machine-readable output mode that is stable and documented; output small
enough to be cheap to read. Exit codes, stream discipline, and what happens on a typo belong to `error-model` on that
surface — the pack's ownership table routes them. Check that the help text and the parser agree by running the
commands; on this surface almost every claim can be executed rather than traced.

## MCP / tool surface (when there is one)

Tool names that say what the tool does, not how it is implemented; descriptions that state when to use the tool and
when not to; parameter schemas with descriptions, enums, and defaults; no two tools whose descriptions overlap so a
model must guess; errors returned as structured, actionable text rather than a stack trace; idempotency and side
effects stated explicitly; output small enough to be usable and truncation that announces itself.

## Predictability

- Same input, same output? Any hidden dependence on ambient state — locale, default charset, time zone, working
  directory, environment variables, static mutable state — is a finding.
- Are failures uniform in shape across the surface, so a caller can handle them in one place? (Depth belongs to
  `error-model`; here, judge only the consistency a caller sees.)
- Is there any operation that succeeds partially and reports success?

## Method

Use the thing without reading its source. Write a small program, or run the CLI, against the docs alone, and record
every point where you had to guess or were wrong. That transcript is the strongest evidence this axis can produce —
include it.
