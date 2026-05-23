---
name: english-prose-style
description: English prose conventions for written deliverables: documentation, README files, javadoc and code comments, commit messages, PR descriptions and review replies, design docs, and choice of English identifier names (methods, variables, classes, files). Covers em-dash usage, hyphen stacking, sentence structure, that/which, gerunds after "rather than", hedging, inclusive language, and British/American dialect consistency. Use whenever the deliverable is English prose or an English identifier that will be read by humans. Do not use for casual chat replies to the user.
---

# English prose style

Conventions for written English that will be read by humans: docs, javadoc, commit messages, PR descriptions, identifier names. These rules target the mechanical drift patterns LLMs fall into when writing technical prose. They are deliberately scoped to genuine LLM failure modes; basic grammar (subject-verb agreement, possessives, capitalisation, punctuation spacing) is assumed and not repeated here.

## When to apply

Apply these rules when producing:

- Documentation (Markdown, Asciidoc, plain text)
- README files, CHANGELOG entries, release notes
- Javadoc, KDoc, docstrings, inline code comments
- Commit messages, PR titles, PR descriptions, review replies
- Design docs, RFCs, architecture notes
- English identifier names (method, variable, class, file, package)
- Error messages and user-facing log strings

Do **not** apply for casual chat replies to the user, or for content the user explicitly marked as draft / informal.

## Dialect

Default to **British English** unless the project specifies otherwise (check the project CLAUDE.md or repository conventions). Common project signals: existing prose using `behaviour` / `organisation` / `colour` (British) vs `behavior` / `organization` / `color` (American). Match the existing dialect rather than overriding it.

LLMs tend to drift towards American spelling in long technical documents because the American corpus dominates training data. On edits longer than a few paragraphs, re-read the output and check for consistency before finishing.

## Em-dash usage

Em-dash (`—`) is the single most-flagged issue in LLM-generated technical prose. The rules below are strict.

- **No em-dash in section headings.** Use a colon: `## reWriteBatchedInserts=true: batch INSERT throughput`. If the qualifier does not fit a colon cleanly, move it into the intro sentence below the heading.
- **No em-dash in definition lists.** Patterns like `**Term** — definition` (status labels, glossary entries, bullet annotations) should be `**Term**: definition`.
- **No paired em-dashes for parentheticals.** `X — qualifier — Y` becomes `X (qualifier), Y`, `X, qualifier, Y`, or two separate sentences.
- **No em-dash as a paragraph-level connector.** `We value backward compatibility — upgrading is...` should be a period (`We value backward compatibility. Upgrading is...`), a semicolon, or a colon depending on the relationship between the two clauses.
- **No em-dash to introduce a list.** Use a colon: `bounded by its own timeout: TCP handshake, optional TLS upgrade, ...` (not `... by its own timeout — TCP handshake, ...`).
- **Use commas for short asides.** "The driver, by default, opens one socket" needs no dash.
- **Reserve the em-dash for genuine sharp emphasis** where comma, colon, semicolon, period, and parentheses would all lose the break. Even then, aim for at most one per page.

If a paragraph contains an em-dash, default to rewriting it. Most uses survive a comma, colon, semicolon, period, or parentheses without losing meaning.

## Prose patterns

LLM drafts fall into a small set of structural patterns that native-English reviewers flag immediately. Light conversational phrasing ("the right default", "the knob you actually want") and standard component-as-agent voice ("the driver bundles", "the parser accepts") are fine. The goal is to head off the mechanical issues.

### Limit hyphen stacking in noun phrases

When several hyphenated modifiers stack inside a single noun phrase, the reader has to mentally unwind each one before reading on. Two hyphens in a row is usually the comfortable limit.

- Hard to parse: `the per-batch socket-buffer deadlock`
- Easier: `the deadlock that happens when the per-batch buffer fills`

- Hard to parse: `the out-of-band cancel side-channel TCP connection`
- Easier: `the second TCP connection that carries the cancel signal`

