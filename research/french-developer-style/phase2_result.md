# Phase 2 Deep Evaluation — French LLM Skill (Technical Prose, Dev Docs, UI Localization)

## 1. Executive summary

**Top 5 sources after deep evaluation, in order of usefulness for this SKILL.md:**

1. **alxbd/boileau SKILL.md** (github.com/alxbd/boileau) — already-written, French-native skill that identifies and rewrites 38 numbered AI-tic patterns; the closest existing artefact to the target and structurally reusable as a starting skeleton.
2. **Mozilla francophone "Guide stylistique pour la traduction"** (github.com/mozfr/besogne/wiki) — CC-BY-SA 4.0, maintained (last edit Aug 2025), explicitly derived from the Imprimerie nationale lexicon and from the Sun OpenOffice fr guide, and the only public source that combines technical-translation rules with concrete UI patterns (`-ing` → substantive, "Cette action…", `Tout sélectionner`).
3. **Microsoft French (France) Localization Style Guide** (download.microsoft.com/.../fra-fra-StyleGuide.pdf, June 2017) — the canonical industry baseline for fr-FR software voice, conjunction modernisation table, and the masculine-default rule that must be explicitly overridden.
4. **Bureau de la traduction — Clés de la rédaction + OQLF Vitrine linguistique (GDT + BDL)** (nos-langues.canada.ca, vitrinelinguistique.oqlf.gouv.qc.ca) — paired primary base for fr-CA terminology and anglicism diagnostics. The Microsoft fr-CA guide itself normatively defers to Termium and GDT.
5. **Lexique des règles typographiques en usage à l'Imprimerie nationale** + **CLDR plural rules + ICU MessageFormat docs** (unicode.org/cldr) — the typography/UI structural baseline. Most rules belong in a linter, but a small subset (NBSP before `; : ! ?`, French guillemets, accented capitals, plural keyword `one` for both 0 and 1 in fr-FR) must be in the skill to prevent the LLM from breaking output.

**Single best base or not?** No single source covers all genres. The recommended primary base is a **synthesis** structured as **boileau-style AI-tic catalogue + Mozilla fr typographic/voice rules + Microsoft fr-FR voice baseline + OQLF/Clés for fr-CA mode**, with FranceTerme and DSFR as opt-in modules and Vale/Grammalecte/LanguageTool as out-of-skill linters.

**Skill packaging:** **One core skill with three optional modules** — `fr-tech` (core, ~1500–2000 tokens), `fr-ui` (UI strings, errors, ICU/Fluent placeholder safety, ~600 tokens), `fr-ca-mode` (overrides for Québec terminology and OQLF preferences, ~400 tokens), `inclusive-writing` (~300 tokens, off by default). Glossaries and Vale config live in sibling files loaded on demand, not in `SKILL.md`.

**Locale architecture:** **fr-FR-first by default, fr-CA as an explicit mode** toggled by repo signal (presence of `fr_CA`/`fr-CA` in i18n filenames, CI matrix, or `package.json` locales) or explicit user instruction. International/locale-neutral fallback is fr-FR with anglicisms tolerated for established dev terms. fr-BE/fr-CH do not warrant separate modules — fr-FR covers them, with the caveat that septante/nonante are not introduced.

**What lives where:**
- **SKILL.md (judgment rules):** voice, register, AI-tic patterns, anglicism resolution that depends on context, vous/imperative/infinitive decisions, placeholder integrity, what to do when a repo already uses one variant.
- **Glossary file (`glossary-fr.tsv`):** locked term mappings (fr-FR + fr-CA columns, with "leave as English" flag for `pull request`, `commit`, `merge`, `branch`, `rebase`, `linter`, `framework`, etc.).
- **Linter (Vale + Grammalecte/LanguageTool in CI):** spelling, typography spaces, repeated words, agreement, accentuated capitals.
- **Translation-memory/Fluent/ICU files:** plural variants and placeholder syntax — the skill teaches preservation, not editing.
- **Human review checklist:** inclusive-writing decisions, tone calibration, brand-name handling.

**Most important risk when adapting French editorial rules to software prose:** **prescriptive French-Académie or FranceTerme/OQLF terminology will corrupt working developer documentation if applied mechanically.** "Mél" (FranceTerme for email), "fouineur" (hacker), "frimousse" (smiley), "philoutage" (phishing) are official but unusable in real fr-FR engineering text; "fureteur" (browser) was historically OQLF-pushed but Microsoft fr-CA uses "navigateur." The skill's job is to filter out folkloric prescriptions and keep only the terminology that real fr-FR/fr-CA engineers use.

## 2. Deep candidate evaluation

