# pr-qa-review

An orchestrated QA review workflow for pull requests and code changes. The package helps an agent inspect the diff,
requirements, design documents, runtime behavior, UI, APIs, logs, deployment manifests, and documentation, then save an
evidence-backed defect report.

The skill is intentionally user-invoked. Use it when you want a broad QA-style review rather than a narrow code review.
It does not modify product code unless the user explicitly asks for fixes.

## What it produces

A Markdown report under a user-selected path, usually `reports/<topic>.md`, with screenshots, logs, command output, and
links to relevant code. Each finding includes severity, classification, reproduction steps, actual and expected results,
and evidence.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/pr-qa-review
```

Or add it to your `apm.yml`:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/pr-qa-review@v1.0.0
```

Then run `apm install` and `apm compile`.

## Usage

Ask the agent to use `pr-qa-review` and provide the target PR, branch, commit, or local change set.
This is an example request, not a required template:

```text
Use pr-qa-review to review PR #123:
https://github.com/example/project/pull/123

Save the report to reports/pr-123-qa-review.md.

Focus on backend/API, UI, deployment, runtime logs, and security.
Do not modify source code, deployment state, or test data; only investigate and report bugs.
Do not run disruptive read-only checks, such as huge-range, malformed, cleanup, TTL, compaction,
or stress requests, unless you ask first or use an isolated disposable environment.
```


You can omit the focus line when you want the agent to infer all required tracks from the diff:

```text
Use pr-qa-review to review PR #123:
https://github.com/example/project/pull/123

Save the report to reports/pr-123-qa-review.md.
Do not modify source code, deployment state, or test data; only investigate and report bugs.
```

Optional runtime setup block, when a local stand exists and may need updating before the review:

```text
A local stand is available. You may update it to the PR version before the review.
After setup/update, switch to read-only mode and do not change source code, deployment state, cluster state,
or test data again.
```

Optional previous-run comparison block, when you want the report to reconcile prior findings. The agent should also
reconcile prior findings when they are already known from the current review context:

```text
Compare with the previous report:
reports/pr-123-qa-review-previous.md

For each previous finding, mark it as reproduced, not reproduced, superseded, accepted/out of scope,
or not rechecked with a reason.
```

The workflow can use local runs, a local cluster, browser automation, API calls, logs, metrics, Helm rendering,
and static analysis when available. After reading the diff, it should create a Required-By-Diff Coverage table for
tracks such as design, protocol compatibility, data lifecycle/retention, UI, deployment, and security, including the
owner for each track. User focus areas prioritize the review but do not remove required-by-diff tracks. If an important
tool is missing for a requested focus area, the agent should explain the value of installing or enabling it and ask
before relying on a weaker fallback.
