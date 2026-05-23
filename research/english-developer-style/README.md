# English developer style: research

A four-step editorial pipeline that produced the
`english-developer-style` APM package. The package itself lives in
[`agent-packages/english-developer-style/`](../../agent-packages/english-developer-style/);
this folder is the audit trail behind it.

## Method

| Step | Artefacts | What happened |
| --- | --- | --- |
| Seed | `seed_SKILL.md` | LLM-distilled from ~20 native-speaker PR-review samples. |
| Phase 1: shortlist | `phase1_prompt.md`, `phase1_result.md` | Deep-research prompt asks for candidate style sources. Cheap, broad, no synthesis. |
| Phase 2: deep evaluation | `phase2_prompt.md`, `phase2_result.md` | Re-evaluate the shortlist on adoption, dialect, false-positive risk, and overlap. Conclusion: synthesise, no single source wins. |
| Phase 3: synthesis | `phase3_prompt.md` → [`SKILL.md`](../../agent-packages/english-developer-style/.apm/skills/english-developer-style/SKILL.md) | Compose the skill from the phase-2 findings. The output is the APM package skill — kept canonical there, not duplicated here. |

The two-phase split keeps deep evaluation cheap by filtering candidates
first, and leaves a reusable shortlist if the brief changes later.

## Files

```text
seed_SKILL.md                          native-speaker starting point
phase1_prompt.md, phase1_result.md     shortlist of style sources
phase2_prompt.md, phase2_result.md     deep evaluation, synthesis decision
phase3_prompt.md                       prompt that produced the skill
```

The phase-3 output lives in the APM package, not here, to avoid
drift. The research files in this folder are frozen as the audit
trail; edit the skill at its
[package home](../../agent-packages/english-developer-style/.apm/skills/english-developer-style/SKILL.md).

## Naming history

The phase prompts and `seed_SKILL.md` refer to the skill as
`english-prose-style`, and an intermediate release shipped it as
`english-developer-prose`. Both names are historical — the canonical
slug is now `english-developer-style`.

The `-prose` suffix was dropped because skill routers (and human
readers) were treating "prose" as a hint that the skill only applies to
long-form text — README pages, design docs, multi-paragraph PR bodies —
and skipping it for one-line error messages, three-word button labels,
and short `msgstr` entries in `.po` files. The skill applies to English
developer text of any length; the new name reflects that.

If you reuse the phase prompts to regenerate the skill, treat the
`english-prose-style` slug inside them as an artefact of the original
run and substitute `english-developer-style` in the new output.

## Reproducing for another dialect

The pipeline is dialect-agnostic. Most editorial rules survive the
switch unchanged; the work concentrates in spelling, quotation, and
date conventions.

1. Reuse `phase1_prompt.md` and `phase2_prompt.md` verbatim. The
   shortlist of sources does not depend on dialect.
1. Skim the phase-2 candidate table; rerun phase 2 only if a
   dialect-specific source needs deeper evaluation.
1. Rerun phase 3 with the new dialect default and switch the
   `Dialect policy` section of the skill.
