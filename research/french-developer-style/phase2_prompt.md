# Research title

Deep evaluation of sources for a French LLM skill for technical prose, developer documentation, and UI localization

# Goal

This is Phase 2 of the research.

Phase 1 found no single proven off-the-shelf French LLM skill for this use case. The likely best approach is to create a compact `SKILL.md` by synthesizing:

- French UI/localization style guides
- vendor and OSS localization rules
- France/Canada terminology sources
- French plain-language and editorial sources
- a small LLM-prose failure-mode checklist
- mechanical linting and typography tools kept outside the skill

Deeply evaluate the shortlisted candidates below and recommend how to build the final skill.

The target is not marketing copy, SEO text, fiction, or AI-detector evasion. The target is clear, natural, technically precise French for software engineering contexts.

# Target domain

The final skill should support:

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

The practical goal is to avoid French LLM prose that sounds artificial, over-translated from English, bureaucratic, too verbose, or machine-generated while preserving technical precision.

# Locale strategy

France French is the primary target.

However, Phase 1 found that Canadian/Québec French differs materially from France French in terminology, inclusive-writing expectations, and some tone choices.

Evaluate whether the final skill should be:

- France-French-first
- Canadian/Québec-French-first
- locale-switching
- split into separate fr-FR and fr-CA variants
- core skill plus locale-specific glossary and typography modules

For each recommendation, explain the practical trade-off.

# Phase 1 summary

Phase 1 found:

- no single proven ready-made French LLM skill for software writing;
- strongest category: French UI/localization guides from major vendors and OSS projects;
- weaker category: generic grammar-checker listicles, prompt-marketplace pages, SEO/humanizer tools;
- developer-documentation-specific French sources are weaker than UI/localization sources;
- France French and Canadian/Québec French likely need separate terminology or a locale switch;
- Phase 2 should focus on vendor localization guides, terminology sources, typography references, linters, and a small AI-tic-removal layer.

Do not repeat broad discovery. Deeply evaluate the shortlist below.

Do not expand the candidate list unless you find a directly relevant authoritative source that clearly beats one of the shortlisted candidates. The main task is deep evaluation, not discovery.

# Shortlisted candidates from Phase 1

Deeply evaluate these candidates.

## 1. Microsoft French Localization Style Guides: fr-FR and fr-CA

Why shortlisted:
- strongest concrete software-localization sources;
- paired fr-FR / fr-CA documents expose locale differences;
- rules on tone, articles, possessives, punctuation, UI wording, product names, gender, semicolons, exclamation marks, and “le ou les” instead of “le(s)”.

Investigate:
- which rules transfer directly into SKILL.md;
- which rules are Microsoft-specific;
- how fr-FR and fr-CA differ;
- how to handle the masculine-default rule versus inclusive-writing guidance.

## 2. Mozilla L10n French style guide + Mozilla general guide

Why shortlisted:
- community-authored, PR-reviewed, software-native;
- concrete on natural expression, literal translation, product-name handling, tone, and per-product formality;
- CC-BY-SA and GitHub-based.

Investigate:
- whether it is suitable as a compact rule source;
- how it handles “vous” vs “tu”;
- what it contributes beyond Microsoft.

## 3. WordPress.com French Translation Style Guide

Why shortlisted:
- short, opinionated, software-grade;
- concrete on vouvoiement, infinitive vs imperative, no familiar register, écriture épicène, and anglicisms;
- useful as compact SKILL.md scaffolding.

Investigate:
- whether its rules generalize beyond WordPress;
- whether it is suitable as a “small digest” for UI localization.

## 4. OQLF Vitrine linguistique: GDT + BDL

Why shortlisted:
- authoritative Québec terminology and editorial source;
- strong on anglicisms, terminology, and Canadian/Québec usage;
- useful for locale-specific glossary.

Investigate:
- which terminology should be in the skill versus glossary;
- how to handle differences with FranceTerme;
- how to use OQLF without forcing Québec terminology into fr-FR docs.

## 5. FranceTerme / Vocabulaire de l’informatique

Why shortlisted:
- official French terminology source;
- IT vocabulary published by the Commission d’enrichissement de la langue française;
- important for France French terminology choices.

Investigate:
- which terms are actually usable in software documentation;
- which official terms are too artificial or uncommon for developer docs;
- how to resolve conflicts with common industry usage and OQLF.

## 6. Bureau de la traduction: Clés de la rédaction + Canada.ca Content Style Guide