| # | Source | URL | Disposition | Org | Variant | Best use | Strongest contribution | Main weakness | Authority/adoption | Maintenance | Examples | FP/awkwardness risk | Portability |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Microsoft French (France) Style Guide | download.microsoft.com/.../fra-fra-StyleGuide.pdf | Top-5 source | Microsoft Loc team | fr-FR | UI translation, voice baseline | "Microsoft voice" register, conjunction modernisation table (de même que → comme, lors de → durant, par conséquent → ainsi), explicit "avoid `on`, `il y a`, `il faut`, `c'est`", explicit rule to drop English possessive (contact your administrator → contactez l'administrateur) | Masculine-default rule (3.1.8) is now politically loaded; semicolon ban is Microsoft-internal; PDF is large and proprietary — must paraphrase | Industry-standard Microsoft Language Portal | June 2017 PDF; index page refreshed 2025 | Yes, bilingual pairs | Low-medium | Medium (must paraphrase) |
| 2 | Microsoft French (Canada) Style Guide | download.microsoft.com/.../fra-can-StyleGuide.pdf | Top-5 source (for fr-CA) | Microsoft Loc team | fr-CA | fr-CA UI translation, terminology arbitration | Explicitly defers to Termium + GDT (OQLF) alongside Le Robert/Larousse — confirms the fr-CA Microsoft choices align with OQLF | PDF text-extraction-resistant; some Quebec-specific picks (e.g. "courriel") not always shared with fr-FR users | Microsoft Loc baseline for fr-CA | June 2017 PDF | Yes (partial access) | Low-medium | Medium |
| 3 | Mozilla fr "Guide stylistique pour la traduction" | github.com/mozfr/besogne/wiki/Guide-stylistique-pour-la-traduction | **Primary base for typography + voice rules** | mozfr (Mozilla.org community) | fr-FR (international-leaning) | Authoring + editing of dev/UI text | Compact, free (CC-BY-SA 4.0), explicitly anchored on Imprimerie nationale; gives the NBSP table verbatim, the `-ing` → substantive rule, "Cette action" rewrite of "This will", `Tout sélectionner` vs Windows' "Sélectionner tout", `Web` vs `web` capitalisation, point médian fallback for inclusive writing | Mozilla-specific terminology bits (Modules complémentaires) need stripping | Mozilla Foundation, used in Pontoon for Firefox/Thunderbird fr | Active (Aug 2025) | Yes | Low | Easy |
| 4 | Mozilla general L10n style guide | mozilla-l10n.github.io/styleguides/mozilla_general/ | Supporting source | Mozilla L10n drivers | International | Trademark handling, source-meaning fidelity | Defines correct handling of brand names, unit conversions, cultural-reference adaptation — generally applicable to dev docs | Targets product UI, not docs; thin on rule specificity | Mozilla Foundation | Active | Yes | Low | Easy |
| 5 | WordPress.com French Translation Style Guide | translate.wordpress.com/glossaries-and-style-guides/french-style-guide/ | Supporting source | Automattic Polyglots | fr-FR | UI string genre defaults | Crisp prescriptive rule: **infinitive when no terminal punctuation, imperative when there is** ("Delete" → « Supprimer »; "Click here to delete." → « Pour supprimer, cliquez ici. »); explicit "vouvoiement formel" stance; recommends rewriting "Are you sure you want to delete…" → "Voulez-vous vraiment supprimer…?" to dodge gendered adjective issue | Short; opinionated toward formal vous which may clash with Mozilla Firefox tu in some products | Used across .com translation pipeline | Active | Yes | Low | Easy |
| 6 | OQLF Vitrine linguistique (GDT + BDL) | vitrinelinguistique.oqlf.gouv.qc.ca | Terminology-only (fr-CA glossary) | Office québécois de la langue française | fr-CA | Terminology lookup | Authoritative for fr-CA software/IT terms — "logiciel libre", "logiciel sur mesure", "groupe de travail" definitions accessible per-term | Some recommendations (témoin for cookie, fureteur for browser) are not the industry default even in fr-CA; do not force into fr-FR | Government of Quebec; the OQLF *Rapport annuel 2023-2024* (24 Sept. 2024) reports the Vitrine linguistique was "consulté près de 4,5 millions de fois, par plus de 1 440 000 utilisateurs et utilisatrices" during the 15 Jan – 1 Mar 2024 campaign window alone | Continuously updated | Per-term | Medium if applied to fr-FR | Glossary, not skill |
| 7 | FranceTerme / Vocabulaire de l'informatique | franceterme.culture.gouv.fr | Background only / terminology-only | DGLFLF (French Ministry of Culture) | fr-FR | Cite when an official term IS in use | Per the DGLFLF 2024 annual report, FranceTerme "compte plus de 9 500" terms total (Wikipedia FR FranceTerme article also states "En 2025, le site comprend environ 9 500 termes"), with the ICT-specific *Vocabulaire des techniques de l'information et de la communication* accounting for ~850 terms | Many entries are unusable in real fr-FR dev prose (mél, fouineur, frimousse, philoutage, ordiphone, témoin de connexion, manche à balai for joystick); "obligatory" only in French government documents | Légally binding for ministerial texts only | Active | Per-term | High if applied mechanically | Glossary, not skill |
| 8 | Bureau de la traduction — Clés de la rédaction | nos-langues.canada.ca/fr/cles-de-la-redaction | Top-5 source (for anglicism diagnostics) | Translation Bureau, PSPC Canada | fr-CA (covers anglicisms relevant to fr-FR too) | Editing for anglicisms | Categorised anglicismes (syntaxiques, sémantiques, phonétiques, de coordination) with examples — superior to a flat blacklist for an LLM that must judge case-by-case | Canada-centred examples; do not force fr-CA spelling on fr-FR text | Government of Canada; authoritative for federal translation | Continuously updated (Canadian Style + Guide du rédacteur merged into it Jan 2024) | Yes | Low | Easy |
| 9 | Canada.ca Content Style Guide | design.canada.ca/style-guide/ | Supporting (fr-CA) | Treasury Board / Canada.ca | en-CA / fr-CA paired | Plain-language web UI rules | Concrete writing-for-the-web rules already validated against accessibility/WCAG; fr-CA sentence-case heading default; explicit "Statistics Canada (2012): almost 50% of Canadians have literacy challenges" backing plain-language pressure | Targets government services, not dev docs; plain-language pressure can over-simplify API references | Mandatory for all Canadian federal departments | Updated 2024–2025 | Yes | Medium if applied to API docs | Easy with carve-outs |
| 10 | Lexique des règles typographiques en usage à l'Imprimerie nationale | (book; widely-mirrored summaries: CNRS PDF, mardi-inspi summary) | Linter + small skill subset | Imprimerie nationale | fr-FR (canonical) | Typography enforcement | Canonical rule source: "signe double, espace double" with insécable; thin space before `; : ! ? %`; French guillemets `« »` with NBSP inside; accentuated capitals (`État`, `À propos`, `Évolution`); rules for `etc.`, `°`, `XIXᵉ siècle`, number grouping by NBSP | Many rules are print-typography (drop caps, justified text, hyphenation) irrelevant to Markdown/code | Cited universally in French editorial norms (ISBN 978-2-7433-0482-9) | Book, periodic editions | Yes (third-party summaries) | Low if scoped | Medium |
| 11 | Grammalecte + LanguageTool fr + Hunspell/Dicollecte | grammalecte.net, languagetool.org | Linter only | Olivier R. (Algoo) / LanguageTool-org | fr-FR (Grammalecte design goal: minimise false positives) | CI/editor grammar+typography check | Grammalecte's stated principle: "le moins de faux positifs possible"; LanguageTool ships explicit French rule set updated from Dicollecte/Grammalecte dictionaries | Both struggle on code-mixed prose, English identifiers, ICU/Fluent placeholders — must be exempted by Vale scopes or `vale off` blocks; cannot reliably parse Markdown code fences | Open-source, widely deployed | Grammalecte revived under Algoo; LanguageTool active | Test corpora exist | Medium-high in dev docs without scoping | Linter only |
| 12 | Vale prose linter | vale.sh | Linter wrapper (yes — create custom French Vale package) | errata-ai / Vale-cli community | Configurable | Markup-aware enforcement of judgement-light rules | Markdown-, AsciiDoc-, RST-, MDX-aware; ignores code fences by default; vocabulary accept/reject lists; per-file scopes; existing Microsoft + Google + Grafana + GitLab style packages prove the model | No turn-key French style; would need an in-house package | Adopted by GitLab, Contentsquare, Grafana, Microsoft Docs | Active | Yes (English) | Low | Easy |
| 13 | ICU MessageFormat + CLDR plural rules | unicode.org/cldr/index/cldr-spec/plural-rules, unicode-org.github.io/icu | Top-5 source (for UI module) | Unicode Consortium | International (fr included) | UI plural and placeholder safety | Specifies that French uses categories `one` (for 0 and 1) and `other` only — practically `{count, plural, one {# fichier} other {# fichiers}}`; `=0` exact-match preserves the "Aucun fichier" pattern; nested `select` for gender; quoted apostrophes are special in MessageFormat | Doesn't address text style — only structure | Universal i18n standard (FormatJS, i18next, react-intl, Fluent, Phrase, SimpleLocalize all support) | Active; per cldr.unicode.org, "The Survey Tool is open twice a year to gather data for new structure" (spring and autumn release cycle: CLDR 46 in Oct 2024, CLDR 47 in April 2025, CLDR 48 in Oct 2025) | Yes | Low | Easy |
| 14 | Mozilla Fluent (projectfluent.org) | projectfluent.org | Top-5 source (for UI module) | Mozilla | International | Placeholder integrity for Mozilla-style i18n | Defines `.attr`, term references `{-brand-name}`, plural `*[other]` syntax; the LLM must not translate selector names or reorder bracketed arms | Smaller ecosystem than ICU | Used in Firefox | Active | Yes | Low | Easy |
| 15 | DSFR — Système de Design de l'État | systeme-de-design.gouv.fr; github.com/GouvernementFR/dsfr | Background only (narrow opt-in module) | Service d'Information du Gouvernement (SIG) | fr-FR (institutional) | French gov-service UI writing only | Mandatory for `.gouv.fr` sites under circulaire n° 6411-SG du 7 juillet 2023 *relative à la lisibilité des sites internet de l'État et de la qualité des démarches numériques* (cited by numerique.gouv.fr and the Sites Conformes platform documentation); recently noted "Le SIG recommande un marquage explicite des contenus produits avec l'aide d'une IA"; useful as terminology source for "Fil d'Ariane", "Pied de page", standard component labels | Institutional tone is wrong for SaaS/dev-tool docs; DSFR licence forbids non-State use of components but documentation is public | Mandatory for State; the only sanctioned design system | Active (v1.14.x in early 2026) | Yes | High if applied outside .gouv.fr scope | Optional module |
| 16 | numerique-gouv/dsfr-skill | github.com/numerique-gouv/dsfr-skill | Background only (reference architecture) | DINUM | fr-FR (DSFR) | Reference SKILL.md layout for a French design-system skill | Demonstrates a working "SKILL.md + per-component reference dir" packaging from a credible French gov source; uses `references/` lazy-load pattern; documents 23 of ~60 DSFR components | Scope is component documentation, not French prose; not a style/voice skill | DINUM (Etalab Open Licence 2.0); per the numerique-gouv org repository listing, the repo shows 0 stars and 11 forks, last updated 15 January 2026 (about 4.5 months before the 27 May 2026 cutoff) | Yes | Low | Architecture inspiration |
| 17 | alxbd/boileau SKILL.md | github.com/alxbd/boileau/blob/main/SKILL.md | **Primary structural base for AI-tic patterns** | alxbd (independent) | fr-FR | Editing (humanising LLM output) | 38 numbered patterns with avant/après, anchored on identified French-native sources (Wikipédia "Identifier l'usage d'une IA générative", Isma's "40 marqueurs", Daria décrypte l'IA); explicitly French-native, not translated from English; covers connectors-en-pluie, doublets d'adjectifs, `permet de`/`constitue`/`représente`, faux-soutenu (`effectuer` vs `faire`, `problématique` vs `problème`), tiret cadratin overuse, listes à puces en gras+deux-points, conversational artefacts (`Bien sûr !`, `J'espère que cela vous aide`), didactic posture (`Ce qu'il faut comprendre`), self-validation (`et c'est précisément le but`), hedging stacks | License unspecified on file; ~765 lines, 40 KB — too big to import wholesale into context; risks overcorrection if applied without "preserve technical precision" guardrails | Small repo (0 stars, 1 author) but content quality is high and methodology is transparent | January 2026 commit timestamp visible | Yes (extensive avant/après) | Medium (over-edit) | Easy as inspiration; license must be clarified before verbatim reuse |
| 18 | StealthyLabsHQ/plume-naturelle (in ai-edu-skills-FR) | github.com/StealthyLabsHQ/ai-edu-skills-FR | Reject as primary; cherry-pick markers only | StealthyLabsHQ | fr-FR | Background research on AI-marker catalogues | 48 patterns, 8 phases, 38 mathematical formulas across 3 tiers (PPL, GLTR, DetectGPT, σ²_D); MIT licence | Explicit goal is detector evasion: "Estimation : un texte IA brut score 85-99 % sur Compilatio. Avec le skill complet… l'objectif est 5-20 % (zone invisible pour Turnitin)" — this is exactly what the user said to NOT optimise for; the math-heavy approach is academic/orthogonal to "clearer prose"; some patterns will damage technical precision | 1 star, single contributor | Active | Yes | High (detector-evasion drift) | Reject |

## 3. Recommended architecture

**Package name:** `fr-tech-prose` (or `claude-skill-fr`).

**File layout:**

```
fr-tech-prose/
├── SKILL.md                          # ~1800 tokens — core
├── modules/
│   ├── ui-strings.md                 # ~600 tokens — UI, ICU/Fluent, errors
│   ├── fr-ca-overrides.md            # ~400 tokens — only loaded when fr-CA mode triggered
│   └── inclusive-writing.md          # ~300 tokens — opt-in, off by default
├── references/
│   ├── glossary-fr.tsv               # term | fr-FR | fr-CA | leave-as-en | note
│   ├── ai-tics-checklist.md          # 20-30 boileau-derived markers, lazy-load
│   ├── typography-cheatsheet.md      # NBSP, guillemets, accented caps
│   └── icu-fluent-placeholders.md    # syntax preservation examples
├── linter/
│   ├── .vale.ini                     # Vale config skeleton (French custom style)
│   └── vale-fr-tech/                 # custom Vale rule pack (YAML files)
└── README.md                         # how to install, when each module activates
```

**Module split decision:** **core + 3 lazy-load modules.** Reasoning: SKILL.md content stays in context for the duration of the conversation, so keep judgement rules tight (~1800 tokens). Volume content (glossary, AI-tic catalogue, per-pattern examples) lives in `references/` and is loaded on demand via the skill body's instructions, following the `numerique-gouv/dsfr-skill` pattern.

**Approximate SKILL.md length:** 1500–2000 tokens for core; 600 for UI module; 400 for fr-CA overrides. Sum stays under 3 000 tokens even when all modules trigger.

**Include examples?** Yes — short bilingual avant/après pairs (3–5 lines each) inline in SKILL.md for the 12 highest-value rules. Longer examples stay in `references/ai-tics-checklist.md`.

**Include glossary files?** Yes, single TSV with columns `term_en | fr-FR | fr-CA | leave-as-english | rationale`. ~120 entries covering dev terminology, anglicism resolutions, false-friends.

**Include linter configs?** Yes, a `.vale.ini` skeleton and a starter custom Vale pack (~20 rules: NBSP, guillemets, accentuated capitals, banned anglicisms list, banned AI connectors). Grammalecte/LanguageTool are referenced in the README but not packaged.

**Include locale-specific files?** Yes — `fr-ca-overrides.md` as a separate module, plus the fr-CA column in the glossary.

**How agents decide which module/locale:**
- Default to **fr-FR**.
- Activate **fr-ca-mode** if any of: (a) repo `package.json` `locales` contains `fr-CA`/`fr_CA`; (b) i18n source files match `**/fr_CA/**` or `**/fr-CA/**`; (c) the user explicitly requests Québec/Canadian French; (d) any sibling text already uses `courriel`, `clavardage`, `pourriel`, `magasiner`.
- Activate **ui-strings** module if the file extension is `.ftl`, `.properties`, `.po`, `.json` under `locales/`/`i18n/`, `.arb`, `.xcstrings`, `.resx`, or if ICU `{x, plural, …}` or Fluent `{$var}` syntax appears in the user prompt.
- Activate **inclusive-writing** only on explicit user request — the default for tech docs is the Microsoft/Mozilla pragmatic rewrite ("La connexion est établie." instead of "Vous êtes connecté(e).").

## 4. Rule families to port into SKILL.md (15 families)

1. **Default voice = vouvoiement, with rewrite-away-the-pronoun as preferred escape.** Sources: Microsoft fr-FR §3.1.8, Mozilla fr besogne, WordPress.com fr. Why: fr-FR Microsoft mandates `vous` + masculine default; Mozilla and WordPress.com both recommend rewriting to avoid the gendered adjective ("Are you sure…?" → "Voulez-vous vraiment…?", "You are now connected." → "La connexion est établie."). Applies to: UI, errors, docs, README. Exception: technical logs may be impersonal/no-subject. fr-CA: same vouvoiement default; `tu` only in informal product copy. Example: "Saisissez votre mot de passe." not "Vous devez saisir votre mot de passe."

2. **UI string voice = infinitive without terminal punctuation, imperative with.** Source: WordPress.com fr explicitly. Why: this is the single rule that disambiguates button labels ("Supprimer") from sentence captions ("Pour supprimer, cliquez ici."). Applies to: UI labels, menu items, buttons, tooltips. Exception: titles of dialog boxes are substantives, not verbs (per Mozilla fr "Installation interactive", not "Comment installer"). fr-FR = fr-CA. Example: button `Save` → `Enregistrer`; toast `Settings saved.` → `Paramètres enregistrés.`

3. **English `-ing` titles, gerunds, and "How to" become French substantives.** Source: Mozilla fr besogne verbatim. Why: titles and section headers sound natural and shorter as nouns. Applies to: docs, README sections, changelog headers. Exception: how-to tutorials can keep imperative when the procedural framing is the point. Example: "Configuring the cache" → "Configuration du cache"; "Installing Docker" → "Installation de Docker".

4. **"This will + action" in confirmations → "Cette action + futur".** Source: Mozilla fr besogne verbatim. Why: more idiomatic than literal "Ceci…". Applies to: UI confirmations, irreversible-action warnings. fr-FR = fr-CA. Example: "This will overwrite your changes." → "Cette action écrasera vos modifications."

5. **Drop English possessive determiners; prefer the definite article.** Source: Microsoft fr-FR. Why: French uses the definite article where English defaults to possessives. Applies to: docs, UI, error messages. Exception: keep the possessive when ambiguity would result. Example: "Contact your administrator." → "Contactez l'administrateur." not "Contactez votre administrateur."

6. **Error message canonical pattern: `Impossible de <action>.` + optional reason + optional remedy on a new line.** Source: synthesis of Microsoft fr-FR plain-clarity principle + Mozilla fr "S'adresser à l'utilisateur" + the implicit pattern in the boileau examples (no "Oops!"). Why: avoids "An error has occurred" calques, avoids blaming the user, avoids apologetic register. Applies to: user-facing errors, validation messages. Exception: technical logs use impersonal `Échec : <cause>` form. fr-FR = fr-CA. Example: "Impossible d'enregistrer le fichier. Vérifiez que vous disposez des droits d'écriture sur le dossier cible."

7. **Mandatory NBSP before `; : ! ? » %` and inside French guillemets.** Sources: Lexique de l'Imprimerie nationale (canonical), Mozilla fr besogne (verbatim table). Why: if the LLM emits `«hello»` or `! ` without the NBSP, the output looks instantly wrong; in Markdown the NBSP is preserved through code blocks but stripped by some markdown processors — flag this. Applies to: all prose. Exception: never inside code fences, inline ` ``code`` ` spans, URLs, regex patterns, JSON/YAML values, CLI examples. Use `U+00A0` (regular NBSP) by default; `U+202F` (narrow NBSP) is technically correct before `;:!?` but support is patchy.

8. **Accentuated capitals: always.** Source: Mozilla fr besogne, Imprimerie nationale, Académie française. Why: Common omissions like `Etat`, `A propos`, `Evolution`, `Edition` are immediate AI-tells. Applies to: titles, sentence-initial words, UI headings. fr-FR = fr-CA. Example: `À propos`, `État du serveur`, `Évolution récente`, `Échec de la requête`.

9. **French guillemets `« … »` not `"…"` or `"…"` in prose; preserve straight ASCII quotes inside code/JSON/CLI examples and inside ICU/Fluent string literals.** Sources: Mozilla fr besogne (`Nous n'utilisons pas les guillemets anglophones ""`), Imprimerie nationale. Why: the LLM frequently uses curly English quotes from prior English training. Exception: never alter quotes inside fenced code blocks, JSON strings, regex, or anything inside ICU `'…'` quoting. Example: prose `Cliquez sur « Enregistrer ».` but code `git commit -m "fix: ..."` stays as-is.

10. **Banned high-frequency AI connectors / hedges / nominalisations.** Source: boileau §13, §14, §32–§37. Why: opening every paragraph with `Par ailleurs,` / `De plus,` / `En outre,` / `Cependant,` / `Néanmoins,` / `En effet,` / `Ainsi,` / `Par conséquent,` is the strongest fr-LLM tell. Same for `il convient de noter que`, `force est de constater`, `à l'aune de`, `dans cette optique`, `il est important de noter que`, `permet de`, `constitue`, `représente`, `s'inscrit dans`, `joue un rôle clé`. Applies to: docs, READMEs, PR descriptions, changelogs. Exception: technical specs may legitimately use `par conséquent` or `en effet` when introducing genuine causal/illustrative relations — frame the rule as "default to dropping the connector; keep it only when removing it breaks the logical link." Frame as **reader-clarity editing, not detector evasion.**

11. **Banned doublets, triades, parallélismes négatifs.** Source: boileau §6, §8, §9. Why: `simple et intuitif`, `robuste et fiable`, `rapide, efficace et fiable`, `Ce n'est pas un X, c'est un véritable Y` are mechanical LLM patterns. Applies to: marketing-adjacent docs, blog-style READMEs. Exception: legitimate enumerations with 3 distinct items are fine — the rule targets synonymic doublets.

12. **Anglicism resolution table — graded.** Source: Clés de la rédaction (anglicismes syntaxiques/sémantiques/de coordination), Microsoft fr-FR, boileau §16. Grade each as **safe-and-useful / useful-with-exceptions / dangerous-if-mechanical / glossary-only**:
    - **Replace mechanically:** `permet de` (vide), `adresser un problème` → `traiter`, `faire du sens` → `avoir du sens`, `supporter X` (meaning "support") → `prendre en charge X`, `assumer` (in the English sense) → `supposer`, `application` (job sense) → `candidature`, `digital` (tech sense) → `numérique`, `définitivement` (= "definitely") → `certainement`, `opportunité` (= "occasion") → `occasion`, `basé sur` → `fondé sur` or `à partir de`, `en termes de` → `pour` or `côté`.
    - **Useful with exception:** `librairie` → `bibliothèque` for code libraries; tolerate `librairie` only inside repo names or established product names. `éventuellement` (= "possibly") → `peut-être` / `le cas échéant`; do not change French-sense "eventually" if context is `éventuel`.
    - **Leave as English (developer accepted):** `pull request`, `merge request`, `commit`, `branch`, `rebase`, `cherry-pick`, `endpoint`, `framework`, `middleware`, `cache`, `debug`, `front-end`, `back-end`, `pipeline`, `runtime`, `linter`, `parser`, `tooling`. Demande de fusion / demande de tirage are correct fr-CA OQLF picks, but in fr-FR engineering text they sound forced — the skill should *not* force them when the codebase, repo, and team already use English.
    - **Locale-split:** `email` → `e-mail` or `courriel` in fr-FR (both acceptable in modern engineering writing); `courriel` in fr-CA (OQLF mandatory). **Never `mél`** — FranceTerme but not real-world. `spam` → `spam` in fr-FR; **`pourriel`** in fr-CA. `cookie` → `cookie` in fr-FR; **`témoin`** is OQLF prescriptive but `cookie` is the de facto fr-CA dev term too — keep `cookie` unless the project explicitly uses témoin. `login` (verb) → `se connecter` or `ouvrir une session` (latter preferred fr-CA per OQLF). `issue` → `ticket` (fr-FR engineering), `problème` for user-facing text; `issue` may be left as-is in PR/Jira context.

13. **Plural and gender placeholder safety with ICU MessageFormat / Mozilla Fluent.** Source: CLDR Plural Rules, ICU userguide, Fluent docs. Why: French plural categories per CLDR are `one` (for both 0 and 1) and `other` only — the LLM must produce `{count, plural, one {# fichier} other {# fichiers}}` and **never** emit `=0` for "Aucun" unless the message logic needs the exact-match. The variants `zero`, `two`, `few`, `many` for fr-FR are useless. **Never translate keys, never translate placeholder names, never reorder `*[other]` arms,** never localise the variant keyword. The apostrophe `'` is the MessageFormat quote character — `aujourd'hui` in an ICU template must be written `aujourd''hui`. Applies to: any UI string editing. fr-FR = fr-CA at CLDR level.

14. **Typography that the LLM must NOT break.** Source: synthesis. Why: a French-quality fixer can corrupt working content. Never apply French typography to:
    - Anything between triple-backtick fences.
    - Anything inside inline backticks.
    - URLs, file paths, command-line invocations, environment variable names.
    - JSON/YAML/TOML keys and string values (a NBSP injected into a JSON key breaks parsers).
    - Regex patterns.
    - ICU `{…}` and `'…'` quoting.
    - Fluent `{$var}`, `{-term}`, `*[other]` syntax.
    - Markdown link targets `[label](URL)` — only `label` is prose.
    - HTML attribute values.

15. **Tone calibration to the target genre — single explicit selector.** Source: synthesis of WordPress.com (formal), Mozilla (mixed per product), DSFR (institutional), Microsoft (conversational but technical). Why: an LLM trained mostly on English flips registers within the same response (boileau §5). Default to **"sober technical, vouvoiement, no marketing register, no diminutives, no exclamation marks except for genuine errors."** Apply per-genre defaults from §6 of this report.

## 5. Rules to keep OUT of SKILL.md

| Goes into | Rule families | Why not in skill |
|---|---|---|
| **Grammalecte / LanguageTool / Hunspell in CI** | Basic spelling, accent agreement, gender-number agreement, repeated words, doublons, basic punctuation | High-volume, mechanical, well-tooled, fast, deterministic. Putting them in SKILL.md wastes context and the LLM doesn't outperform Grammalecte on these. |
| **Custom Vale style pack (`fr-tech-prose`)** | NBSP before `; : ! ?`, French guillemets enforcement, accentuated capitals, banned-anglicism list, banned-AI-connector list, sentence-length thresholds | Vale handles markup correctly (ignores code fences); rules are mechanical; configurable per-file scope; visible in PR checks. The skill teaches *the intent*, the linter enforces *the form*. |
| **Glossary file (`glossary-fr.tsv`)** | Locked term mappings, product names, brand do-not-translate list, fr-FR/fr-CA divergences for specific terms | Glossary scales linearly with vocabulary; bloating SKILL.md degrades all answers. The skill *references* the glossary by name. |
| **Translation memory / Fluent / ICU files** | Plural variants per language, gender variants, branded interpolation tokens | These belong to the project repository, not the skill. The skill teaches placeholder integrity, not the inventory. |
| **Human review checklist** | Inclusive-writing decisions (point médian vs épicène rewrite vs masculine default), brand-tone calibration, marketing slogan adaptation, legal-text wording, cultural-reference substitution | Judgement calls with organisational policy weight. The skill flags them for human attention; it does not decide. |
| **Background / not enforced** | DSFR-specific component vocabulary (unless the project is a `.gouv.fr` site), FranceTerme officialese (`mél`, `fouineur`, `philoutage`), OQLF prescriptive picks not adopted by industry (`fureteur`) | Including them as rules would actively damage output quality. |

## 6. Genre defaults table

| Genre | Default voice | Sentence length | What to include | What to avoid | fr-FR vs fr-CA differences |
|---|---|---|---|---|---|
| UI button label | Infinitive, no period | 1–3 words | Verb action only | Possessives, "Cliquez pour…", emoji | None material |
| UI menu item | Infinitive or substantive, no period | 1–3 words | Substantive for sections (`Paramètres`), infinitive for actions (`Exporter`) | "Comment…", question forms | None |
| UI placeholder | Substantive or short instruction, no period | ≤ 5 words | What to enter (`Adresse e-mail`), example with `ex. :` | Full sentences | fr-CA: `Adresse courriel` preferred |
| Tooltip | Short impersonal sentence with period | 1 sentence | Hint or shortcut | Marketing register | None |
| Validation message | Impersonal or vous, period | 1 short sentence | Specific problem + correction | "Erreur :" prefix, blame | None |
| User-facing error | `Impossible de … .` + reason or remedy | 1–2 sentences | What failed, what to try; recovery action if the user can act | Apologies, "Oups !", stack-traceish terms, blame | None |
| Developer log message | Impersonal, no subject, period optional | ≤ 1 line | Event + identifier; structured fields prefer key=value | Localised in CI logs at all (often keep English); user-only French | Same |
| README / tutorial | Vous + imperative for steps; impersonal for prose | Mixed | Goal, prerequisites, steps, expected output, troubleshooting | "Bienvenue !", "N'hésitez pas", "J'espère que cela vous aide" | None |
| API reference | Impersonal, declarative present | 1–2 sentences per element | Type, default, range, side effects, errors thrown | Marketing adjectives, "permet de" without object | None |
| Code comment | Impersonal, fragment OK | 1 line typical | Why, not what; assumptions; invariants; TODO with owner | Translated identifier names, decorative banners | None |
| Docstring / Javadoc / KDoc | Impersonal, declarative present, infinitive for "Returns…"/"Throws…" patterns | 1–3 sentences + `@param` / `@return` | Description, params, return, errors, since-version | First person, exclamation marks | None |
| Changelog / release note | Infinitive past-action pattern (`Ajout de…`, `Correction de…`) OR third-person past (`Corrige…`) — pick one and stick to it | 1 line per entry | What changed; ticket reference; breaking-change flag | "Nous avons…", "Vous allez adorer", emojis in headings | None |
| PR description | First-person plural or impersonal | 3–10 lines | What, why, how to test, screenshots/links, breaking change | Boilerplate apology, AI conclusion sentences | None |
| Review reply | Vous if reviewing colleague's PR; tu if internal team convention; impersonal for technical points | 1–3 sentences | Specific code-level observation; suggested patch | Sycophancy ("Excellente question !"), didactic posture | None |

## 7. High-risk contradictions and recommended decisions

1. **Microsoft masculine default vs inclusive writing.** Microsoft fr-FR §3.1.8: "always use the masculine gender." Mozilla fr besogne: rewrite to avoid the gender ("La connexion est établie."), point médian as last resort. Académie française has formally opposed point-médian; INSP/government communications guide is moving toward épicène. **Decision: default to the Mozilla rewrite strategy** (rewrite to avoid the gendered adjective entirely). Fall back to masculine if the rewrite damages clarity. Use point médian only on explicit project policy. Never use parenthetical `(e)` in UI strings — they degrade screen-reader experience.

2. **FranceTerme official terminology vs common dev usage.** **Decision: ignore the unusable FranceTerme picks entirely** — `mél`, `fouineur`, `frimousse`, `philoutage`, `ordiphone`, `manche à balai`, `cybercaméra`, `témoin de connexion`, `bloc-notes` for blog. Keep only the FranceTerme picks that match industry usage (`courriel`, `mégadonnées`, `numérique`, `infonuagique` in fr-CA only). The skill cites this trade-off explicitly.

3. **OQLF Québec terminology vs France French industry usage.** **Decision: locale-scoped glossary, no cross-application.** Never push `fureteur` to fr-FR text; never push `clavardage` or `pourriel` to fr-FR. Inside fr-CA, prefer OQLF picks (`courriel`, `clavardage`, `pourriel`, `magasiner`), but tolerate the English borrowing if the codebase already uses it.

4. **WordPress.com formal `vous` vs Mozilla product-specific `tu`.** **Decision: vous by default for documentation, UI, and errors.** Use `tu` only when explicitly instructed (some consumer products and onboarding flows do choose `tu`).

5. **Plain-language pressure (Canada.ca, ISO plain-language standard) vs technical precision in API docs.** **Decision: plain-language wins for user-facing text; technical precision wins for API reference, error catalogues, and security advisories.** When in doubt for API references, prefer precise nominalisations (`délégation d'authentification`) over folksy paraphrase (`quand on confie l'authentification à quelqu'un d'autre`).

6. **Anti-anglicism vs accepted developer English terms.** **Decision: the "leave as English" list in rule family 12 above is authoritative.** When the project repository already uses an English term in identifiers, do not translate it in surrounding French prose unless the project glossary mandates a French alternative.

7. **French typography vs Markdown/code readability.** **Decision: typography only outside code spans and code fences.** The skill explicitly forbids applying NBSP, accented capitals, or guillemets inside backtick spans, fenced code, JSON/YAML/TOML, regex, URLs, CLI examples, and ICU/Fluent literals.

8. **UI infinitive vs imperative.** **Decision: WordPress.com rule wins** — infinitive without terminal punctuation, imperative with terminal punctuation. This is the most cleanly enforceable rule.

9. **DSFR institutional tone vs developer-doc tone.** **Decision: DSFR is an opt-in module activated only for `.gouv.fr` projects.** Default for SaaS/dev-tooling docs is the Microsoft/Mozilla conversational-technical voice, not DSFR's institutional register.

10. **AI-tic removal vs legitimate technical phrasing.** **Decision: frame every AI-tic rule as "default to removing, keep if removing damages meaning."** `Par conséquent` is allowed when introducing a real causal link; `permet de` is allowed when the verb that follows is itself meaningful (`l'API permet de filtrer par date` is fine, `notre solution permet d'optimiser` is not). The skill flags candidates; it does not blindly strip.

## 8. Final synthesis

**Recommended primary base:** a **synthesis**, structured as `boileau-style AI-tic catalogue` (structural inspiration only; clarify licence before any verbatim reuse) + `Mozilla fr besogne` (paraphrased rules for typography, voice, `-ing`→substantive, "Cette action…") + `Microsoft fr-FR` (voice baseline, conjunction modernisation, anglicism diagnostics) + `Bureau de la traduction Clés de la rédaction` (graded anglicism diagnostics) + `CLDR/ICU/Fluent` (placeholder integrity). No single source is sufficient.

**Secondary sources (loaded on demand or cited in glossary):** OQLF Vitrine linguistique (fr-CA terminology lookup), Canada.ca Content Style Guide (fr-CA web plain-language defaults), Lexique de l'Imprimerie nationale (typography canon for the linter), WordPress.com fr (UI infinitive/imperative rule).

**Background-only sources:** FranceTerme (cite when an official term IS in industry use; ignore the unusable ones), DSFR + numerique-gouv/dsfr-skill (only when working on `.gouv.fr` projects; the dsfr-skill repo is an excellent architecture model regardless), Mozilla general L10n guide (trademark handling).

**Sources to avoid as primary:**
- **StealthyLabsHQ/plume-naturelle** — explicit detector-evasion framing, math-heavy, orthogonal to the user's stated goal.
- **FranceTerme as a glossary backbone** — too much folkloric content.
- **OQLF as a glossary backbone for fr-FR** — Quebec-locked picks will sound forced.
- **Sun Microsystems 2005 fr style guide** — historical interest only; Mozilla fr besogne has already absorbed and updated what was usable.

**Recommended next step to create the actual SKILL.md:** 
1. Clone the `numerique-gouv/dsfr-skill` repository layout (SKILL.md + `references/` lazy-loaded files + `.claude-plugin/plugin.json` + sync scripts) as the directory skeleton.
2. Draft `SKILL.md` core in ~1800 tokens, structured around the 15 rule families above, each with one 2-line example.
3. Author `references/ai-tics-checklist.md` paraphrasing 20 boileau patterns under a clarified licence (request CC-BY from alxbd or rewrite from cited primary sources: Wikipedia "Identifier l'usage d'une IA générative", Isma's "40 marqueurs", and Daria décrypte l'IA, which boileau itself credits).
4. Build `glossary-fr.tsv` with 120 entries seeded from Microsoft fr-FR + OQLF GDT + Clés de la rédaction.
5. Author `modules/ui-strings.md` covering ICU/Fluent integrity, WordPress.com infinitive/imperative rule, error-message canonical pattern, placeholder safety.
6. Ship `linter/.vale.ini` + `linter/vale-fr-tech/` with ~20 starter rules.
7. CI integration: run Vale on `*.md` and `*.po` excluding code fences; run Grammalecte/LanguageTool on rendered prose only; require glossary review on changes to translated UI strings.

**10–15 concrete principles the final skill should enforce:**

1. Default vouvoiement; rewrite to avoid the gendered adjective before reaching for inclusive markers.
2. UI strings: infinitive without terminal punctuation, imperative with.
3. Translate English `-ing`/"How to" headings as French substantives.
4. Rewrite "This will…" confirmations as "Cette action…".
5. Drop English possessive determiners; use definite article.
6. Error message canonical form: `Impossible de … .` plus optional reason and optional actionable remedy; never apologetic, never blaming.
7. Mandatory NBSP before `; : ! ? » %` and inside French guillemets — and never inside code, JSON/YAML, URLs, CLI examples, ICU/Fluent literals.
8. Accentuated capitals always (`À propos`, `État`, `Évolution`, `Édition`, `Échec`).
9. French guillemets `« … »` in prose only; ASCII quotes inside code/JSON/CLI.
10. Default to dropping leading connectors (`Par ailleurs,` / `De plus,` / `Cependant,` / `Ainsi,` / `En effet,`); keep them only when they introduce a real logical link.
11. Avoid synonymic doublets (`simple et intuitif`), forced triades (`rapide, efficace et fiable`), parallélismes négatifs (`Ce n'est pas X, c'est Y`), pseudo-soutenu (`effectuer`/`problématique`/`s'avère`/`disposer de`), inflated participles (`témoignant de`, `s'inscrivant dans`).
12. Banned anglicisms with mechanical replacement: `permet de` (vide), `adresser un problème`, `faire du sens`, `supporter` (sense "support"), `basé sur`, `en termes de`, `digital`, `définitivement`, `opportunité` (= occasion), `assumer` (= suppose), `application` (= candidature).
13. Leave English as English for established dev terms (`pull request`, `commit`, `branch`, `framework`, `middleware`, `cache`, `endpoint`, `linter`, `parser`) unless the project glossary mandates otherwise.
14. Locale-aware terminology: `e-mail`/`courriel` fr-FR, `courriel` fr-CA; `spam` fr-FR, `pourriel` fr-CA; never `mél`, never `fouineur`, never `frimousse`, never `philoutage`.
15. Preserve ICU MessageFormat (`{count, plural, one {…} other {…}}`, `=0` exact-match, `'…'` quoting), Mozilla Fluent (`{$var}`, `{-brand}`, `*[other]`) and `%s`/`%d`/`%(name)s` placeholders verbatim; French CLDR plural categories are only `one` and `other`.
