# Hand-over note: core-infra issue on the tag-pinned `docker-build.yaml` call

Nothing has been filed. The issue body is in `draft.md`, next to this note.

## Suggested title and command

Title: `generic-go-build.yaml pinned by SHA still calls docker-build.yaml by a mutable tag`

```bash
gh issue create --repo Netcracker/qubership-core-infra \
  --title 'generic-go-build.yaml pinned by SHA still calls docker-build.yaml by a mutable tag' \
  --body-file draft.md
```

Add labels yourself. This is a hardening request and not a failing build, so `bug` may not fit. Your recent issues carry `26.4_scope`, so decide whether this one should too.

## Decisions that are yours

1. **A new issue, a comment on #321, or both.** Renovate PR #321 already makes the change on `main`. A comment there asking for review would cover the `main` part. The issue adds the request for a release and the question of releases already published. If you choose a comment only, the Context section of the draft (from the run evidence onward) is the material for it.
2. **Public or private route.** The draft describes a hardening gap with no observed misuse: the tag still pointed at the pinned commit on 2026-09-23, and moving it requires write access to core-infra. The reference is already public in the workflow files and in #321. If you treat it as a vulnerability anyway, the org `SECURITY.md` names `opensourcegroup@netcracker.com`. Private vulnerability reporting is off on core-infra. Do not file it publicly in that case.
3. **Form.** The draft uses the structure of your recent issues in this tracker (Goal, Context, Scope, Definition of done). The org-level `feature_request.yml` in `Netcracker/.github` applies to core-infra, but its fields were not recorded in this session. `gh issue create` does not enforce form fields. If you want the form, open `https://github.com/Netcracker/.github/blob/main/.github/ISSUE_TEMPLATE/feature_request.yml` and map the sections to its labels.
4. **AI disclosure.** No AI policy was found in core-infra or in the org `.github` repository, so nothing is required. Whether to mention that the draft was written with a tool is your call. Make sure you can explain the evidence yourself if a maintainer asks.
5. **Org pinning convention.** `Netcracker/qubership-ai-packages`, `.agents/skills/qubership-workflow-conventions/SKILL.md` lines 93 and 107, requires a full SHA for every action and forbids bare tags. It talks about actions, not reusable workflows. I left it out because of your rule against policy content in tickets. If you consider it fine to cite, it is the strongest grounding available after the repository's own Renovate PR.

## Gaps to close before filing

All observations are from 2026-09-23. It is now 2026-10-31, so re-check these first:

- Whether #321 has been merged or closed, and whether a new release contains the pin:
  `gh pr view 321 --repo Netcracker/qubership-core-infra --json state,mergedAt,reviews`
  `gh release list --repo Netcracker/qubership-core-infra; git ls-remote --tags https://github.com/Netcracker/qubership-core-infra`
- Whether `main` still has the tag reference:
  `curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/main/.github/workflows/generic-go-build.yaml | grep -n 'docker-build.yaml@'`
- Whether `v2.5.2` still peels to `71206242f5967ac6691337913593f8623863f711`:
  `git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}'`
- The `rulesets`, `releases`, and tag protection lookups were made through the API. It is not recorded whether the calls were authenticated. A maintainer can confirm under Settings > Rules. To re-run:
  `gh api repos/Netcracker/qubership-core-infra/rulesets`

Not established, and not claimed in the draft:

- How the 16 repositories named in #367 pin `generic-go-build.yaml`. This would show how many callers are on a tag-resolved `docker-build.yaml` today:
  `gh search code 'generic-go-build.yaml@' --owner Netcracker`
- The workaround of setting `skip-docker: true` and calling `docker-build.yaml@<sha>` directly from `go-build.yml` was not tried. If qubership-ratelimit needs the pin before core-infra acts, try it in a branch and add the run to the issue or to a ratelimit issue.
- How a `./` reference resolves inside a workflow that another repository calls. GitHub's docs do not say. The draft marks it as an untested shape.
- The tag ruleset shape in Scope was not tested either. It is marked that way in the draft.

## Tracker search

Queries run on Netcracker/qubership-core-infra issues and PRs, all states: `docker-build.yaml in:title,body`, `pin SHA in:title`, `unpinned`, `docker-build.yaml@`, `pinned by SHA`, `mutable tag`. The nearest hit is #321, which the draft names. The other hits are #371 and #367, which concern the same job but different problems, #401, which is merged and pins the Go compiler, and #196, #216, #102, and #33, which are unrelated.

## Separate finding, other owner

One level lower, `qubership-workflow-hub` `actions/docker-action/action.yml` at `6b356d28e46b2d4683cccb1d91f92643d7f0c513`, line 485, uses `actions/upload-artifact@v4` by tag. That belongs to qubership-workflow-hub and needs its own report there if you want it raised. It was not pursued.
