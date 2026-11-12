# Hand-over note: issue for Netcracker/qubership-core-infra

The issue body is in `draft.md`. Nothing has been filed.

## Filing command

```bash
gh issue create --repo Netcracker/qubership-core-infra \
  --title "Pinning generic-go-build.yaml by commit SHA leaves its docker-build.yaml call on a mutable tag" \
  --body-file draft.md
```

I left out the `[Bug]:` prefix to match your recent issues in this tracker. Labels are your call (`bug`, `26.4_scope`). Nothing is broken today, so this reads as hardening rather than a bug.

## Decisions for you

1. **PR #321 already makes this change.** Renovate opened it on 2026-07-27 and it had no reviews as of 2026-09-23. Instead of a new issue, you could comment on #321 or ask the core-infra maintainers to review and release it. The issue links to #321 and adds what the PR lacks: why the pin matters to callers that pin by SHA, the run evidence, and the ask for a release.
2. **Security route.** I treated this as hardening and not as a vulnerability. The tag reference is visible in the public workflow file and in #321, moving the tag needs write access to core-infra, and nothing different runs today. If you disagree, don't file it publicly. Private vulnerability reporting is off on core-infra, and the org `SECURITY.md` names `opensourcegroup@netcracker.com`.
3. **Format.** I used the structure of your recent issues in this tracker (Goal, Context, Scope, Definition of done). Core-infra has no template of its own, so the web UI offers the org `bug_report.yml`, with required fields "Describe the bug" and "To Reproduce", optional "Version", "Logs", and "Additional information", and the title prefix `[Bug]: `. If you file through that form, map the sections: Goal and Context go into "Describe the bug", the commands go into "To Reproduce", and `v2.5.2` (`71206242`), `v2.6.1` (`8a233b03`), and `main` (`f7fba11`) go into "Version".
4. **AI disclosure.** I found no AI policy for the repository or the org, so no disclosure is required. Whether to mention it anyway is up to you.

## Re-check before filing (the observations are from 2026-09-23)

- Whether #321 is still open, and whether a release after `v2.6.1` exists: `gh pr view 321 --repo Netcracker/qubership-core-infra`, `git ls-remote --tags https://github.com/Netcracker/qubership-core-infra`.
- Whether `main` still has the tag reference: the `for ref in v2.6.1 main` loop in the issue.
- Whether `v2.5.2` still peels to `71206242…`: the `git ls-remote` command in the issue. If it no longer does, the issue needs rewriting, because that is an observed move.
- Duplicates since then. The queries I ran on issues and PRs in all states were `docker-build.yaml in:title,body`, `pin SHA in:title`, `unpinned`, `docker-build.yaml@`, `pinned by SHA`, and `mutable tag`. Hits: #321 (the nearest), #371 and #367 (different problems in the same job), #401 (Go compiler pin, merged), and #196, #216, #102, and #33 (unrelated).

## Not established

- Whether a comment just above line 392 of `generic-go-build.yaml` at `71206242` gives a reason for the tag reference. I read lines 388–395, not 386–387. Check: `curl -s https://raw.githubusercontent.com/Netcracker/qubership-core-infra/71206242f5967ac6691337913593f8623863f711/.github/workflows/generic-go-build.yaml | sed -n '380,396p'`.
- How the 16 repositories from #367 pin `generic-go-build.yaml`. The issue does not depend on this, because every caller of the checked releases gets the tag-resolved inner call.
- Releases `v2.5.1` and earlier were not checked for the same pattern.
- The rulesets result came from `GET /repos/.../rulesets` only. If you have admin access, the repository settings show tag rules directly.
- The caller-side workaround from the review finding (`skip-docker: true` plus a direct `docker-build.yaml@<sha>` job in `go-build.yml`) was not tried. It belongs in qubership-ratelimit and not in this issue.
- Whether a `./.github/workflows/docker-build.yaml` reference resolves to the callee's commit when the caller is in another repository. The issue marks this as untried.

## Left out of the issue on purpose

- The DEP-01 review finding. It is in Russian and in a review readers can't open.
- The org workflow conventions (`Netcracker/qubership-ai-packages`, `.agents/skills/qubership-workflow-conventions/SKILL.md`, lines 93 and 107: full SHA for every action, bare tags forbidden). They are written for actions and say nothing about reusable workflows, and they may count as policy content under your rule for ticket texts. If you want them, one sentence in Context with that limit stated is enough.
- `actions/upload-artifact@v4` in qubership-workflow-hub `docker-action/action.yml` line 485. The issue names it only as out of scope. A separate issue in qubership-workflow-hub is your call.
