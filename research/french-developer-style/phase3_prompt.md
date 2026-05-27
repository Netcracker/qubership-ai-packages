# Task

Create a French technical-prose agent skill package.

The package should help an LLM write, edit, translate, and review French software-facing prose:

- technical documentation
- README files
- API docs
- code comments
- Javadoc/KDoc/docstrings translated or written in French
- changelog and release notes
- PR descriptions and review replies
- UI strings and UI translations
- error messages
- human-readable log messages

The goal is not marketing copy, SEO text, fiction, or AI-detector evasion.

The goal is clear, natural, technically precise French that does not sound artificial, over-translated from English, bureaucratic, too verbose, or machine-generated.

Create a practical skill package that a coding agent can use in real repositories.

# Package name

Use:

```text
french-developer-style
````

# Create this file layout

Create:

```text
french-developer-style/
├── SKILL.md
├── modules/
│   ├── ui-strings.md
│   ├── fr-ca-overrides.md
│   └── inclusive-writing.md
├── references/
│   ├── glossary-fr.tsv
│   ├── ai-tics-checklist.md
│   ├── typography-cheatsheet.md
│   └── icu-fluent-placeholders.md
├── linter/
│   ├── .vale.ini
│   └── vale-fr-tech/
│       ├── Anglicisms.yml
│       ├── AITics.yml
│       ├── Typography.yml
│       ├── Terms.yml
│       └── README.md
└── README.md
```

If the current repository has a different skill layout convention, adapt the paths but keep the same logical structure.

# Source model

Use the following synthesis as the source of truth.

Primary base:

1. Boileau-style AI-tic catalogue

   * structural inspiration only
   * do not copy verbatim unless the license allows it
   * use it to shape the French AI-tic editing checklist

2. Mozilla francophone style guide

   * primary source for French software translation style, typography, and voice
   * useful rules: French typography, `-ing` titles into substantives, “This will…” into “Cette action…”, product names, Mozilla Fluent-style localization safety

3. Microsoft French Localization Style Guide, fr-FR

   * industry baseline for French software localization
   * useful rules: vouvoiement, product-name handling, avoid literal possessives, modern conjunctions, clear UI wording
   * do not copy proprietary text verbatim

4. Bureau de la traduction / Clés de la rédaction + OQLF Vitrine linguistique

   * fr-CA / Québec mode
   * anglicism diagnostics
   * terminology differences
   * do not apply Québec terminology blindly to fr-FR

5. CLDR / ICU MessageFormat / Mozilla Fluent

   * placeholder integrity
   * plural handling
   * selector syntax
   * gender and number safety

6. Lexique de l’Imprimerie nationale

   * typography baseline
   * most rules belong in linter/reference, not in the core prompt

Supporting sources:

* WordPress.com French Translation Style Guide for UI infinitive vs imperative rule
* FranceTerme only when official terminology matches real developer usage
* DSFR only for an optional government/public-service UI context
* Grammalecte, LanguageTool, Hunspell/Dicollecte, Vale as linting infrastructure

Avoid as primary:

* AI-humanizer or detector-evasion sources
* StealthyLabsHQ/plume-naturelle-style detector-evasion framing
* FranceTerme as a blanket glossary backbone
* OQLF as a blanket glossary backbone for fr-FR
* generic grammar-checker listicles
* generic French-learning grammar sources
* marketing/copywriting prompts

# Locale strategy

Default locale: **fr-FR**.

Support **fr-CA / Québec** as an explicit mode.

The skill should activate fr-CA mode when:

* the user explicitly asks for Canadian French, Québec French, or fr-CA;
* file paths contain `fr_CA`, `fr-CA`, `fr_CA.UTF-8`, or equivalent locale markers;
* locale config includes `fr-CA`;
* sibling text already uses terms such as `courriel`, `clavardage`, `pourriel`, `magasiner`;
* the repository has an explicit Canadian/Federal/Québec localization target.

For fr-BE and fr-CH, do not create separate modules. Use fr-FR conventions unless the repository has its own glossary. Do not introduce `septante`, `huitante`, or `nonante` unless already used.

If a repository already has a clear locale and terminology convention, follow the repository rather than imposing the skill default.

# SKILL.md requirements

Create a complete `SKILL.md` with YAML frontmatter.

Suggested frontmatter:

```yaml
---
name: french-developer-style
description: French technical-prose conventions for software documentation, README files, UI strings, error messages, logs, code comments, PR descriptions, changelog entries, and French localization. Use when writing, editing, translating, or reviewing French software-facing prose. Defaults to fr-FR, supports fr-CA mode, and focuses on clear natural French, technical precision, terminology consistency, and avoiding over-translated or LLM-like phrasing.
---
```

Write the body in French.

Keep the core concise:

* target length: about 1500–2200 tokens
* do not write a full style guide
* include short rules and compact original examples
* make it editing/rewrite-oriented, with a small authoring section
* tell the agent when to load the optional modules and references
* do not cite sources inside the skill unless the repository convention asks for citations
* do not copy proprietary guide text verbatim
* do not optimize for AI-detector evasion

# Suggested SKILL.md structure

Use this structure:

1. Quand appliquer cette compétence
2. Variante linguistique et registre
3. Voix par défaut
4. Règles de réécriture des brouillons LLM
5. Anglicismes, faux amis et calques
6. Typographie française à préserver
7. Chaînes UI et localisation
8. Erreurs et journaux
9. Commentaires de code et documentation API
10. Ce qui relève des linters ou du glossaire
11. Checklist finale
12. Quand enfreindre une règle

# Core principles to encode in SKILL.md

## 1. Default voice

Default:

* fr-FR
* vouvoiement
* sober technical style
* clear but not childish
* precise but not bureaucratic
* no marketing adjectives
* no unnecessary exclamation marks
* no generic corporate boilerplate

Prefer rewriting to avoid gendered adjectives when possible:

* Prefer: `La connexion est établie.`
* Avoid when possible: `Vous êtes connecté.` / `Vous êtes connecté(e).`

Use `tu` only when explicitly requested or when the existing product style clearly uses it.

## 2. UI voice

For UI strings:

* use infinitive for buttons and menu actions without terminal punctuation:

  * `Enregistrer`
  * `Supprimer`
  * `Exporter`
* use imperative or full sentence when the text has terminal punctuation:

  * `Pour supprimer ce fichier, confirmez l’action.`
* dialog titles and section titles can be nouns:

  * `Paramètres`
  * `Configuration du cache`
  * `Installation interactive`

Avoid:

* `Cliquez pour…` on buttons
* friendly filler such as `Oups !`
* unnecessary possessives copied from English
* inconsistent switching between infinitive and imperative

## 3. English `-ing` and “How to” titles

Translate English gerund-style headings into French substantives when natural:

* `Configuring the cache` → `Configuration du cache`
* `Installing Docker` → `Installation de Docker`
* `How to configure TLS` → `Configurer TLS` or `Configuration de TLS`, depending on the surrounding style

Do not force this when a tutorial is clearly procedural and an imperative heading is more useful.

## 4. “This will…” confirmations

For confirmation messages, prefer:

* `Cette action supprimera le fichier.`
* `Cette action écrasera vos modifications.`

Avoid literal `Ceci va…` unless the project already uses it.

## 5. Drop English possessive determiners

French often uses the definite article where English uses possessives.

Prefer:

* `Contactez l’administrateur.`
* `Redémarrez le service.`
* `Ouvrez le fichier de configuration.`

Avoid unnecessary literal possessives:

* `Contactez votre administrateur`
* `Redémarrez votre service`

Keep the possessive only when ambiguity would result.

## 6. Error message pattern

Use this pattern for user-facing errors:

1. What failed.
2. Why, if known.
3. What the user can do next, if there is a recovery action.

Canonical pattern:

```text
Impossible de <action>. <Cause or recovery.>
```

Examples:

* Bad: `Une erreur est survenue.`
* Better: `Impossible d’enregistrer le fichier. Vérifiez que vous disposez des droits d’écriture.`
* Bad: `Vous avez saisi une valeur incorrecte.`
* Better: `La valeur n’est pas valide. Indiquez un port entre 1 et 65535.`

Avoid:

* blaming the user
* apologies unless product policy requires them
* stack traces in user-facing errors
* `Oups !`
* vague `Erreur lors de l’opération`

For developer logs, prefer technical clarity over empathy. Include identifiers and structured fields. Do not use `vous`.

## 7. French typography

The LLM should know the intent, but mechanical enforcement belongs to linter/typography tools.

Include these rules in the skill:

* Use French guillemets in prose: `« … »`.
* Use NBSP before `;`, `:`, `!`, `?`, `%`, and before closing `»` where required.
* Use accented capitals: `À propos`, `État`, `Échec`, `Évolution`.
* Use French punctuation only in prose.

Never change typography inside:

* fenced code blocks
* inline code
* URLs
* file paths
* CLI commands
* environment variables
* JSON/YAML/TOML keys or values
* regexes
* ICU MessageFormat strings
* Fluent strings
* Markdown link targets

Preserve straight ASCII quotes where syntax requires them.

## 8. AI-like French prose patterns

Frame this as reader-clarity editing, not detector evasion.

Default to removing or rewriting these when they do not add meaning:

* `il est important de noter que`
* `il convient de noter que`
* `force est de constater`
* `dans cette optique`
* `à l’aune de`
* `en conclusion`
* `ainsi`
* `de plus`
* `par ailleurs`
* `en outre`
* `cependant`
* `néanmoins`
* `en effet`
* `par conséquent`
* empty `permet de`
* `constitue`
* `représente`
* `s’inscrit dans`
* `joue un rôle clé`
* synonymic doublets: `simple et intuitif`, `robuste et fiable`
* forced triples: `rapide, efficace et fiable`
* negative parallelism: `Ce n’est pas X, c’est Y`
* pseudo-formal verbs: `effectuer`, `disposer de`, `s’avérer`
* over-explaining obvious context
* generic final summary paragraphs

Do not ban these words mechanically. Keep them when they express a real logical relation or a precise technical meaning.

## 9. Anglicisms, false friends, and calques

Create a graded approach.

Safe replacements:

* `faire du sens` → `avoir du sens`
* `adresser un problème` → `traiter un problème`, `résoudre un problème`
* `supporter X` meaning “support” → `prendre en charge X`
* `assumer` meaning “suppose” → `supposer`
* `digital` in software context → `numérique`
* `définitivement` meaning “definitely” → `certainement`
* `opportunité` meaning “occasion” → `occasion`
* `basé sur` → `fondé sur`, `à partir de`, `repose sur`
* `en termes de` → `pour`, `côté`, or remove

Useful with exceptions:

* `librairie` → `bibliothèque` for code libraries; keep if product/project uses `librairie`.
* `éventuellement` → `peut-être` or `le cas échéant` when translating “possibly”.
* `permet de` is often empty, but can be correct if it introduces a real capability.

Leave as English when accepted in developer usage unless the project glossary says otherwise:

* `pull request`
* `merge request`
* `commit`
* `branch`
* `rebase`
* `cherry-pick`
* `endpoint`
* `framework`
* `middleware`
* `cache`
* `debug`
* `front-end`
* `back-end`
* `pipeline`
* `runtime`
* `linter`
* `parser`
* `tooling`

Locale split:

* fr-FR: `e-mail` or `courriel`; avoid `mél`.
* fr-CA: prefer `courriel`.
* fr-FR: `spam`; fr-CA: `pourriel` where project style supports it.
* fr-FR: `cookie`; fr-CA: tolerate `cookie`, use `témoin` only if the project already uses it.
* `login` as a verb → `se connecter`; fr-CA may prefer `ouvrir une session`.
* `issue` → `ticket`, `problème`, or keep `issue` in repository/PR/Jira context.

## 10. Placeholder and localization syntax safety

The skill must never break localization syntax.

Preserve exactly:

* ICU MessageFormat placeholders
* Fluent variables and terms
* `%s`, `%d`, `%1$s`, `%(name)s`
* `{name}`, `{{name}}`, `${name}`
* HTML/XML tags in localized strings
* Markdown placeholders
* product tokens and brand names

For ICU MessageFormat:

* French plural categories are usually `one` and `other`.
* In French CLDR, `one` covers 0 and 1.
* Use exact `=0` only when the product specifically needs a distinct “Aucun …” message.
* Do not invent `zero`, `two`, `few`, or `many` for French unless the framework explicitly requires them.
* Remember that apostrophe is special in ICU MessageFormat; preserve or escape it correctly.

For Fluent:

* Do not translate selector keywords.
* Preserve `{$var}`, `{-brand-name}`, attributes, and `*[other]`.
* Do not reorder variants unless you understand the syntax.

## 11. Code comments and API docs

For code comments:

* explain why, not what the code already says;
* do not translate code identifiers;
* keep comments short;
* preserve English technical identifiers and API names;
* avoid literary rewriting when the comment is already precise.

For API docs:

* use neutral present tense;
* keep precise technical nouns;
* avoid marketing language;
* do not force plain-language rewrites that damage precision;
* preserve parameter names, return types, exceptions, and version markers.

## 12. What belongs outside SKILL.md

State clearly:

Use linters/glossaries for mechanical checks:

* spelling
* grammar agreement
* repeated words
* accents
* accented capitals
* NBSP and typography spacing
* French guillemets
* terminology enforcement
* project-specific product names
* ICU/Fluent syntax validation
* sentence-length thresholds
* banned-word regex lists

Recommended tooling:

* Grammalecte
* LanguageTool French
* Hunspell/Dicollecte
* Vale custom French package
* project glossary
* translation memory

The skill provides judgement. Linters enforce mechanical style.

# modules/ui-strings.md

Create this module in French.

Focus on UI and localization.

Include:

* when to load this module;
* button labels;
* menu items;
* placeholders;
* tooltips;
* validation messages;
* confirmations;
* user-facing errors;
* warnings;
* ICU MessageFormat;
* Mozilla Fluent;
* placeholders and variables;
* plural and gender handling;
* terminology consistency;
* locale-specific wording.

Include short original examples.

Required examples:

* `Delete` → `Supprimer`
* `Click here to delete.` → `Pour supprimer, cliquez ici.`
* `This will overwrite your changes.` → `Cette action écrasera vos modifications.`
* `Are you sure you want to delete this file?` → `Voulez-vous vraiment supprimer ce fichier ?`
* `Cannot save file` → `Impossible d’enregistrer le fichier.`
* ICU plural example with `one` and `other`
* Fluent example preserving `{$count}` and `*[other]`

# modules/fr-ca-overrides.md

Create this module in French.

Focus on Québec/Canadian French.

Include:

* when to activate fr-CA mode;
* terminology preferences;
* when to use OQLF/GDT/Clés de la rédaction;
* when not to force Québec terms;
* differences from fr-FR;
* how to handle existing repository terminology.

Include a small term table:

* email / courriel
* spam / pourriel
* cookie / témoin / cookie
* login / se connecter / ouvrir une session
* chat / clavardage
* shopping / magasinage / magasiner
* pull request / merge request / demande de fusion / leave as English
* issue / ticket / problème
* browser / navigateur / fureteur
* podcast / balado / podcast

Important:

* Do not force `fureteur`, `témoin`, or `demande de tirage` into fr-FR text.
* Do not force prescriptive Québec terms into a repository that already uses common developer English.

# modules/inclusive-writing.md

Create this module in French.

It is off by default.

Include:

* activate only on explicit user request or project policy;
* prefer epicene rewrites over point médian;
* avoid `(e)` in UI strings;
* do not damage readability or screen-reader output;
* preserve technical precision;
* use point médian only if the project already uses it;
* examples of rewriting away gendered adjectives.

Examples:

* `Vous êtes connecté.` → `La connexion est établie.`
* `Utilisateur connecté` → `Connexion établie`
* `Les développeurs peuvent…` → `L’équipe de développement peut…` or `Les personnes qui développent peuvent…` depending on context

# references/glossary-fr.tsv

Create a starter TSV glossary with columns:

```text
term_en	fr-FR	fr-CA	leave_as_english	note
```

Include about 80–120 entries.

Include terms such as:

* API
* endpoint
* request
* response
* payload
* header
* cookie
* token
* session
* cache
* queue
* topic
* partition
* broker
* cluster
* node
* replica
* primary
* standby
* failover
* rollback
* migration
* feature flag
* configuration
* setting
* option
* property
* parameter
* argument
* environment variable
* log
* trace
* span
* metric
* timeout
* retry
* backoff
* transaction
* connection pool
* driver
* plugin
* extension
* build
* release
* changelog
* pull request
* merge request
* issue
* ticket
* branch
* commit
* rebase
* cherry-pick
* framework
* middleware
* linter
* parser
* runtime
* tooling
* front-end
* back-end
* debug
* browser
* email
* spam
* login
* logout
* sign in
* sign out
* upload
* download
* file attachment
* machine learning
* AI
* cloud
* serverless
* webhook
* callback
* sandbox
* workspace

Do not invent product-specific terminology.
Mark uncertain translations as contextual.
Use `leave_as_english=true` for accepted developer-English terms.

# references/ai-tics-checklist.md

Create a French AI-tic checklist.

Do not frame it as detector evasion.

Frame it as an editing checklist for clarity and natural technical prose.

Include 20–30 patterns, grouped by type:

* connectors overuse
* inflated formal register
* empty abstractions
* synonymic doublets
* forced triples
* negative parallelisms
* anglicism calques
* generic conclusions
* didactic posture
* conversational artefacts
* over-polished product prose

For each pattern:

* pattern
* why it is suspicious or weak
* what to do instead
* short original example

# references/typography-cheatsheet.md

Create a compact French typography cheat sheet.

Include:

* NBSP before `; : ! ? %`
* guillemets `« … »`
* accented capitals
* abbreviations
* numbers and units
* when not to apply typography
* Markdown/code exclusions

Keep it practical for developers.

# references/icu-fluent-placeholders.md

Create a compact reference for localization syntax safety.

Include:

* ICU plural examples for French
* exact `=0` handling
* apostrophe escaping in ICU
* Fluent variables and terms
* placeholder preservation
* examples of what not to translate
* examples of safe French rewriting around placeholders

# linter/.vale.ini and linter/vale-fr-tech

Create a starter Vale configuration.

It does not need to be perfect, but it should be plausible and conservative.

Add rules for:

* common AI connectors / phrases
* common anglicism calques
* typography warnings where Vale can safely detect them
* terminology warnings
* do-not-process-code guidance

If a rule is too hard to implement reliably, document it in `linter/vale-fr-tech/README.md` instead of pretending it works.

Do not write an enormous Vale package.

# README.md

Create a README in English or French, whichever fits the repo convention.

Include:

* what the skill is for
* what it is not for
* fr-FR default and fr-CA mode
* module activation rules
* glossary usage
* linter usage
* examples of invoking the skill
* known limitations
* licensing caution: do not copy proprietary Microsoft text; paraphrased rules only

# Quality constraints

* Use French for the skill and module bodies.
* Use concise, practical rules.
* Include original examples, not copied proprietary examples.
* Preserve technical precision.
* Avoid dogmatic anti-anglicism.
* Avoid detector-evasion language.
* Avoid marketing tone.
* Do not force FranceTerme or OQLF official terms when real developer usage differs.
* Do not apply typography inside code, JSON, YAML, regex, CLI examples, URLs, ICU, Fluent, or placeholders.
* Prefer examples that look like real software docs and UI strings.
* Make the package useful for a coding agent editing real repository files.

# After creating the files

Report:

1. Which files were created.
2. The final structure.
3. Which core principles were encoded.
4. Which rules were intentionally left to linters/glossary/human review.
5. Any assumptions or uncertain terminology choices.
6. Suggested next test: run the skill on 5–10 real French docs/UI strings and inspect the diff.
