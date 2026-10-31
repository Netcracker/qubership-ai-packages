# Hand-over note for the person filing

Draft: `draft.md`. The first line (`Title: ...`) is the issue title; the rest is the body. Nothing has been filed.

Filing command, once the title line is removed from a copy of the body and the checks below are done:

```bash
gh issue create --repo Netcracker/qubership-core-infra \
  --title "generic-go-build.yaml calls docker-build.yaml by tag, so a caller's SHA pin does not fix the publish logic" \
  --body-file <body-without-title-line>.md
```

## Decide before filing

1. **New issue or a comment on PR #321?** #321 (open Renovate PR) already pins the same line on `main`. A comment there may serve better, but it would not carry the point that existing tags and callers stay on the tag reference. Your call.
2. **Public hardening issue or a security report?** I wrote it as a hardening request: the tag has not moved, and the report claims no exploit and no impact beyond what the run shows. If you regard it as a vulnerability, the org `SECURITY.md` points to `opensourcegroup@netcracker.com`, and private vulnerability reporting is off on core-infra. Then it should not go to the public tracker.
3. **Can you explain and defend the report without me?** I found no AI policy in the repo or the org, so the draft has no disclosure line.

## Stale: re-check first

Every observation is from 2026-09-23, five weeks before today (2026-10-31). Re-run these, and edit the draft if an answer changed:

- `git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' refs/heads/main` (does `v2.5.2` still resolve to `71206242…`; `main` was `f7fba11`).
- Whether PR #321 is still open, unreviewed, and unmerged, and whether a release newer than `v2.6.1` exists.
- Whether qubership-ratelimit `go-build.yml` still pins `v2.5.2`.
- `rulesets` and `releases/tags/v2.5.2` on core-infra.

## Not established, so not claimed in the draft

- Support window of core-infra releases (no `SUPPORT.md` or release policy read). The draft gives the tag and commit, and shows the same reference in the newest release.
- Whether a comment near line 392 explains the tag. I only grepped `uses:`. A release cannot contain its own commit SHA, so the maintainers may have a reason; read the lines around 392 before filing.
- `generic-maven-build.yaml`: seen only on `main`, not at `v2.5.2`.
- Legacy `tags/protection` returned 404, which is likely a permission limit on an unauthenticated call. I left it out. Whether the other API calls were authenticated is not recorded in my notes.
- How the 16 repositories from #367 pin `generic-go-build.yaml`. The draft says only that they take the reference from the workflow.
- Workarounds were not tried: `skip-docker: true` with a direct `docker-build.yaml@<sha>` call from `go-build.yml`, and the finding's idea of a same-repo `./` call inside `generic-go-build.yaml`. For `./`, GitHub's docs do not say how a nested call resolves, so it is untested.

## Left out on purpose

- The review finding DEP-01 and the exact wording of its suggestions.
- The org workflow conventions ("Pin every action ... full SHA", from qubership-ai-packages): your rule says no policy content. They cover actions, not reusable workflows.
- Below this report, in qubership-workflow-hub: `docker-action/action.yml` at `6b356d2`, line 485, uses `actions/upload-artifact@v4` by tag. Different owner; a separate issue there if you want one.

## Form and routing

- core-infra has no `.github/ISSUE_TEMPLATE`. The org `Netcracker/.github` has `bug_report.yml` (Describe the bug, To Reproduce, Version, Logs, Additional information; prefix `[Bug]: `) and `feature_request.yml`, whose fields I did not read. I used your usual `Goal`, `Context`, `Scope`, `Definition of done` headings and no `[Bug]:` prefix. If the web form pre-fills a template, paste the sections into the matching fields.
- Labels (`bug`, `26.4_scope`) are yours to set.

## Searches run on core-infra (issues and PRs, all states)

`docker-build.yaml in:title,body`, `pin SHA in:title`, `unpinned`, `docker-build.yaml@`, `pinned by SHA`, `mutable tag`. Nearest hit #321; also seen: #371, #367, #401 (not the same problem). #258 is the Dependency Dashboard that lists #321.