Why shortlisted:
- authoritative Canadian French plain-language and editorial source;
- strong on anglicisms, typography, inclusive writing, and plain language;
- useful for fr-CA variant and editing rules.

Investigate:
- what transfers to software prose;
- how it conflicts with Microsoft fr-FR;
- whether it should be primary for fr-CA only.

## 7. Lexique des règles typographiques en usage à l’Imprimerie nationale

Why shortlisted:
- canonical France French typography reference;
- relevant to French punctuation spacing, guillemets, accented capitals, abbreviations.

Investigate:
- which rules belong in linter/typography tooling rather than SKILL.md;
- which rules the LLM must know to avoid damaging Markdown, code, JSON, YAML, regexes, CLI examples, and placeholders.

## 8. Grammalecte + LanguageTool French + Hunspell/Dicollecte

Why shortlisted:
- mechanical-checking layer;
- Grammalecte and LanguageTool handle grammar, orthotypography, anglicisms, regionalisms, false friends, repetitions;
- LanguageTool supports fr-FR/fr-CA/fr-BE/fr-CH variants.

Investigate:
- what belongs in CI/linter rather than the skill;
- false-positive risks in code-mixed developer docs;
- whether Vale should wrap some checks;
- whether a custom glossary/terminology linter is needed.

## 9. Vale prose linter framework

Why shortlisted:
- no mainstream French package was found, but Vale is useful for custom style checks;
- likely substrate for anglicism swap lists, terminology, NBSP checks, capitalization rules, and forbidden AI-tic phrases.

Investigate:
- whether to create a custom French Vale package;
- which rule families are suitable for Vale;
- which are too judgment-heavy and should remain in SKILL.md.

## 10. ICU MessageFormat / CLDR French plural rules + Mozilla Fluent

Why shortlisted:
- essential for UI strings with variables, number, gender, and plural forms;
- French plural categories and Fluent selectors must be preserved by any LLM working on UI strings.

Investigate:
- exact guidance for preserving placeholders and syntax;
- how to teach LLM not to break ICU/Fluent strings;
- whether this belongs in a UI module.

## 11. alxbd/boileau SKILL.md

Why shortlisted:
- existing French AI-tic-removal skill;
- directly targets failure modes such as “permet de”, “Par ailleurs”, “De plus”, “faire du sens”, “adresser un problème”, calques, and falsely elevated register.

Investigate:
- how good the rules are;
- whether it is trustworthy enough to reuse structurally;
- what failure modes it catches that vendor localization guides miss;
- whether it overcorrects or becomes anti-AI-detector advice.

## 12. StealthyLabsHQ “plume-naturelle” / French AI-text marker catalogues

Why shortlisted:
- possible French LLM-tell catalogue;
- likely weak evidence but potentially useful for diagnostic checklist.

Investigate:
- which markers are credible enough to include;
- which should be excluded as detector-evasion or academic-only.

## 13. DSFR documentation + numerique-gouv/dsfr-skill

Why shortlisted:
- sober, accessible, institutional fr-FR UI prose;
- relevant for government/public-service UI contexts;
- existing Claude Code skill may show packaging pattern.

Investigate:
- whether DSFR contributes general French UI-writing rules or only design-system component rules;
- whether it should be a narrow optional module rather than core skill.

# Key questions to investigate

## 1. Best base for the skill

Answer:

- Is there a single best base source?
- Should the base be Microsoft fr-FR, Mozilla L10n, WordPress.com FR, DSFR, Boileau, or a synthesis?
- Which source should define default voice?
- Which source should define UI translation rules?
- Which source should define documentation prose?
- Which source should define terminology rules?
- Which source should define fr-CA behavior?

## 2. Skill architecture

Recommend whether the final result should be:

- one monolithic French technical-prose skill
- a core skill plus domain modules
- separate skills, for example:
  - `fr-technical-prose`
  - `fr-ui-strings`
  - `fr-errors-logs`
  - `fr-code-comments`
- one skill plus companion linter configuration
- a skill package with locale glossaries and examples

Consider token budget and practical agent usage. Avoid a huge style guide that the LLM will ignore.

## 3. Locale architecture

Recommend how to support:

- fr-FR
- fr-CA / Québec
- fr-BE / fr-CH if relevant
- international French

Answer:

- Is fr-FR a good default?
- Should fr-CA be a mode or separate skill?
- Which rules are locale-neutral?
- Which rules need locale-specific variants?
- Which rules should be in glossary files rather than SKILL.md?
- How should the skill behave when a repository already uses one variant?

