# Hand-over note for the person filing

Nothing was filed or sent. The issue body is `draft.md`; this note is not part of it.

## Title and command

Title (names the symptom, not the fix):

```text
Callers that pin generic-go-build.yaml by SHA still run docker-build.yaml from a mutable tag
```

```bash
gh issue create --repo Netcracker/qubership-core-infra \
  --title "Callers that pin generic-go-build.yaml by SHA still run docker-build.yaml from a mutable tag" \
  --body-file draft.md
```

Labels are yours to choose. Your recent issues there carry `bug` and `26.4_scope`; this reads as a hardening request, not a bug.

## Decisions for you

1. **Issue or comment on #321?** PR #321 (Renovate, open since 2026-07-27, 0 reviews) already makes the one-line change. If it merges and a release follows, the request is met. A comment there asking for the release may serve better than a new issue. I drafted the issue because the tag-pinned callers and the Maven workflow are not what #321's title says.
2. **Is it public?** I treated it as a hardening request: the tag resolves to the pinned commit today, and no exploit or observed abuse is involved. The report states the condition ("moving the tag") without a claim that anyone can do it. If you consider it a vulnerability, it must not go to the public tracker. Private vulnerability reporting is off on core-infra, and the org `SECURITY.md` names `opensourcegroup@netcracker.com`.
3. **AI policy.** I found none in the repo or at org level (`Netcracker/.github`). The draft has no disclosure sentence. Add one if you want it, and confirm you can defend the report without me.
4. **Voice.** The draft speaks as you ("I call...", "I did not check..."), and the observations are from this session on 2026-09-23. Check that you are fine presenting them that way.

## Lookups not made, and what is unchecked

- **Form.** core-infra has no `.github/ISSUE_TEMPLATE`. The org `bug_report.yml` fields are known, but I did not read the org `feature_request.yml`. I used the structure of your recent issues there (`## Goal`, `## Context`, `## Scope`, `## Definition of done`). If you file through the web form for requests, move the text into its fields.
- **Re-run before filing.** The `main` SHA was read at 10:00 UTC on 2026-09-23, and #321 was last updated 2026-09-16. Re-run the `git ls-remote` command and recheck #321, since `main` or the PR may have moved.
- **Callers.** How the 16 repositories from #367 pin `generic-go-build.yaml` was not checked. The report says so. To close it: search GitHub for `generic-go-build.yaml@` in those repositories.
- **Why line 392 is a tag.** I did not read the full file for a comment explaining it, so I could not say there is none. The report only says no project document states a rule. Check the file and the history of #368 and #401 for a reason.
- **The Maven line.** `generic-maven-build.yaml` line 222 on `main` is from my notes; the command was not recorded. Re-run: `curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/main/.github/workflows/generic-maven-build.yaml | grep -n 'docker-build.yaml@'`.
- **Rulesets and releases.** The `[]` and 404 results are from unauthenticated API reads, as far as my notes show. If you can read repository settings, confirm there is no tag protection.
- **Support window.** No `SUPPORT.md` or release schedule was read. The report only says `v2.6.1` is the newest tag and has the same pattern.

## Left out of the issue on purpose

- The Russian DEP-01 finding and its wording, per your rule against policy content.
- The org workflow conventions from `qubership-ai-packages` (`.agents/skills/qubership-workflow-conventions/SKILL.md`). It reads as internal policy, and it covers actions, not reusable workflows. GitHub's docs ground the request instead.
- Both fixes from the finding. Asking core-infra to pin is the issue itself. Calling `docker-build.yaml` directly by SHA from `go-build.yml` is a caller-side change in qubership-ratelimit. Its workaround form, `skip-docker: true` plus a direct call, was not tried, so it stays out of the report. To try it, run it on a branch and compare `referenced_workflows`.
- A `./` reference inside the nested workflow. GitHub's docs say a `./` call resolves to the caller's commit, but they do not say how it behaves in a nested called workflow. Untested.
- A lower-layer finding with a different owner: qubership-workflow-hub `docker-action/action.yml` at `6b356d2` uses `actions/upload-artifact@v4` (tag) at line 485. It belongs in a report to that repository if you want one.
- Line 8 of `generic-go-build.yaml` shows callers using `@v2.x.x` tags in its usage comment. It is true, but it answers no reader's question here.
