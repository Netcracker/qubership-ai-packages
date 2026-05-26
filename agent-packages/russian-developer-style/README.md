# russian-developer-style

Style guidance for Russian-language developer-facing text: README and
Markdown docs, code comments, docstrings (Javadoc, KDoc), commit messages,
PR descriptions, changelogs, UI strings, error and log messages, and
localisation files (`.po`, `.properties`, JSON i18n). Length does not
matter: a one-line `msgstr` in a `.po` file goes through the same checklist
as a README page.

The skill fires on any task involving Russian developer text: authoring,
editing, translation, localisation, review, proofreading, verification, or
audit. Russian trigger verbs include «напиши», «переведи», «локализуй»,
«проверь», «перепроверь», «сверь», «отревью». If a request touches Russian
text, the skill loads *before* the agent answers.

The skill covers what linters handle poorly: voice, genre structure,
defending against канцелярит (bureaucratic officialese) and LLM tells,
error-message tone, and terminology choices. Mechanical checks (spelling,
quotation marks, dashes, non-breaking spaces, ё/е) stay with LanguageTool,
yaspeller, and typograf.js.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/russian-developer-style
```

Or manually in `apm.yml`:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/russian-developer-style@v1.0.0
```

Then run `apm install` and `apm compile` so the skill trigger lands in your
local `AGENTS.md` / `CLAUDE.md`.

## What's inside

- A short trigger instruction that fires on any task involving Russian
  developer text (Markdown, comments, commits, PRs, changelog, errors,
  logs, UI, localisation files). Lists trigger verbs in both Russian and
  English, so both «напиши» and 'double-check the translation' are
  covered.
- The main skill file
  ([`SKILL.md`](.apm/skills/russian-developer-style/SKILL.md)): voice,
  per-genre settings, editing LLM drafts, канцелярит and em-dash policy,
  terminology, checklist, exceptions.
- Modules:
  [`ui-strings.md`](.apm/skills/russian-developer-style/modules/ui-strings.md),
  [`errors-logs.md`](.apm/skills/russian-developer-style/modules/errors-logs.md),
  [`code-comments.md`](.apm/skills/russian-developer-style/modules/code-comments.md).
- A starter glossary
  ([`glossary.md`](.apm/skills/russian-developer-style/glossary.md)) with
  about 50 IT terms marked translate / keep.
- A before / after example collection
  ([`examples/before-after.md`](.apm/skills/russian-developer-style/examples/before-after.md)).
- Starter linter configs for Markdown and Russian prose
  ([`lint/`](.apm/skills/russian-developer-style/lint/)).

## Companion linters

The skill deliberately stays quiet on what tools do better. Use it
alongside:

- **LanguageTool** with the `ru-RU` profile for grammar, repetition, and
  agreement. Expect false positives on code embedded in prose; configure an
  ignore block for inline code and fenced code blocks.
- **yaspeller** for spelling with a custom dictionary. Upstream is
  archived, so keep your own fork or version pin and grow the dictionary
  with product-specific terms.
- **typograf.js** for guillemet quotation marks («…»), em-dashes,
  non-breaking spaces, and the space between a number and its unit. Do not
  run code through it.
- Project-specific checks for placeholders in ICU MessageFormat / Fluent,
  and for the banned-terms list from the glossary.

## Updates

`apm outdated` shows new versions; `apm deps update` upgrades them.

## Sources and history

The skill is synthesised from a four-stage study of Russian style guides
and LLM tells (Контур.Гайды, Microsoft RU L10n, Ozon Tech styleguide,
Mozilla L10n, Нора Галь, academic work on LLM tells). Prompts and notes
live under
[`research/russian-developer-style/`](../../research/russian-developer-style/).
