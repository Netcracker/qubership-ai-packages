# {{Target}} QA Review

Review target: {{PR / branch / commit / local changes}}
Date: {{date}}
Reviewer: {{agent / user}}
Initial base OID: {{complete OID / stable patch identity}}
Initial head OID: {{complete OID / stable patch identity}}
Final head OID: {{complete rechecked OID / stable patch identity}}
Target status: {{Current / Updated and delta reviewed / Stale / Preliminary}}
Permission boundaries: {{allowed, denied, and unresolved actions by mutation class}}
Runtime strategy: {{not required / existing aligned runtime / in-place update / clean deployment / limited evidence}}
Runtime alignment proof:
{{complete OID, artifact digest, configuration, migrations, external dependencies / limitation}}
Direct and indirect mutations: {{none / commands, affected resources, side effects, cleanup, and outcome}}
Pending permissions: {{none / bounded unresolved question; a material unresolved decision requires Preliminary status}}
Orchestration: {{owners, named or generic sub-agents, main-thread fallbacks, and ownership impact}}
Coverage limitations: {{none / unavailable evidence, partial or skipped tracks, reason, and impact}}

## Summary

- Findings: {{count; excludes suspected candidates}}
- Critical: {{count}}
- High: {{count}}
- Medium: {{count}}
- Low: {{count}}
- Confirmed: {{count}}
- Strong static evidence: {{count}}
- Existing issues: {{count}}
- Negative checks: {{count and short list}}
- Weakened or skipped coverage: {{count and short list with reason and impact}}

## Required-By-Diff Coverage

| Track | Why required | Capability | Implementation | Owner | Planned evidence | Status | Coverage impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| {{track}} | {{diff trigger}} | {{required capability}} | {{selected implementation}} | {{owner}} | {{evidence}} | {{complete / partial / skipped}} | {{none / reason and impact}} |

Every required row must be terminal. A `partial` or `skipped` row must state its reason and impact in Coverage impact.

## Main Findings

Include only `Confirmed` and `Strong static evidence` candidates in this section and in finding counts.

### N. {{Short Bug Title}}

Severity: {{Critical / High / Medium / Low}}

Finding confidence: {{Confirmed / Strong static evidence}}

Evidence source: {{Runtime / Browser / Test or executable check / Static / Mixed}}

Check outcome: {{Reproduced / Not reproduced / Not checked}}

Classification: {{PR regression / Existing issue / Design mismatch / domain}}

Problem:

{{Explain the violated requirement, impact, and why it matters.}}

Code or design anchors:

Resolve each link relative to the actual saved report location, or use a target-OID-pinned permalink.
Use both anchors below unless the first deterministically proves both cause and impact; in that case, delete the second.

- [`path/to/file.ext:123`]({{report-relative-or-target-OID-pinned-URL}}):
  {{defective implementation or configuration}}.
- [`docs/design.md:45`]({{report-relative-or-target-OID-pinned-URL}}):
  {{affected consumer, contract, test, or observable result}}.

Reproduction or deterministic analysis:

1. {{Step, command, request, UI path, or exact static reasoning.}}
1. {{Next step or decisive code path.}}

Actual result:

{{Observed result, or the behavior proved by deterministic static analysis.}}

Expected result:

{{Behavior required by the applicable contract.}}

Affected scope:

{{Users, components, configurations, data, or workflows supported by the evidence.}}

Evidence:

```text
{{Short log, response, metric, console output, network error, command output, or exact code path.}}
```

Screenshot or artifact: {{link / not captured with reason / not applicable}}

Evidence boundary:

{{Map claims to sources, distinguish observation from analysis, and state runtime, mock, and environment limits.}}

Fix direction:

{{Evidence-supported remediation direction, or unknown. Do not present an unverified patch as fact.}}

Retest criteria:

{{Checks that prove the defect is resolved without regression.}}

## Suspected Follow-Ups

Suspected candidates are not findings and are excluded from all finding, severity, and confidence counts above.

### {{Candidate title}}

Finding confidence: Suspected

Evidence source: {{Runtime / Browser / Test or executable check / Static / Mixed}}

Check outcome: {{Reproduced / Not reproduced / Not checked}}

Follow-up evidence needed: {{decisive check, capability, permission, or aligned runtime needed}}

Current evidence and limitation: {{anchors, observations, uncertainty, and coverage impact}}

## Previous-Run Reconciliation

| Prior item | Decision | Evidence or constraint |
| --- | --- | --- |
| {{title}} | {{Reproduced / Not reproduced / Superseded / Accepted or out of scope / Not checked}} | {{evidence or blocking constraint}} |

Use `Not applicable` only when no previous review findings are available.

## Rejected, Accepted-Risk, and Merged Candidates

| Candidate | Source | Decision | Evidence or basis |
| --- | --- | --- | --- |
| {{title or ID}} | {{track or prior review}} | {{Rejected / Accepted risk / Merged into finding N}} | {{contract, ADR, test, duplicate root cause, or contradictory evidence}} |

## Negative Checks

| Check | Result | Evidence | Scope boundary |
| --- | --- | --- | --- |
| {{check}} | {{no defect observed}} | {{command, output, artifact, or link}} | {{what the result does and does not prove}} |

## Artifacts and Validation

- Report validation: {{structure, counts, statuses, and links checked}}
- Artifacts: {{links / none}}
- Cleanup: {{completed actions and outcome / none required}}
- Final target recheck: {{complete final OID and comparison result / patch identity comparison}}
