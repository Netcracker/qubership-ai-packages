# Hand-over note: core-infra issue on the tag-pinned `docker-build.yaml` call

Nothing has been filed. The issue body is in `draft.md`, next to this note.

## Title and command

Title (no `[Bug]: ` prefix, which matches your earlier issues in this tracker; nothing here fails, so this is a change request):

> Callers that pin generic-go-build.yaml by SHA still run docker-build.yaml from a mutable tag

```bash
gh issue create --repo Netcracker/qubership-core-infra \
  --title "Callers that pin generic-go-build.yaml by SHA still run docker-build.yaml from a mutable tag" \
  --body-file draft.md
```

Add labels yourself. Your bug issues here carry `bug` and `26.4_scope`; whether either fits a change request is your call.

## Decisions for you before filing

1. **New issue, or a comment on #321?** Renovate's PR #321 already makes the `main` part of this change (it has been open since 2026-07-27, with 0 reviews and only the SonarCloud comment). The issue adds two things: the reason for the change and the request for a release that carries it. A comment on #321 with the same evidence may get it merged faster. If you comment there, cut the "Scope" and "Definition of done" sections down to the release ask.
2. **Public or private?** I treated this as a hardening gap and not as a suspected vulnerability. Nothing was exploited, the tag points at the pinned commit, moving it needs write access to core-infra, and the pattern is already public in the workflow file and in #321. If you consider it a vulnerability, it does not go to the public tracker. Private vulnerability reporting is off on core-infra, so the route is the org SECURITY.md address, `opensourcegroup@netcracker.com`.
3. **AI policy.** Neither core-infra nor the org `.github` repo has an AI policy, so the issue carries no disclosure. Whether to mention that a tool drafted it is up to you. If a maintainer asks follow-up questions, you are the one who answers them.
4. **"We need" in the Goal.** The issue speaks for the qubership-ratelimit team. It also says that a pinned `docker-build.yaml` lagging one release behind is acceptable ("what we need is that the call resolves to a fixed commit"). Confirm that this is true for the team.

## Re-check before filing (the evidence is from 2026-09-23, five weeks old)

```bash
# Tag still on the pinned commit, and current main
git ls-remote https://github.com/Netcracker/qubership-core-infra 'refs/tags/v2.5.2^{}' refs/heads/main
# Newest tags: was a release cut after v2.6.1?
git ls-remote --tags https://github.com/Netcracker/qubership-core-infra | tail -n 5
# Still tag-pinned on main?
curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/main/.github/workflows/generic-go-build.yaml | grep -n 'docker-build.yaml@'
# #321 still open?
gh pr view 321 --repo Netcracker/qubership-core-infra --json state,reviews,mergedAt
```

If #321 has been merged and a tag cut since then, the issue becomes a request to callers to bump, not to core-infra. In that case don't file it.

## Gaps not closed in the session

- **Duplicate search.** The queries were `docker-build.yaml in:title,body`, `pin SHA in:title`, `unpinned`, `docker-build.yaml@`, `pinned by SHA`, and `mutable tag` (issues and PRs, all states). The nearest hit is #321, which the issue names. The other hits were different problems in the same job: #371 (QEMU/Buildx toggles), #367 (fork safety), and #401 (Go compiler pin, merged). Re-run the queries before filing.
- **Issue form.** The org `Netcracker/.github` has `bug_report.yml` (Describe the bug, To Reproduce, Version, Logs, Additional information) and `feature_request.yml`. I didn't read the fields of `feature_request.yml`. The draft uses your Goal / Context / Scope / Definition of done structure from this tracker. `gh issue create` does not apply the form. If you file through the web UI with the feature form, put Goal in its problem or motivation field and the rest in the matching fields.
- **Lines around 392.** I didn't read the lines next to line 392 for a comment that explains why the tag is used. Check with `curl -s <raw URL at 71206242> | sed -n '385,396p'`. If a comment gives a reason, the issue has to answer it.
- **How the 16 repositories from #367 pin `generic-go-build.yaml`.** Not checked. The issue only quotes #367's count. A code search for `generic-go-build.yaml@` in the Netcracker org would close this.
- **Untried workaround.** Setting `skip-docker: true` and calling `docker-build.yaml@<sha>` directly from `go-build.yml` was not tried, so it is not in the issue. If you want it as a stopgap for qubership-ratelimit, try it in a PR there first.
- **`./` local reference as an alternative shape.** GitHub's docs say a `./` reference without `@ref` runs the workflow from the caller's commit. They don't say how it resolves inside a nested workflow that another repository calls, so it is left out of the issue. To close this, test it in a fork before proposing it.

## Left out on purpose

- **The org workflow conventions** (`Netcracker/qubership-ai-packages`, `qubership-workflow-conventions/SKILL.md`, lines 93 and 107: full SHAs only, bare tags forbidden). They support the issue, but they are written for actions and not for reusable workflows. You may also count them as policy content, which your rule keeps out of tickets. Add a link if you want the extra grounding.
- **The tag in `qubership-workflow-hub`.** `docker-action/action.yml` at `6b356d2`, line 485, uses `actions/upload-artifact@v4` by tag. That repository has a different owner, so this needs its own issue there; this issue doesn't depend on it.
- **The original DEP-01 finding text (in Russian) and its "call `docker-build.yaml` directly from `go-build.yml`" fix.** That is a change in qubership-ratelimit, not in core-infra.