If a noun phrase has three or more compound modifiers in a row, rewrite it as a clause.

### Split sentences earlier than you think

Aim for one main idea per sentence. If a sentence joins two distinct claims with a semicolon or a comma-plus-conjunction, or carries more than one subordinate clause, consider splitting. The fact that an existing paragraph already has long sentences is not evidence that the style fits.

- Heavy: `The driver pipelines the writes, so the wall-clock cost is not literally N × round-trip; the cost is still high, though, because before server-prepare warms up there is per-execution parse work, and even after that the response stream still carries one CommandComplete per row.`
- Split: `The driver pipelines the writes, so the wall-clock cost is not literally N × round-trip. The cost is still high. Before server-prepare warms up, every execution carries parse work; after that, the response stream still returns one CommandComplete per row.`

### Relative clauses: `that` / `which` / `what`

Use `that` for restrictive (defining) clauses; reserve `which` for non-restrictive (parenthetical) clauses, set off by commas:

- Restrictive: `the timeout that bounds the TCP handshake`
- Non-restrictive: `the timeout, which is shared across hosts, bounds the TCP handshake`

When the relative clause modifies a specific noun, do not fuse it with `what` ("the thing that"). Fused-relative `what` is grammatical but reads as conversational in technical prose:

- Less natural: `Each comes with one specific caveat (what is holding it back from being on by default)...`
- More natural: `Each comes with one specific caveat (the reason it is off by default)...`

`What` is fine in non-relative use (`do what the property says`).

### Use the gerund after `rather than` / `instead of`

When the comparison is between two actions, both sides need the gerund form. Truncating to the bare verb reads as colloquial shorthand.

- Clipped: `rather than copy-paste`, `instead of send a separate SET`
- Full: `rather than copy-pasting`, `instead of sending a separate SET`

### Hedge once, not three times

A single hedge (`in practice`, `typically`, `in most deployments`, `usually`) does the work. When several stack in one sentence, keep the strongest and drop the rest.

- Bloated: `In practice, on most deployments, the savings are typically modest in the same-DC case.`
- Tight: `On a same-DC network the savings are modest.`

### Don't define the page topic in its own body

A paragraph that explains what its containing page is about ("This page is the explanation that backs the X entry...") rarely adds information; the heading and the front-matter `description` already carry that signal. Lead with the substance.

### Watch for missing or duplicated small words

LLM auto-completion occasionally drops or duplicates short function words (`is`, `are`, `have`, `will be`, `you can`, `we`). Re-read for them:

- Missing verb: `There a number of restrictions` → `There are a number of restrictions`
- Extra word: `will have be in UTC` → `will be in UTC`
- Extra word: `you can use issue a query` → `you can issue a query`

## Inclusive language

Replace exclusionary terms with neutral alternatives:

- `master switch` / `master config` → `top-level switch` / `main config`
- `blacklist` / `whitelist` → `blocklist` / `allowlist`
- Replication topology: `primary` / `standby` / `replica` rather than `master` / `slave`
- `sanity check` → `quick check` / `consistency check`
- `dummy value` → `placeholder value`

When the term is a literal identifier (config value, class name, CLI flag, external API), keep the literal token unchanged.

## Identifier names

The dialect, inclusive-language, and brand-spelling rules above apply to identifier names too. Match the surrounding code: if a file already uses `parseURL`, do not introduce `parseUrl`; if a project is British, write `initialiseConnection`. Verify brand spelling (`PostgresConnection`, not `PostresConnection`).

## Final pass before finishing

For non-trivial English deliverables, re-read looking specifically for the LLM-typical failure modes:

1. Any em-dash in the output: almost always rewrite.
2. Dialect drift: pick one variant and normalise.
3. Hyphen stacks of three or more modifiers in one noun phrase.
4. Stacked hedges in one sentence.
5. Dropped or duplicated small function words.
6. Brand spelling and acronym casing (`PostgreSQL`, `GitHub`, `URL`, `JDBC`, `TLS`).
