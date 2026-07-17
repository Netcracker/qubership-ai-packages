# pr-qa-review

`pr-qa-review` is a user-invoked skill for evidence-backed QA review of a pull request, branch, commit, or local change
set. It derives required review tracks from the exact diff, evaluates source and runtime behavior where evidence is
available, and writes a self-contained defect report. By default, it does not edit product code, deploy or restart
applications, or mutate test data and runtime state.

The [skill workflow](.apm/skills/pr-qa-review/SKILL.md) is the entry point. Installing the package does not add an
always-on instruction or change unrelated conversations.

## Review workflow

The root agent follows eleven universal phases:

1. Identify the target.
2. Establish permissions and mutation boundaries.
3. Resolve exact base and head revisions.
4. Build the diff-driven coverage map.
5. Inventory available capabilities.
6. Align or validate the runtime environment.
7. Delegate independent tracks.
8. Run static, test, and runtime checks.
9. Confirm and deduplicate findings.
10. Recheck the target revision.
11. Write and validate the report.

The exact local diff is authoritative. The workflow records complete base and head object IDs at the start and checks
the head again before completion, so a moving target cannot silently invalidate the report.

## Capabilities

The workflow discovers capabilities before choosing implementations. Capabilities can include source and diff
inspection, build and compilation, tests, browser automation, API invocation, runtime startup or deployment, logs and
metrics, configuration rendering, and dependency or security scanning.

The agent searches repository-native setup paths and every available implementation before declaring a capability
unavailable. A repository harness, local program, language binding, remote service, or existing environment may provide
the same capability. If a required capability still needs installation, configuration, access, or deployment, the
agent explains the evidence it would unlock and asks the user before reducing coverage.

## Runtime strategy

Runtime evidence is valid only when the agent can prove that every changed deployed layer matches the target. Depending
on permissions and state, the root uses an already aligned runtime, proposes a state-preserving in-place update, or
proposes a clean isolated deployment. It explains the chosen strategy, the installation or migration evidence it may
hide, and the risk to existing state.

Material direct or indirect mutation requires user approval. This includes deployment and test-data writes as well as
startup side effects such as migrations, recovery, cleanup, retries, background jobs, compaction, uploads, cache
warming, and lifecycle transitions. When approval is unavailable, the affected runtime coverage remains partial or is
skipped with its impact recorded.

## Coverage and delegation

The required-by-diff coverage table is a working gate. Each required track records why it is needed, its capability and
implementation, owner, planned evidence, terminal status, and the impact of partial or skipped coverage. A review does
not finish while a required track lacks a terminal status.

Before delegation, the root gives each leaf exact revisions, a bounded track and file set, relevant requirements,
selected capability implementations, verified runtime URLs and proof, mutation permissions, and the required evidence
format. Leaves do not repeat target discovery, full diff classification, capability inventory, or runtime-readiness
analysis.

Package agents are optional. Generic agents or the main thread can preserve the same coverage contract when named
agents are unavailable. Backward compatibility runs only when a public or persisted contract changes. It is a
lower-priority conditional track, and intended PR behavior remains primary.

## Findings and report

Finding confidence, evidence source, severity, and check outcome are independent axes. `Confirmed` findings have
executable evidence. `Strong static evidence` follows from multiple independent code or contract anchors. Suspected
items remain in limitations or follow-ups rather than the main defect list. Severity measures impact and recoverability,
not how the evidence was collected.

The agent records whether evidence came from runtime behavior, a browser, tests, static analysis, or a mixture. It
reconciles duplicates and rejected candidates before writing a report based on the
[report template](.apm/skills/pr-qa-review/references/report-template.md). The report includes target identity,
coverage, findings, limitations, and enough evidence for independent retesting.

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
