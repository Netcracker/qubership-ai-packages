# Hand-over note: nested workflow tag issue for Netcracker/qubership-core-infra

## Filing

Title: `generic-go-build.yaml` calls `docker-build.yaml` by tag, so a caller's SHA pin does not fix the image push

```bash
gh issue create --repo Netcracker/qubership-core-infra \
  --title 'generic-go-build.yaml calls docker-build.yaml by tag, so a caller'"'"'s SHA pin does not fix the image push' \
  --body-file result.md
```

Labels are yours to pick. Your recent bug issues here carry `bug` and `26.4_scope`; this one is a hardening request, since nothing different runs today, so `bug` may not fit.

## Decisions for you (not answered in the body)

1. **Comment on #321 instead of a new issue?** Renovate's PR #321 already makes the change on `main` (both lines, plus `maven-deploy.yml` and `maven-verify.yml`). It has had no review since 2026-07-27. A comment there asking for review and a release, with the run evidence, may get the same result with less noise. The body is written as a standalone issue that names #321 as the nearest hit.
2. **Public tracker or private route.** I judged this a hardening gap, not a vulnerability: nothing is exploitable without write access to core-infra, the tag resolves to the pinned commit today, and #321 already discusses the pin in public. If you see it differently, the org SECURITY.md names `opensourcegroup@netcracker.com`; private vulnerability reporting is off on core-infra. Do not file publicly in that case.
3. **Org workflow conventions.** `Netcracker/qubership-ai-packages` `.agents/skills/qubership-workflow-conventions/SKILL.md` (lines 93 and 107) requires full-SHA pins and forbids bare tags, but it is written for actions and says nothing about reusable workflows. I left it out because of your rule against policy content in tickets. If it is not policy content to you, one sentence citing it would be a stronger grounding than the GitHub docs.
4. **Form.** core-infra has no issue templates. The org `bug_report.yml` has fields Describe the bug (required), To Reproduce (required), Version, Logs, Additional information, with the `[Bug]: ` prefix. I used the Goal / Context / Scope / Definition of done structure of your recent issues here instead, because this is a request, not a failure. The fields of the org `feature_request.yml` were not recorded; read them if you want to use that form.

## Gaps and the checks that close them

- **Comment above line 392.** The grep showed only the `uses:` line. Check that no comment near it explains the tag reference; the body assumes none:
  `curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/71206242f5967ac6691337913593f8623863f711/.github/workflows/generic-go-build.yaml | sed -n '380,396p'`
- **The rulesets API returned `[]` without authentication.** If that endpoint hides rulesets from anonymous callers, the "plain tag" sentence is wrong. Re-check with `gh api repos/Netcracker/qubership-core-infra/rulesets` as an authenticated user, and look at repository settings if you have access.
- **How the 16 repositories from #367 pin `generic-go-build.yaml`.** Not checked. The body's claim about them does not depend on it (the nested call is by tag either way), but it would tell you how many callers have a SHA pin that this defeats:
  `gh search code 'generic-go-build.yaml@' --owner Netcracker`
- **Older releases.** Only v2.5.2, v2.6.0, v2.6.1, and `main` were read. Earlier tags were not.
- **The `./` reference shape** is untested and marked so. Whether a `./.github/workflows/...` reference inside a workflow called from another repository resolves to core-infra at the called commit is not established from the docs.
- **Workaround not tried and not in the body:** `skip-docker: true` on `generic-go-build.yaml` plus a direct call to `docker-build.yaml@<sha>` from qubership-ratelimit's `go-build.yml`. If it works, it is the fix on the qubership-ratelimit side regardless of this issue.

## Out of this issue

- `netcracker/qubership-workflow-hub` `actions/docker-action/action.yml` at `6b356d2`, line 485, uses `actions/upload-artifact@v4` by tag. Different owner; it needs its own report in qubership-workflow-hub if you want it fixed.
- No AI policy was found in core-infra or the org `.github` repository, so the body carries no disclosure.
- Names in the body are all public (public repositories, public run), so nothing was renamed or redacted.
