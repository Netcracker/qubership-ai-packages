# french-developer-style

French technical-prose style guidance for developer-facing text of any length: Markdown docs and README content,
code comments and docstrings inside source files (`.go`, `.js`, `.ts`, `.py`, `.java`, `.rs`, `.kt`, `.cs`, ...),
commit messages, PR descriptions, changelog entries, UI strings, error and log messages, and French-side
localisation files (`.po`, `.properties`, JSON i18n, `.ftl`, `.arb`). A one-line `msgstr`, a three-word button
label, and a multi-page README go through the same checklist.

The skill fires on any task that touches French developer text: writing, editing, rewriting, translating,
localising, reviewing, proofreading, verifying, auditing, double-checking, cross-checking. Trigger verbs in
French (`écrire`, `réécrire`, `traduire`, `relire`, `vérifier`, `rends ça plus naturel`) also load the skill.

The package encodes the judgement-based rules — voice, structure, AI-tic catalogue, anglicism diagnostics,
French typography intent, error-message pattern, locale policy — that linters cannot enforce reliably.
Mechanical checks (orthography, accord, typography enforcement, ICU/Fluent placeholder integrity, full
grammar) belong in LanguageTool, Grammalecte, dedicated validators, and the starter Vale pack shipped under
[`linter/`](.apm/skills/french-developer-style/linter/).

## What it is not for

- Marketing copy, SEO text, sales pitches, product taglines.
- Fiction, journalism, literary translation.
- AI-detector evasion or "humanisation" tooling — the AI-tics checklist is an editorial filter for clarity,
  not a stealth tool.
- French outside the software-facing surface (academic writing, legal contracts, official correspondence with
  French administrative bodies).

## Default locale and `fr-CA` mode

The skill defaults to **fr-FR**, with vouvoiement (`vous`), present tense, sober technical register, and
substantive titles (`Configuration du cache`, not `Configurer le cache`).

`fr-CA` mode activates when **any** of the following is true:

- the user explicitly asks for Canadian French, Québec French, or `fr-CA`;
- a file path contains `fr_CA`, `fr-CA`, `fr_CA.UTF-8`, or an equivalent locale marker;
- locale config (`languages`, `i18n.locales`, gettext, ICU) lists `fr-CA`;
- sibling text already uses `courriel`, `clavardage`, `pourriel`, `magasiner`, `balado`;
- the repository targets the Canadian Federal government, the Government of Québec, or a Canadian audience.

For fr-BE and fr-CH, the skill follows fr-FR unless the repository has its own glossary. `septante` / `huitante`
/ `nonante` are never introduced unless they are already present.

When the repository already has a clear locale and terminology convention, follow the repository — do not
override.

## Module activation rules

| Module | Load when |
| --- | --- |
| [`modules/ui-strings.md`](.apm/skills/french-developer-style/modules/ui-strings.md) | Editing buttons, labels, placeholders, tooltips, validation messages, confirmations, empty states, ICU MessageFormat, Mozilla Fluent. |
| [`modules/fr-ca-overrides.md`](.apm/skills/french-developer-style/modules/fr-ca-overrides.md) | The fr-CA detection rules in the section above match. |
| [`modules/inclusive-writing.md`](.apm/skills/french-developer-style/modules/inclusive-writing.md) | Explicit user request or documented project policy. **Off by default.** |

Modules are loaded by the agent in addition to the core `SKILL.md`, not as replacements for it.

## Reference files

| File | Purpose |
| --- | --- |
| [`references/glossary-fr.tsv`](.apm/skills/french-developer-style/references/glossary-fr.tsv) | Starter TSV with `term_en / fr-FR / fr-CA / leave_as_english / note`. ~150 entries. |
| [`references/ai-tics-checklist.md`](.apm/skills/french-developer-style/references/ai-tics-checklist.md) | 30 patterns common to French LLM drafts, with rewrite guidance. |
| [`references/typography-cheatsheet.md`](.apm/skills/french-developer-style/references/typography-cheatsheet.md) | French typography intent: non-breaking spaces, guillemets, accented capitals, dashes. Code-and-syntax exclusions. |
| [`references/icu-fluent-placeholders.md`](.apm/skills/french-developer-style/references/icu-fluent-placeholders.md) | French CLDR plural categories, `select`, apostrophe escaping in ICU, Fluent structure, what not to translate. |

The glossary is a starting point. A project glossary always wins. Do not import a proprietary glossary
verbatim — paraphrase and attribute upstream when adapting from Microsoft, Mozilla, or OQLF guides.

## Linter package

[`linter/`](.apm/skills/french-developer-style/linter/) ships a starter Vale pack
([`vale-fr-tech/`](.apm/skills/french-developer-style/linter/vale-fr-tech/)) that covers a small set of
substitutions, AI-tic markers, and typography hints. See the pack’s own README for what Vale can and cannot
do here — most importantly, do not expect Vale to enforce non-breaking spaces, ICU/Fluent integrity, or
grammar. Pair with LanguageTool (`fr`), Grammalecte, and a typography post-processor.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/french-developer-style
```

Or add it to your `apm.yml`:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/french-developer-style@v1.0.0
```

Then run `apm install` and `apm compile` to merge the trigger into your local `AGENTS.md` / `CLAUDE.md`.

## How to invoke

Direct examples that load the skill:

- "Translate this README into French."
- "Rewrite the error messages in `errors_fr.po` so they sound less translated."
- "Localise this UI flow into fr-CA."
- "Review the French docstrings in `lib/auth.py` — does the wording sound natural?"
- "Vérifie les chaînes du fichier `fr.json` et rends-les moins traduites."
- "Audite les messages d’erreur du module de paiement."

Short messages count: a one-line `msgstr "..."` triggers the same checklist as a full README.

## Known limitations

- The package encodes editorial judgement, not full grammar. Hand grammar, accord, orthography and full
  typography enforcement to LanguageTool, Grammalecte, and Hunspell/Dicollecte.
- The Vale pack is intentionally minimal. A richer terminology check requires a project-specific glossary
  compiled from `references/glossary-fr.tsv` plus your product vocabulary.
- fr-CA support is a mode, not a separate package. Differences live in
  [`modules/fr-ca-overrides.md`](.apm/skills/french-developer-style/modules/fr-ca-overrides.md). fr-BE and
  fr-CH have no dedicated module — fall back to fr-FR.
- ICU / Fluent integrity is described in the reference file but not enforced by the package. Wire
  `messageformat-validator`, `fluent-syntax`, `msgfmt -c`, or `compare-locales` separately.
- The glossary marks a number of terms as `contextuel` (project-dependent). Treat these entries as
  starting points, not as final answers.

## Licensing caution

The skill draws structural inspiration from the **Mozilla** style guide (publicly licensed), the **Microsoft
French Localization Style Guide** (proprietary — paraphrased only, never quoted verbatim), the **Bureau de la
traduction** materials and **OQLF Vitrine linguistique** (publicly accessible, used as reference for fr-CA),
and the **Boileau-style AI-tic catalogue** (structural inspiration only). All examples in this package are
original. Do not paste rule text or translated examples from proprietary guides into this skill or into
derived rule packs.

## Background

The package was synthesised from an editorial-research pipeline similar to the one used for the
[`english-developer-style`](../english-developer-style/) and
[`russian-developer-style`](../russian-developer-style/) packages. See the upstream research notes folder if
the project ships one — useful when adapting the skill to another locale.

## Updating

`apm outdated` flags new versions; `apm deps update` upgrades. Bump the version in `apm.yml` when the
contract changes (new module, breaking rename, new module activation condition), not on every prose edit.