## 4. Authoring vs editing

Recommend whether the skill should be:

- editing/rewrite-oriented
- authoring-oriented
- split into authoring, editing, and final-check sections

The immediate need is to make LLM-generated French technical prose sound less artificial and less translated, but the same rules should help when drafting new text.

## 5. French genre defaults

For each text type, recommend default tone and grammar:

- UI button labels
- menu items
- placeholders
- tooltips
- validation messages
- user-facing errors
- warnings
- logs intended for humans
- README and tutorials
- API docs
- code comments
- Javadoc/KDoc/docstrings
- changelog and release notes
- PR descriptions
- review replies

For each type, answer:

- infinitive, imperative, impersonal, “vous”, “tu”, “nous”, or neutral?
- short phrase or full sentence?
- should the text explain action, reason, consequence, or recovery?
- what should be avoided?

## 6. Anglicisms, false friends, and calques

Deeply evaluate which anti-anglicism rules transfer safely into software prose.

For each rule family, classify as:

- safe and useful
- useful with technical-context exceptions
- dangerous if applied mechanically
- should live only in a glossary or linter

Rule families to evaluate:

- “permet de”
- “faire du sens”
- “adresser un problème”
- “impacter”
- “supporter” meaning “prendre en charge”
- “éventuellement” meaning “possibly”
- “librairie” vs “bibliothèque”
- “assumer” vs “supposer”
- “application” vs “candidature”
- “définitivement” vs “certainement”
- “opportunité” vs “occasion”
- “digital” vs “numérique”
- “mail/email/courriel/mél”
- “cookie/témoin”
- “spam/pourriel”
- “login/se connecter/ouvrir une session”
- “issue/problème/ticket”
- “pull request/merge request/demande de fusion”

Give concrete guidance: when to rewrite, when to keep, and what to rewrite into for fr-FR and fr-CA.

## 7. Technical precision vs plain language

Evaluate where plain-language rules can damage technical precision.

Check:

- official terminology that is correct but uncommon;
- common developer terms that are English but accepted in practice;
- nominalizations that are normal technical nouns;
- passive or impersonal constructions that are clearer than forced active voice;
- inclusive-writing rules that make UI strings too long or ambiguous;
- typography rules that break code, Markdown, JSON, YAML, ICU, or CLI examples.

Recommend practical exceptions.

## 8. UI and localization strategy

Evaluate how to handle:

- source-language interference from English
- literal translations
- product terminology
- untranslated brand names and feature names
- button labels
- menu items
- placeholders
- tooltips
- validation messages
- plural forms
- gendered placeholders
- ICU MessageFormat
- Fluent strings
- variables and placeholders in translated strings
- punctuation around placeholders
- consistency between UI and docs
- “vous” vs “tu” vs neutral style
- French capitalization in headings and UI labels

Recommend which source is strongest for each of these.

## 9. Error messages and logs

Recommend a French pattern for errors and logs.

Answer:

- Should user-facing errors start with “Impossible de…”?
- When should the message use “vous”?
- Should the message say what happened, why, what to do next, or all three?
- Should messages apologize?
- How should technical logs differ from user-facing errors?
- How to avoid blaming the user?
- How should fr-FR and fr-CA differ, if at all?

Use Microsoft, Mozilla, WordPress.com, DSFR, or other sources if they provide guidance.

## 10. LLM-specific French failure modes

Use Boileau, StealthyLabsHQ, and any serious French LLM-tell sources only as diagnostic background.

Identify which French LLM failure modes are credible enough to include in the skill, for example:

- “il est important de noter que”
- “en conclusion”
- “ainsi”
- “de plus”
- “par ailleurs”
- “permet de”
- “joue un rôle clé”
- inflated formal register
- noun-heavy prose
- English-like sentence rhythm
- literal calques
- mechanically parallel bullet lists
- vague summarizing closers
- over-explaining obvious context
- generic corporate boilerplate tone

Do not turn this into AI-detector evasion. Frame it as editing for reader clarity and genre fit.

## 11. LLM skill vs linter split

Recommend which rule families belong in:

1. `SKILL.md`
2. linter / CI
3. glossary / terminology file
4. translation memory / localization workflow
5. optional human-review checklist

Consider:

