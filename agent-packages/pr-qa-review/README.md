# pr-qa-review

`pr-qa-review` is a user-invoked skill for evidence-backed QA review of a pull request, branch, commit, or local change
set. It derives required review tracks from the exact diff, discovers available implementations and local development
environments, asks before using them, and writes a mechanically validated evidence package. By default, it does not
execute review tools, contact runtimes, edit product code, deploy applications, or mutate runtime state.

The [skill workflow](.apm/skills/pr-qa-review/SKILL.md) is the entry point. Installing the package does not add an
always-on instruction or change unrelated conversations.

## Review workflow

The root agent follows a permission-gated state machine:

1. Discover the exact target, required coverage, available implementations, and configured local environments without
   executing evidence checks or contacting runtimes.
2. Present the discovered tools and environments and obtain explicit access permission.
3. Inspect approved runtimes and obtain an exact action budget for alignment or mutation.
4. Assign checks only to owners that can invoke their approved implementations.
5. Execute approved checks and retain every artifact immediately.
6. Reconcile candidates, recheck the target, and validate the durable evidence package.

An unapproved fallback, target, recovery action, or scope change returns the workflow to the applicable permission
gate. Missing or invalid evidence returns it to execution.

The exact local diff is authoritative. The workflow records complete base and head object IDs at the start and checks
the head again before completion, so a moving target cannot silently invalidate the report.

## Capabilities

The workflow discovers capabilities before requesting permission to use implementations. Capabilities can include
source and diff inspection, build and compilation, tests, browser automation, API invocation, runtime startup or
deployment, logs and metrics, configuration rendering, and dependency or security scanning.

The agent checks repository-native setup paths, harness-native implementations, configured runtime names, and
reasonable visible alternatives before declaring a capability unavailable. Passive discovery does not execute these
implementations or contact the runtime. The agent presents candidates, targets, modes, side effects, and fallbacks and
asks which ones it may use. If no viable implementation exists, the agent may propose a bounded, reversible
installation plan. Permission to install an implementation does not grant permission to execute it.

## Runtime strategy

Runtime evidence is valid only when the agent can prove that every changed deployed layer matches the target. Depending
on permissions and state, the root uses an already aligned runtime, proposes a state-preserving in-place update, or
proposes a clean isolated deployment. It explains the chosen strategy, the installation or migration evidence it may
hide, and the risk to existing state.

Material direct or indirect mutation requires an exact action budget. This includes deployment and test-data writes as
well as startup side effects such as migrations, recovery, cleanup, retries, background jobs, compaction, uploads,
cache warming, and lifecycle transitions. A failed deployment does not authorize unplanned rollback, recovery,
resource changes, Secret deletion, or cleanup. Denied actions remain visible as limited coverage with recorded impact.

## Coverage and delegation

The durable `review-state.json` ledger is the working gate. Each required track declares evidence slots; each check
records its approved implementation, callable owner, target, status, action, and retained artifacts. Coverage status is
derived from these checks. A review does not finish while a required slot is open.

Before delegation, the root gives each leaf exact revisions, a bounded track and file set, relevant requirements,
selected capability implementations, mutation permissions, the required evidence format, and, when applicable,
verified runtime URLs and proof. No-runtime tracks record those runtime details as `Not applicable`. Leaves do not
repeat target discovery, full diff classification, capability inventory, or runtime-readiness analysis.

Package agents are optional. Generic agents or the main thread can preserve the same coverage contract when named
agents are unavailable. Backward compatibility runs only when a public or persisted contract changes. It is a
lower-priority conditional track, and intended PR behavior remains primary.

## Findings and report

Finding confidence, evidence source, severity, and check outcome are independent axes. `Confirmed` findings have
executable evidence. `Strong static evidence` normally requires independent implementation and consumer or contract
anchors; one anchor is sufficient only when it proves both cause and impact. Suspected items remain in limitations or
follow-ups rather than the main defect list. Severity measures impact and recoverability, not how the evidence was
collected.

The agent records whether evidence came from runtime behavior, a browser, tests, static analysis, or a mixture. It
reconciles duplicates and rejected candidates before writing a report based on the
[report template](.apm/skills/pr-qa-review/references/report-template.md). The bundled validator rejects unresolved
permissions, actions outside approved budgets, open checks, missing UI evidence, ephemeral artifact paths, stale
targets, and inconsistent terminal states.

Until the package is released, the ledger schema and validator are internal workflow details and may evolve within
this pull request.

## Install

Install the package directly:

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/pr-qa-review
```

Or add it to `apm.yml`:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/pr-qa-review@v1.1.0
```

Then run `apm install` and `apm compile`.

## Usage

Provide a target, report path, and any known permissions or runtime access:

```text
Use pr-qa-review to review PR #123 and save the report to reports/pr-123-qa-review.md.
Do not modify source, deployment state, runtime state, or test data without asking first.
```

You can add available runtime evidence without prescribing a particular tool:

```text
Use pr-qa-review to review commit 0123456789abcdef and save the report to reports/change-qa-review.md.
A shared read-only environment is available at https://review.example.test.
Ask before any action that may restart workloads or trigger direct or indirect mutation.
```

Focus areas prioritize work but do not remove tracks required by the diff. The final report states the impact of every
capability or permission gap.
