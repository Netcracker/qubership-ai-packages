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
| Trial: error text | `ab-verify-release-deps.md` | The skill before and after the error-text rules, on the failure message of a Gradle verification task, three runs per arm on Haiku and Sonnet, judged blind and read by a fresh agent |
| Trial: library exception | `ab-max-result-buffer.md` | The skill before the change, its build-tool first version, and the shipped version, on the `maxResultBuffer` exception of pgjdbc, three runs per arm on Haiku and Sonnet, judged blind |

All passes ran on Opus on 2026-09-12; the error-text trial ran on 2026-10-26. The prompts are what the subagents were
given, and the result files are what came back, unedited, with one correction: `phase2_result.md` claimed that Ruff
TRY400/TRY401 report log-and-raise, which they do not, and the four occurrences now say so.

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
- **An error's text is the caller's channel, and the skill says what it carries.** The skill as first written spoke only
  of hosts, operators, and alerts, and a writer that loaded it for a Gradle failure message judged it irrelevant. In
  `ab-verify-release-deps.md` no writer loaded it from the old trigger and every writer loaded the revised one. Every
  writer that loaded the shipped version said why the check exists, gave a diagnose command with the module filled in,
  and said what to do either way; no writer without the skill did any of these. The rows a writer meets without the
  skill were dropped. On the `maxResultBuffer` exception of pgjdbc, in `ab-max-result-buffer.md`, the build-tool first
  version did not help and the general one did: it added why the limit exists, the property to set, and its accepted
  values. Asking for the change to the request beside raising a limit, for remedies that work as the code stands, and
  against example values that fail the same check brought an alternative to raising the limit into every message, with
  no wrong advice.
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
ab-verify-release-deps.md                the error-text rules tried on apache/jmeter#6846, before and after
prompt_ab-verify-release-deps.md, results_ab-verify-release-deps-*.md   that trial's prompts, messages, verdicts, and interrogation
ab-max-result-buffer.md                  the shipped rules tried on a pgjdbc exception, against the earlier versions
prompt_ab-max-result-buffer.md, results_ab-max-result-buffer.md   that trial's prompts, verdicts, and messages
cases/                                   regression cases with run-case.sh and check.py
```

The phase prompts and results, the seed, and each trial's prompt and results are excluded from markdownlint by
`FILTER_REGEX_EXCLUDE` in `.github/super-linter.env`, as the other research directories are.

## Status

The skill is in `agent-packages/telemetry-authoring`. The trials cover a JVM library's log line, a Gradle build check,
and a JVM library's exception; Go, Python, and service mode are exercised by the six worked cases in `phase2_result.md`
§5 and by no agent run. The pgjdbc trial's prompt gave both runs part of the answer and needs rebuilding before any
count of findings from it is quoted. That trial ran under `--setting-sources project`, which does not stop user-level
`CLAUDE.md` files, so its runs may also have seen the machine's own rules; `ab-verify-release-deps.md` describes the
isolation that works. The error-text trials exercised one Gradle check and one pgjdbc exception; an error response, a
CLI command that rejects its input, a lint, a pre-commit hook, a CI step outside the build tool, and a tool outside the
JVM have no run in the trials. Since 1.2.0, [`cases/`](cases/README.md) holds regression cases, including a library and
a Go CLI rejecting a trivial argument, where the subsection on the caller's channel has to add nothing.
