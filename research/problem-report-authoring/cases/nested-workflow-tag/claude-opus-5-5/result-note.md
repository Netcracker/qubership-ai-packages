# Hand-over note: nested docker-build.yaml tag in qubership-core-infra

Not part of the issue body. Nothing was filed, and nothing was fetched while drafting: every fact in the body comes from the session notes of 2026-09-23.

## Proposed title and filing command

Title: `generic-go-build.yaml calls docker-build.yaml by tag, so SHA-pinned callers still build and push images from a mutable ref`

```bash
gh issue create --repo Netcracker/qubership-core-infra \
  --title 'generic-go-build.yaml calls docker-build.yaml by tag, so SHA-pinned callers still build and push images from a mutable ref' \
  --label bug \
  --body-file research/problem-report-authoring/cases/nested-workflow-tag/claude-opus-5-5/result.md
```

- Title prefix: the org bug form (`Netcracker/.github`, `bug_report.yml`) sets `[Bug]: `, but your recent issues in this tracker carry no prefix. I left it off; add it if you prefer the form's default.
- Labels: your bug issues there also carry `26.4_scope`. Add it with a second `--label` if this belongs to that scope.

## Decisions for you before filing

1. **Issue, or a comment on PR #321.** #321 (Renovate, open since 2026-07-27, no reviews) already makes the change of expected behavior 1 on `main`. If all you want is 1, a comment on #321 with the run evidence (steps 4 and 5 of the body) and a request to merge and release may be enough. The issue is worth filing for what #321 lacks: the reason, and expected behavior 2 (the tags already referenced by released commits).
2. **Public issue or private report.** I judged this a hardening gap, not a vulnerability: using it needs write access to core-infra's tags, nothing shows the tag has been moved, and the same reference is already public in #321. If you read it otherwise, do not file publicly: the org `SECURITY.md` names `opensourcegroup@netcracker.com`, and core-infra has private vulnerability reporting turned off.
3. **The org workflow conventions.** `Netcracker/qubership-ai-packages`, `.agents/skills/qubership-workflow-conventions/SKILL.md` lines 93 and 107, requires a full SHA and forbids bare tags. It is written for actions and says nothing about reusable workflows. I left it out because of your rule against production policy content in tickets; it would be the strongest in-org grounding if you decide it is fine to cite.
4. **Form.** I used the org bug form's fields (Describe the bug, To Reproduce, Version, Logs, Additional information) as headings, because `gh issue create` does not apply the form. Expected behavior sits under Describe the bug, since the form has no field for it. Your own issues in this tracker use Goal, Context, Scope, and Definition of done; if you would rather match those, the expected-behavior list maps to Definition of done.
5. **AI disclosure.** No AI policy was found in core-infra or in the org `.github` repository, so the body carries none. Whether to mention the tool is your call.

## Gaps and the commands that close them

- Whether the org has tag rulesets the session's `GET .../rulesets` call did not show (the notes do not say whether it ran with admin rights). An org or repo admin can check the repository's Settings, Rules, Rulesets, or run:

  ```bash
  gh api repos/Netcracker/qubership-core-infra/rulesets --jq '.[] | {name, target, enforcement}'
  gh api orgs/Netcracker/rulesets --jq '.[] | {name, target, enforcement}'
  ```

  If a tag ruleset exists, drop expected behavior 2 or rewrite it.
- The legacy `tags/protection` 404 is not evidence either way (GitHub retired that endpoint), so the body does not cite it.
- How the 16 repositories named in #367 pin `generic-go-build.yaml` was not checked. The body does not need it, since the tag reference reaches every caller, but it would show how many callers expected behavior 2 protects:

  ```bash
  gh search code 'qubership-core-infra/.github/workflows/generic-go-build.yaml@' --owner Netcracker --json repository,path,textMatches
  ```

- The caller-side workaround (`skip-docker: true` plus a direct `docker-build.yaml@<sha>` call in `go-build.yml`) was not tried; the body says so.
- Whether a same-repository `./.github/workflows/docker-build.yaml` reference inside a nested called workflow resolves to the called workflow's commit was not tested; the body says so.
- Re-run the tracker search just before filing, in case something landed after 2026-09-23:

  ```bash
  gh search issues --repo Netcracker/qubership-core-infra 'docker-build.yaml' --include-prs --state all
  gh pr view 321 --repo Netcracker/qubership-core-infra --json state,reviews,mergedAt
  ```

## Left out on purpose

- `qubership-workflow-hub` `actions/docker-action/action.yml` at `6b356d2` calls `actions/upload-artifact@v4` by tag at line 485. Different owner, so it would be a separate issue in Netcracker/qubership-workflow-hub.
- The usage comment at line 8 of `generic-go-build.yaml` tells callers to reference `@v2.x.x`, a tag. Related, but a separate change; not in this issue.
- The Russian original of review finding DEP-01 is not quoted; the body restates only what the session verified.
