# Telemetry authoring: research

An editorial pipeline that collects evidence for a repository-independent skill on **instrumentation**: which signal
an event owes, what a record carries, the rate at which it may be emitted, and what a library may emit into a host it
never sees, across the JVM, Go, and Python. This folder is the audit trail; the skill is written from the results and
kept canonical in [`agent-packages/telemetry-authoring`](../../agent-packages/telemetry-authoring/).

The pipeline reuses the method of [`test-authoring`](../test-authoring/): readers are fixed before the first search,
the unit of evaluation is a rule with its detection, and every rule is judged on whether a writer who is rewarded when
review passes can satisfy it without the signal being worth anything.

| Reader | Situation |
| --- | --- |
| R1 Library author | Adds or changes a logger call or a counter in a library that ships to hosts it never sees |
| R2 Service author | Has written a branch that ends in a failure, a retry, a fallback, or a clamped value |
| R3 On-call engineer | Holds an alert and the emitted text, without the source, and decides whether to wait or intervene; served through R1, R2, and R4, never a consumer of the skill |
| R4 Reviewer | Holds a diff in which a signal appeared, changed, or is conspicuously absent |

Wording is out of scope and belongs to the developer-style skill of the language the message is written in. The
documentation a user-visible message owes belongs to `docs-page-authoring`.

## Method

| Step | Artifacts | What happened |
| --- | --- | --- |
| Seed | `seed_baseline.md` | What existing skills already said about logging, twelve positions stated from practice and sourced nowhere, and the recorded failures: a model review of pgjdbc/pgjdbc#2837 that checked the wording and the documentation and never asked whether the line answers the operator's question |
| Phase 1a: cross-cutting sources | `phase1a_prompt.md`, `phase1a_result.md` | Discovery over practitioner guidance, empirical research on logging code, the OpenTelemetry specification, metric-design guidance, project conventions, and agent skills |
| Phase 1b: per-ecosystem sources | `phase1b_prompt.md`, `phase1b_result.md` | Discovery over the Go, Python, and JVM primary documentation, OpenTelemetry per language, metric clients, project conventions, and linters; split from 1a because three ecosystems by three signals is wider than one pass covers |
| Phase 2: rules | `phase2_prompt.md`, `phase2_result.md` | Forty rules with detection and repair, six conflicts decided, the signal-choice rule built and tested on six named cases, the audit of the seed, and verification of every figure inside the pass |
| Synthesis | the skill itself | Written by the orchestrating agent from the results; no separate synthesis document |
| Trial | `ab-pr2837.md` | The skill tried on the review that seeded the research, with and without the skill |

All passes ran on Opus on 2026-09-12. The prompts are what the subagents were given, and the result files are what
came back, unedited.

## Findings

- **No source states which signal an event owes.** The skill's central rule is derived from six sourced criteria and
  labeled as derived; `phase2_result.md` §5 tests it on six cases, which serve as the regression fixture.
- **The ground is unoccupied.** Every published observability skill found works on the backend: querying,
  investigating, and defining objectives. None covers the author.
- **A repository instruction file is the weakest enforcement channel measured** in the one study of agent-written
  logging, so every rule in the skill carries its detection in the same sentence and names a linter rule id where one
  exists.
- **Seed positions that did not survive.** "A library does not export metrics" is contradicted by Prometheus's own
  guidance and replaced by "a library does not choose where its metrics go". "The steady state is silent" is
  replaced by one record per unit of work, or per state transition where the code owns no unit of work. The
  `MessageFormat` digit-grouping trap is JVM-only.
- **The ecosystems differ in kind on three points**: what a host sees when it configures nothing, Python's warnings
  channel for a condition the caller can fix, and the shape of a lost or stale context. A fourth difference,
  configuring against acquiring a logger, turned out to be one rule with two detections.
- **Corrections to phase 1** are named in `phase2_result.md` §11; sources that stayed unreachable had their claims
  dropped.

## Files

```text
seed_baseline.md                         the seed: house text, positions from practice, recorded failures
phase1a_prompt.md, phase1a_result.md     cross-cutting discovery
phase1b_prompt.md, phase1b_result.md     per-ecosystem discovery
phase2_prompt.md, phase2_result.md       rules, conflicts, the signal-choice rule and its six cases, seed audit, verification
ab-pr2837.md                             the skill tried on pgjdbc/pgjdbc#2837, with and without the skill
prompt_ab-pr2837.md, results_ab-pr2837-*.md   the trial's prompt and the two reviews, unedited
```

The phase prompts and results, the seed, and the trial's prompt and reviews are excluded from markdownlint by
`FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`, as the other research directories are.

## Status

The skill is in `agent-packages/telemetry-authoring`. The only trial covers a JVM library; Go, Python, and service
mode are exercised by the six worked cases in `phase2_result.md` §5 and by no agent run. The trial's prompt gave both
runs part of the answer and needs rebuilding before any count of findings from it is quoted.
