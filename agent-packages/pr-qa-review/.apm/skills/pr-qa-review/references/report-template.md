# <Target> QA Review

Review target: <PR / branch / commit / local changes>
Date: <date>
Reviewer: <agent / user>
Scope: <read-only / runtime / UI / API / deployment / docs / security>
User focus areas: <none / list; focus is emphasis and does not remove required-by-diff tracks>
Environment: <local / Kubernetes namespace / URLs / versions>
Runtime version proof: <commit / image digest / chart version / endpoint / limitation>
Setup mutations before review: <none / commands / rollout actions / failed attempts>
Read-only review began at: <timestamp / after command / not applicable>
Coverage limitations:
<missing UI tooling / degraded traffic / scanners not run / access limits / skipped disruptive checks / none>
Orchestration: <named or generic sub-agents used / failed spawns / main-thread fallbacks / coverage impact>
Previous-run reconciliation:
<not applicable only when no prior findings are available / reproduced / not reproduced / superseded / not rechecked>
Required-by-diff coverage: <tracks run / partially covered / skipped with owner and reason>

## Summary

- Findings: <count>
- High: <count>
- Medium: <count>
- Low: <count>
- Existing issues: <count>
- Checks with no confirmed findings: <short list>
- Weakened or skipped coverage: <short list and reason>

## Required-By-Diff Coverage

| Required track | Owner | Status | Reason / evidence |
| --- | --- | --- | --- |
| <track> | <sub-agent / main thread / skipped> | <run / partial / skipped> | <short reason> |

## Previous-Run Reconciliation

| Prior item | Status | Reason / evidence |
| --- | --- | --- |
| <title> | <reproduced / not reproduced / superseded / accepted / not rechecked> | <short reason> |

## Finding Template

## N. <Short Bug Title>

Severity: High | Medium | Low

Classification:

<One or more of: PR regression, Existing issue, Design mismatch, Backend, API, UI/UX,
Accessibility, Runtime, Observability, Deployment/config, Security, Documentation, Test gap>

Problem:

<Explain the problem and why it matters.>

Code / Design:

- [`path/to/file.ext:123`](../path/to/file.ext#L123): <why this line matters>.
- [`docs/design.md:45`](../docs/design.md#L45): <requirement or expected behavior>.

Reproduction:

1. <Step, command, URL, UI path, or API request.>
1. <Next step.>

Actual Result:

<Observed behavior.>

Expected Result:

<Expected behavior.>

Affected Scope:

<Users, components, configurations, data, or workflows affected by the defect.>

Evidence:

```text
<Short relevant log, API response, metric, browser console output, network error, or command output.>
```

Screenshot or artifact: <path, not captured with reason, or not applicable>

Fix Direction:

<Evidence-supported remediation direction, or unknown. Do not present an unverified patch as fact.>

Retest Criteria:

<Checks the fixing agent should run to prove the defect is resolved and avoid regression.>

Notes:

<Optional uncertainty, suspected root cause, whether this is pre-existing, or follow-up test ideas. Separate suspected
root cause from confirmed evidence.>
