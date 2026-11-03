# Hand-over note (not part of the issue)

Nothing was filed. The first line of `draft.md` is the proposed title; the body starts at `## Goal`.

```bash
gh issue create -R Netcracker/qubership-core-infra \
  --title "Pinning generic-go-build.yaml by SHA leaves the docker-build job's workflow resolved by tag" \
  --body-file <body-only file, i.e. draft.md without its first two lines>
```

## Check before filing: every observation is from 2026-09-23

Today is 2026-10-31. A new release, a merge of #321, or a moved tag would change the body. Re-run:

```bash
git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' 'refs/tags/v*' refs/heads/main
for ref in main; do curl -s "https://raw.githubusercontent.com/Netcracker/qubership-core-infra/$ref/.github/workflows/generic-go-build.yaml" | grep -n 'docker-build.yaml@'; done
gh pr view 321 -R Netcracker/qubership-core-infra --json state,mergedAt,title
gh api repos/Netcracker/qubership-core-infra/rulesets
```

If #321 merged, or main no longer uses a tag, the report changes (see the next section).

## Decisions for you

- **Public or private.** I wrote it as a public hardening request: the tag still resolves to the pinned commit, and the body states no exploit and no speculative impact. Private vulnerability reporting is off on core-infra. The org `SECURITY.md` names `opensourcegroup@netcracker.com`. If you read the DEP-01 finding as a vulnerability, send it there instead.
- **New issue or a comment on PR #321.** #321 is the nearest hit and touches the same lines. The new part is that existing releases cannot be fixed that way and a file cannot name its own commit. I wrote a new issue because the problem is wider than the Renovate change. A comment on #321 may serve better.
- **Defending the text.** I found no AI policy in the repository or the org (`CONTRIBUTING.md` covers only the CLA and the Code of Conduct), so no disclosure is in the body. You need to be able to explain and answer for it yourself.
- **Labels and format.** core-infra has no issue template. The org `bug_report.yml` (`[Bug]: ` prefix, `bug` label) is for defects, and this is a change request, so I used the Goal / Context / Scope / Definition of done layout of your recent issues here, with no prefix. Label choice (`bug`, `26.4_scope`) is yours.
- **Separate report for workflow-hub.** `docker-action/action.yml` at `6b356d2` line 485 uses `actions/upload-artifact@v4` by tag. Different owner, so it would be its own issue in qubership-workflow-hub. The body only excludes it from scope.

## Not established (the body says so only where a claim rests on it)

- Search queries run in core-infra (issues and PRs, all states): `docker-build.yaml in:title,body`, `pin SHA in:title`, `unpinned`, `docker-build.yaml@`, `pinned by SHA`, `mutable tag`. Only #321 is cited. #371, #367, #368 and #401 concern the same job or workflow and are not duplicates; #367 is cited for the 16 repositories.
- How the 16 repositories from #367 pin `generic-go-build.yaml`.
- The `./.github/workflows/docker-build.yaml` shape. GitHub's page does not address nested calls, and I did not run it. A test caller workflow would settle it.
- Whether `v2.5.2` is still inside a support window. core-infra has no published one that I found; the body therefore also shows the pattern on `v2.6.1` and `main`.
- Whether a comment or a document in core-infra explains the tag reference. I only read the `uses:` lines.

## Left out of the body on purpose

- The caller-side workaround (`skip-docker: true` plus a direct `docker-build.yaml@<sha>` call from `go-build.yml`). It was never tried, and the report does not depend on it. Try it in qubership-ratelimit if you want an interim fix.
- The Netcracker workflow conventions file in qubership-ai-packages. Your rule is no production policy content, and the GitHub documentation grounds the request on its own.
- The DEP-01 identifier and the review's wording, the `SONAR_TOKEN` secret, and the wiki-style links.
- The tag object `504063c`, the other tags, and the full push log (one line is kept as evidence).