- spelling
- accents
- capitales accentuées
- typography
- NBSP before `; : ! ?`
- French guillemets
- repeated words
- grammar agreement
- terminology consistency
- product names
- UI string placeholders
- ICU/Fluent syntax
- plural and gender agreement
- anglicisms
- false friends
- sentence length
- AI-tics
- inclusive writing
- locale-specific vocabulary

## 12. Maintenance, licensing, and derivation

Check:

- whether the source is actively maintained
- whether the source can be cited
- whether the rules can be paraphrased into a skill
- whether examples can be copied or should only inspire original examples
- whether the source is proprietary or lacks an open license
- whether the source is safe to use as an implementation base
- whether a package can depend on the source directly or should only summarize rules

Do not copy proprietary guide text verbatim into the final skill.

# Required output

Produce a research report under 3500 words.

Use source URLs and cite primary sources. Prefer official docs, public repositories, and named authors.

Do not spend space on generic French grammar unless it affects skill design.

## 1. Executive summary

Answer directly:

- What are the top 5 sources after deep evaluation?
- Is there a single best base?
- What should be the primary base: Microsoft, Mozilla, WordPress.com, OQLF/FranceTerme, Canada.ca/Clés, DSFR, Boileau, or a synthesis?
- Should the final deliverable be one skill, split skills, or a core skill with modules?
- Should the final deliverable be fr-FR-first, fr-CA-first, locale-switching, or split?
- What should live in the skill vs in linters/glossaries/translation memory?
- What is the most important risk when adapting French editorial/localization rules to software prose?

## 2. Deep candidate evaluation

For each shortlisted candidate, provide a compact table with:

- name
- URL
- final disposition:
  - primary base
  - top-5 source
  - supporting source
  - background only
  - linter only
  - terminology only
  - reject for this use case
- author / organization
- French variant:
  - fr-FR
  - fr-CA / Québec
  - fr-BE / fr-CH
  - international
  - configurable
- best use:
  - authoring
  - editing / rewrite
  - UI translation
  - error messages
  - terminology
  - linting / review
  - background research
- strongest contribution
- main weakness
- evidence of authority or adoption
- maintenance status
- examples available: yes / no / partial
- false-positive or awkward-output risk: low / medium / high
- portability to compact `SKILL.md`: easy / medium / hard

## 3. Recommended architecture

Describe the proposed final skill package.

Include:

- package name
- file layout
- whether to split modules
- approximate `SKILL.md` length
- whether to include examples
- whether to include glossary files
- whether to include linter configs
- whether to include locale-specific files
- how agents should decide which module or locale to use

## 4. Rule families to port into SKILL.md

List 12–20 rule families that should become skill guidance.

For each:

- source or sources
- why it matters
- whether it applies to docs, UI, comments, errors, logs, PRs, or all
- whether it needs exceptions for technical text
- whether it needs fr-FR / fr-CA variants
- one short original example if useful

Do not copy examples verbatim from proprietary sources.

## 5. Rules to keep out of SKILL.md

List rules that should instead live in:

- Grammalecte / LanguageTool / custom linter
- Vale custom style
- typography tool
- glossary / terminology table
- translation memory
- human review checklist

Explain why.

## 6. Genre defaults

Create a compact table for the main text types:

- UI button
- UI menu item
- UI placeholder
- tooltip
- validation message
- UI error
- developer log message
- README/tutorial
- API reference
- code comment
- docstring/Javadoc/KDoc
- changelog/release note
- PR description
- review reply

For each, recommend:

- default voice: infinitive / imperative / impersonal / “vous” / “tu” / “nous” / neutral
- sentence length
- what to include
- what to avoid
- fr-FR / fr-CA differences if material

## 7. High-risk contradictions

Call out contradictions between sources and recommend decisions.

Examples to check:

- Microsoft masculine default vs inclusive writing guidance
- FranceTerme official terminology vs common developer usage
- OQLF Québec terminology vs France French industry usage
- WordPress.com formal “vous” vs Mozilla product-specific “tu”
- plain-language advice vs technical precision
- anti-anglicism advice vs accepted developer English terms
- French typography rules vs Markdown/code readability
- UI infinitive vs imperative
- DSFR institutional tone vs developer-doc tone
- AI-tic removal rules vs legitimate technical phrasing

## 8. Final synthesis

End with:

- recommended primary base
- secondary sources
- background-only sources
- sources to avoid as primary
- recommended next step to create the actual `SKILL.md`
- 10–15 concrete principles that the final skill should enforce
