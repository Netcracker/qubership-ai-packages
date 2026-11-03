# Hand-over note: core-infra issue on the tag-pinned `docker-build.yaml` call

Nothing has been filed. The issue body is `draft.md`. Its first line is the title, so remove that line from the body
before filing.

## Decide before filing

1. **Issue or a review on #321.** Renovate PR #321 already makes the change for `generic-go-build.yaml` and
   `generic-maven-build.yaml`, pinning both to the `v2.6.1` commit `8a233b0`. It has been open since 2026-07-27 with no
   review. I recommend a new issue linked to #321. The PR carries no problem statement, and it does not address the
   release constraint: each release refers to its own tag, and a commit cannot contain its own SHA. A review comment on
   #321 asking a maintainer to merge it is the lighter option. Which one to use is your call.
2. **Public issue or private report.** I drafted this as a public hardening request. Nothing observed has gone wrong:
   on 2026-09-23 `v2.5.2` still peeled to the pinned commit. Moving the tag needs write access to core-infra, and the
   same pattern is already public in #321. If you treat it as a vulnerability instead, do not file it publicly.
   Private vulnerability reporting is off on core-infra, and the org `SECURITY.md` names `opensourcegroup@netcracker.com`.
3. **Labels.** Your bug issues here carry `bug` and `26.4_scope`. This issue is a hardening request with no failure, so
   choose whether `bug` fits.
4. **AI disclosure.** I found no AI policy in core-infra or in the org `.github` repository, so nothing requires
   disclosure. Whether to mention it anyway is your choice.

## Re-run before filing (the data is from 2026-09-23)

```bash
git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' refs/heads/main 'refs/tags/v2.*'
for ref in main <newest-tag>; do printf '%s: ' "$ref"; curl -s "https://raw.githubusercontent.com/Netcracker/qubership-core-infra/$ref/.github/workflows/generic-go-build.yaml" | grep -n 'docker-build.yaml@'; done
curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/main/.github/workflows/generic-maven-build.yaml | grep -n 'docker-build.yaml@'
gh pr view 321 --repo Netcracker/qubership-core-infra --json state,reviews,mergedAt
gh api repos/Netcracker/qubership-core-infra/rulesets
```

If #321 has merged or a newer tag has come out, update the "latest tag", `main`, and #321 sentences in the body. If
`v2.5.2` no longer peels to `71206242`, the issue gains an observed effect. Re-run the `referenced_workflows` command on
a new caller run before you add that.

## Format

- core-infra has no issue templates of its own. The org repository `Netcracker/.github` has `bug_report.yml` and
  `feature_request.yml`. I did not record the field labels of `feature_request.yml`. The bug form asks for "To
  Reproduce", and nothing here fails, so I used the `Goal`, `Context`, `Scope`, and `Definition of done` structure of
  your recent issues in this tracker. If you file through the web form, map the sections onto its fields. `gh issue
  create` does not enforce the form fields.
- Filing command, once the title line is removed from the body:

  ```bash
  gh issue create --repo Netcracker/qubership-core-infra \
    --title '`generic-go-build.yaml` calls `docker-build.yaml` by tag, so a caller'"'"'s SHA pin does not cover the image build' \
    --body-file draft.md --label <labels>
  ```

## Not established, and left out of the issue

- **Who else is affected.** #367 says the generic Go build "is used by 16 observability repositories". I did not
  check how those repositories pin it. Only callers that pin by SHA lose anything here, so I left the count out.
- **The `./` reference.** I did not test how a `./.github/workflows/docker-build.yaml` reference resolves inside a
  workflow that another repository calls. The issue marks it as untested.
- **A stated reason for the tag.** My notes on lines 388–395 of `generic-go-build.yaml` at `71206242` show no comment
  that explains the tag reference. Open the file and confirm this before relying on the "every other `uses:` pins a
  full SHA" sentence.
- **Rulesets.** I made the `rulesets` call without checking whether an unauthenticated call shows org-level tag
  rulesets. Re-run it with `gh api` before filing.
- **The caller-side alternative from DEP-01.** Setting `skip-docker: true` and calling `docker-build.yaml@<sha>`
  directly from `go-build.yml` was not tried. That change belongs to qubership-ratelimit, not to this issue.

## Left out on purpose

- The org workflow conventions in `Netcracker/qubership-ai-packages`
  (`.agents/skills/qubership-workflow-conventions/SKILL.md`, lines 93 and 107) require full-SHA pins. They cover
  actions and say nothing about reusable workflows, and your rule excludes policy content from tickets. Add a link if you
  consider that file public guidance rather than policy.
- One level down, `docker-action/action.yml` in qubership-workflow-hub at `6b356d2` uses
  `actions/upload-artifact@v4` by tag at line 485. qubership-workflow-hub has a different owner, so this needs a
  separate issue there if you want one. I did not investigate it further.

## Searches run (core-infra issues and PRs, all states)

`docker-build.yaml in:title,body`, `pin SHA in:title`, `unpinned`, `docker-build.yaml@`, `pinned by SHA`,
`mutable tag`. Nearest hit: #321. Related to the same job, but a different problem: #371 (forwarding the qemu and
buildx toggles), #367 (fork-safe generic Go build), and #401 (Go compiler pin, merged).
