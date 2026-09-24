# Hand-over note

## What was established in the report

- **Symptom**: Nested reusable workflow `docker-build.yaml` is called by mutable tag, not SHA
- **Version scope**: v2.5.2, v2.6.1, main (2026-09-23)
- **Impact**: Caller repositories that pin `generic-go-build.yaml` by SHA do not constrain which `docker-build.yaml` runs
- **Grounding**: Org convention, GitHub documentation, current observable state
- **Reproducer**: Complete: curl commands, git queries, step results verified in a real workflow run (run 35839496302)
- **Duplicates**: Tracker search found PR #321 (proposed fix) and unrelated issues; no duplicate bug report found
- **Analysis**: Marked as lower confidence; explains the behavior but does not claim a defect in GitHub; stands without it

## Steps not executed (hand-over to person filing)

1. **Test the workaround**: Try calling `docker-build.yaml` directly by SHA from the caller workflow, with `skip-docker: true` in `generic-go-build.yaml`. This was not attempted; if it works, it is an alternative approach the project may prefer.
   
   Suggested command:
   ```bash
   # Draft a PR to qubership-ratelimit that calls docker-build.yaml directly by SHA
   # instead of through generic-go-build.yaml
   # See if this pin propagates through the workflow run as expected
   ```

2. **Survey caller repositories**: How do the 16 "observability repositories" mentioned in issue #367 currently pin `generic-go-build.yaml`? Do they have the same exposure? This context may strengthen the case for fixing it now vs. later.

3. **Verify the current state of PR #321**: It is open and includes this fix. If it is blocked or waiting, mentioning that in the issue may help prioritization.

## Questions for the person filing (before submitting)

1. **AI policy**: Netcracker/qubership-core-infra does not appear to have a public AI policy. The GitHub org's SECURITY.md and CONTRIBUTING.md carry no mention of machine-authored reports. **Do you want the standard machine-authorship disclosure ("Generated with Claude Code") added to the issue?** The project has not explicitly forbidden it, but some projects prefer not to have tooling disclosed. The issue can stand without it.

2. **Analysis section**: The issue includes a lower-confidence analysis of why this happens. **Does your team want to keep it?** It is marked as such, and the report stands without it. If the project prefers to avoid analysis altogether, delete the "Analysis" paragraph under "Additional context".

3. **Priority and scope**: The issue names two callsites (generic-go-build.yaml and generic-maven-build.yaml) as distinct expected outcomes. It also notes that PR #321 already proposes the same fix across four files. **Should the issue also mention maven-deploy.yml and maven-verify.yml**, or is the scope intentionally narrower?

4. **Severity**: The impact is "next push would run different build/publish logic with no commit in qubership-ratelimit". **What severity label should this carry?** (e.g., high, medium, low). The org's bug template includes a Version field but not a Severity/Priority field; the issue does not assume a level.

## Deliverable

The issue body in `result.md` is ready to copy into a GitHub issue create dialog or `gh issue create --title ... --body-file result.md`. It follows the bug_report.yml template from Netcracker/.github/.

**Title line** (ready to copy):
```
Nested workflow tags in generic-go-build.yaml are not constrained by caller's SHA pin
```

This names the symptom (mutable tag) and the affected surface (generic-go-build.yaml), not a fix.
