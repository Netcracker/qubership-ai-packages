# french-developer-style: research

Three-phase editorial pipeline behind the `french-developer-style` APM package. The package itself lives in
[`agent-packages/french-developer-style/`](../../agent-packages/french-developer-style/); this folder is the
audit trail behind it.

## Method

| Step | Artefacts | What happened |
| --- | --- | --- |
| Phase 1: broad survey | `phase1_prompt.md`, `phase1_result.md` | A deep-research prompt collects candidate style sources for French software-facing prose. Cheap, broad, no synthesis. Finding: no single ready-made French LLM skill targets developer text, so the brief is to synthesise. |
| Phase 2: deep evaluation | `phase2_prompt.md`, `phase2_result.md` | The shortlist is re-evaluated on coverage, fr-FR / fr-CA dialect fit, AI-tic catalogue overlap, false-positive risk on technical text, and licence constraints. Finding: combine the Mozilla francophone style guide, the Microsoft fr-FR localisation guide (paraphrased only), Bureau de la traduction + OQLF Vitrine linguistique for fr-CA, CLDR / ICU MessageFormat / Mozilla Fluent for placeholder safety, Lexique de l’Imprimerie nationale for typography, and a Boileau-style AI-tic checklist for structural inspiration. |
| Phase 3: synthesis | `phase3_prompt.md` → [`SKILL.md`](../../agent-packages/french-developer-style/.apm/skills/french-developer-style/SKILL.md) | The skill, modules, references, and starter Vale pack are assembled from the Phase 2 findings. The canonical copy lives in the package and is not duplicated here. |

Splitting the work in two evaluation phases keeps the deep evaluation cheap by pre-filtering candidates, and
preserves a reusable shortlist if the brief later changes.

## Files

```text
phase1_prompt.md, phase1_result.md     style-source shortlist
phase2_prompt.md, phase2_result.md     deep evaluation, decision to synthesise
phase3_prompt.md                       prompt that assembled the skill
```

The phase-3 output lives in the APM package, not here, to avoid drift. Files in this folder are frozen as a
worklog; edit the skill at its
[canonical location](../../agent-packages/french-developer-style/.apm/skills/french-developer-style/SKILL.md).

## Naming history

The phase-2 result file uses `fr-tech-prose/` once as a working directory name during the research. The
canonical slug is `french-developer-style`.

The `-prose` suffix was dropped for the same reason as in the English and Russian sister packages: skill
routers and human readers were treating `prose` as a hint that the skill only applies to long-form text
(README pages, design docs, multi-paragraph PR bodies) and skipping it for one-line error messages,
three-word button labels, and short `msgstr` entries in `.po` files. The skill applies to French developer
text of any length; the new name reflects that.

If you re-run the phased prompts, treat any stray `fr-tech-prose` or `french-prose-style` reference inside
them as an artefact of the original run and substitute `french-developer-style` in the new result.

## Locale strategy

Phase 2 settled on a single package with **fr-FR as the default** and **fr-CA as an explicit mode**, rather
than separate `fr-FR` and `fr-CA` packages. The rationale:

- Most editorial rules (voice, AI-tics, anglicism diagnostics, error-message pattern, placeholder safety) are
  shared across the two variants.
- The differences concentrate in a small terminology table (`courriel`, `clavardage`, `pourriel`, `magasiner`,
  `balado`) plus a thin layer of register choices (`ouvrir une session` vs `se connecter`).
- Maintaining two packages would have doubled the editorial surface for a fraction of unique content.

fr-BE and fr-CH have no dedicated module: they fall back to fr-FR. `septante` / `huitante` / `nonante` are
not introduced unless the repository already uses them.

## Reusing for another language

The pipeline is language-neutral: survey, evaluation, and synthesis do not depend on the target language.
Most editorial rules survive a language swap with few changes; the work concentrates in the style sources,
typography, spelling, terminology, and locale-mode strategy.

1. Use `phase1_prompt.md` and `phase2_prompt.md` as a template. Swap the target language, the localisation
   guides, the AI-tic catalogue language, and the source candidates; the prompt structure stays.
1. Re-read the phase-2 candidate table. Re-run phase 2 in full only if the new language has a source absent
   from the French shortlist (for example a national terminology body equivalent to OQLF or Académie
   française).
1. Re-run phase 3 with the new default locale and substitute the sections on typography (quotation marks,
   dashes, non-breaking spaces, accented capitals), placeholder rules (CLDR plural categories for the
   target locale), and anglicism diagnostics. Keep the licence caution on proprietary style guides — it
   applies to most national localisation guides.
