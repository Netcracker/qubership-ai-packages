# russian-developer-style: research

> Русская версия: [README.ru.md](README.ru.md).

Four-step editorial pipeline behind the `russian-developer-style` APM
package. The package itself lives in
[`agent-packages/russian-developer-style/`](../../agent-packages/russian-developer-style/);
this folder is the worklog that produced it.

## Method

| Step | Artefacts | What happened |
| --- | --- | --- |
| Phase 1: broad survey | `phase1_prompt.md`, `phase1_result.md` | A deep-research prompt collects style-source candidates. Cheap, broad, no synthesis. Finding: no ready-made Russian LLM skill targets technical text. |
| Phase 2: deep evaluation | `phase2_prompt.md`, `phase2_result.md` | The shortlist is re-evaluated for coverage, tone, false-positive risk, and overlap. Finding: no single source covers the brief alone, so a synthesis from Контур.Гайды, Microsoft RU L10n, Ozon Tech styleguide, Mozilla L10n, Нора Галь, and the LLM-tells corpus is needed. |
| Phase 3: synthesis | `phase3_prompt.md` → [`SKILL.md`](../../agent-packages/russian-developer-style/.apm/skills/russian-developer-style/SKILL.md) | The skill is assembled from the Phase 2 findings. The canonical copy lives in the package and is not duplicated here. |

Splitting the work in two phases keeps the deep evaluation cheap by
pre-filtering candidates, and preserves a reusable shortlist if the
brief later changes.

## Files

```text
phase1_prompt.md, phase1_result.md     style-source shortlist
phase2_prompt.md, phase2_result.md     deep evaluation, decision to synthesise
phase3_prompt.md                       prompt that assembled the skill
audit-2026-10-31-rule-ends.md          rules with no end condition: fixed and left alone (1.1.0)
cases/                                 regression cases, see cases/README.md
```

The phase 3 output lives in the APM package, not here, to avoid drift.
Files in this folder are frozen as a worklog; edit the skill at its
[canonical location](../../agent-packages/russian-developer-style/.apm/skills/russian-developer-style/SKILL.md).

## Naming history

The phase 2 and phase 3 prompts call the skill `ru-tech-prose`. That
was the working name during the research; the canonical slug is now
`russian-developer-style`.

The old name was dropped for two reasons. The `ru-` prefix is opaque
to routers and to anyone outside the Russian-speaking team:
`russian-` reads the same in any tool. The word `prose` narrowed the
scope: routers and readers alike treated it as a hint that the skill
applied only to long-form text (README pages, design docs,
multi-paragraph PR descriptions) and skipped it for one-line error
messages, three-word button labels, and short `msgstr` entries in
`.po` files. The skill applies to Russian developer text of any
length; the new name reflects that.

When you re-run the phased prompts, treat the slug `ru-tech-prose`
inside them as an artefact of the original run and substitute
`russian-developer-style` in the new result.

## Reusing for another language

The pipeline is language-neutral: survey, evaluation, and synthesis
do not depend on the target language. Most editorial rules survive a
language swap with few changes; the work concentrates in the style
sources, typography, spelling, and terminology.

1. Use `phase1_prompt.md` and `phase2_prompt.md` as a template. Swap
   the target language, the localisation guides, and the source
   candidates; the prompt structure stays.
1. Re-read the phase 2 candidate table. Re-run phase 2 in full only
   if the new language has a source absent from the Russian
   shortlist.
1. Re-run phase 3 with the new default language and substitute the
   sections on typography, quotation marks, dashes, non-breaking
   spaces, and ё/е-like dialectal features.
