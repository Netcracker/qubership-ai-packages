# Hand-over note

## Gaps and decisions for the human

**AI policy disclosure**: The organization's CONTRIBUTING.md and SECURITY.md contain no explicit AI policy. No AI_POLICY.md was found in the repository. The person filing should verify whether qubership-core-infra or the Netcracker organization has an AI policy that requires disclosure of machine-authored reports. If disclosure is required, the issue body may need a note or line stating it was drafted with assistance.

**PR #321 vs. new issue**: PR #321 ("chore(deps): pin netcracker/qubership-core-infra action to 8a233b0") already addresses this for some workflows and versions. The person filing should decide:
- File this issue as-is, which will document the problem and can reference the existing PR.
- Comment on PR #321 with findings about additional workflows or versions it does not yet cover (e.g., any in generic-maven-build.yaml or older releases).
- Close this issue if PR #321 is comprehensive enough and the person filing believes commenting on the PR serves better.

## Unchecked findings

The following were in scope but not checked before drafting. They are candidates for the hand-over comment on the issue or for triage:

**Scope of the problem**: How do the 16 repositories mentioned in issue #367 currently pin `generic-go-build.yaml`? If they pin by SHA, they are all exposed to nested mutable tag references. This context could strengthen the urgency in the issue.

Query: Search Netcracker organization repositories for `.github/workflows/*.yml` files that call `generic-go-build.yaml@` or `generic-maven-build.yaml@`, and check whether they pin by SHA or by tag.

**Workaround viability**: The suggested workaround in the deep-review finding (DEP-01) — calling `docker-build.yaml` directly by SHA from the caller instead of through a generic-go-build.yaml — was not tested. If the workaround is viable (e.g., with `skip-docker: true` to skip nested docker-build in generic-go-build.yaml), it could be mentioned as a temporary mitigation while the fix is in progress.

Command to test (if the person filing chooses to pursue this):
```bash
# In qubership-ratelimit, call docker-build.yaml@<sha> directly with skip-docker: true
uses: Netcracker/qubership-core-infra/.github/workflows/docker-build.yaml@8a233b03c5b5355d59c1585ffdaa1f45ea816405 # v2.6.1
with:
  skip-docker: false  # or true to test nested behavior
```

## Issue structure notes

The issue was drafted using the section headings observed in recent issues filed by the person filing in this tracker (Goal, Context, Scope, Expected Behavior, Definition of Done, Reproducer, Evidence, Related), rather than the org's ISSUE_TEMPLATE/bug_report.yml form fields. This matches the pattern seen in issues #367, #371, and #401. If the project's process has changed or if the template is now enforced, the person filing may need to adapt the structure to match the web UI form.

## Channels and routing

The issue is routed to Netcracker/qubership-core-infra as decided by the person filing. No security channel is needed (not a vulnerability; a reproducibility and pinning practice issue). No redirect routing found in the contribution guide.
