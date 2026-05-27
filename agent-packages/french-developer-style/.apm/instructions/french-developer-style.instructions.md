---
description: French technical-prose style rules for developer-facing text — docs, code comments and docstrings inside source files (.go, .js, .ts, .py, .java, .rs, .kt, .cs, ...), commits, PR descriptions, changelogs, UI strings, error and log messages, and French-side localisation files (.po, .properties, JSON i18n, .ftl, .arb). Triggered by review/translate/verify/proofread, not only writing.
applyTo: "**"
---

## Skill trigger: `french-developer-style`

**You MUST invoke the `french-developer-style` skill BEFORE producing, modifying, translating, or critiquing any
French developer-facing text.** The skill applies regardless of text length — a one-line `msgstr`, a three-word button
label and a multi-page README go through the same checklist.

### Trigger verbs

The skill fires on any of these tasks, in English or in French. The verb in the user request, not the file size,
decides.

- write, draft, author, compose / écrire, rédiger, composer, créer
- edit, rewrite, revise, polish, copy-edit / modifier, réécrire, relire, polir, retravailler
- translate, localise (to or from French) / traduire, localiser
- review, proofread, verify, audit, double-check, cross-check / réviser, vérifier, contrôler, auditer
- "check the wording", "does this sound natural in French", "make this less AI", "make this less translated",
  "rends ça plus naturel", "rends ça moins traduit", "ça sonne français ?"

### Covered surfaces

- Markdown: README, reference docs, design docs, ADR, runbooks, changelog, release notes.
- Source files (`.go`, `.js`, `.ts`, `.py`, `.java`, `.rs`, `.kt`, `.cs`, `.cpp`, `.rb`, `.swift`, `.scala`, `.php`,
  ...): all French text inside them — code comments, docstrings (Javadoc, KDoc, TSDoc, JSDoc, Python docstrings,
  Rust doc-comments).
- Localisation files (French source or French target): `.po`, `.pot`, `.properties`, `.resx`, `.json` (i18n), `.ftl`,
  `.arb`.
- UI strings: buttons, labels, placeholders, tooltips, empty states, confirmations.
- Error, validation, warning, and log messages (including one-line `msgid` / `msgstr`).
- Commit messages, PR / MR descriptions, code-review replies in French.

Short messages count. A single `msgstr "..."` line is in scope.

### fr-FR default; fr-CA mode

Default locale is **fr-FR**. Activate **fr-CA** mode when any of the following is true:

- the user explicitly asks for Canadian or Québec French, or names `fr-CA`;
- file paths contain `fr_CA`, `fr-CA`, `fr_CA.UTF-8`, or an equivalent locale marker;
- locale configuration (`languages`, `i18n.locales`, gettext, ICU) lists `fr-CA`;
- sibling text already uses `courriel`, `clavardage`, `pourriel`, `magasiner`, `balado`;
- the repository targets the Canadian Federal government, the Government of Québec, or a Canadian audience.

For fr-BE and fr-CH, follow fr-FR unless the repository says otherwise. Do not force `septante` / `huitante` /
`nonante` unless they already appear.

When the repository already has a clear locale and terminology convention, follow the repository.

### When NOT to invoke

- *Existing* code identifiers, product names, CLI flags, file paths, environment variables — do not translate or
  rename them.
- Generated API references and verbatim third-party quotes.
- Files explicitly marked "do not edit" or covered by a repository-specific style guide — yield to the local guide.
- Casual chat replies to the user.

### Failure mode to avoid

If the request touches French developer text and the skill has not been invoked, stop and invoke it before
continuing. Native-speaker intuition is not a substitute: the dialect policy, the AI-tic catalogue, French
typography rules, anglicism diagnostics and the per-surface templates live in the skill, not in general fluency.
