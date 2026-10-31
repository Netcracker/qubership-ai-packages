# Hand-over note: core-infra pinning issue

Nothing was filed or sent. The body is in `draft.md`. The title is not part of it.

Suggested title (names the task, not the fix):
`Cannot pin the image build logic behind generic-go-build.yaml to a commit`

Filing command, after you have read the body and handled the points below:

```bash
gh issue create --repo Netcracker/qubership-core-infra \
  --title "Cannot pin the image build logic behind generic-go-build.yaml to a commit" \
  --body-file draft.md
```

Add labels yourself. Your recent issues there use `bug` and `26.4_scope`. This one is a hardening request with no observed failure, so `bug` may not fit.

## Decisions for you

1. **Public issue or private report.** I wrote it as a public hardening request. It shows no exploit, nothing different has run, and PR #321 already proposes the same pin in public. It is still a supply-chain weakness on a job with `packages: write`. If you read it as a vulnerability, it should not go to the public tracker. Private vulnerability reporting is off on core-infra, and the org `SECURITY.md` says to write to `opensourcegroup@netcracker.com`.
2. **New issue or a comment on PR #321.** #321 is open and changes the same two lines. The issue adds only that a merge on `main` does not change released tags, and that a release is needed. A comment there may serve better. I wrote the issue because you chose the tracker.
3. **Whether you can defend it without me.** I found no AI policy in the repo or the org, so the body carries no disclosure. If you know of one, add what it asks for.
4. **Whether it is worth filing.** #321 has had no review since 2026-07-27, which may mean few maintainers are watching the repo. I did not check recent maintainer activity.

## Not established (the body says so where a claim rests on it)

- **Everything is five weeks old.** All observations are from 2026-09-23. Before filing, re-run the `git ls-remote` command, and check that `v2.5.2` still resolves to `71206242...`, that `main` is still `f7fba11d...`, and whether #321 has merged or a newer release exists. Update the body if any of that changed.
- **Support window of core-infra.** I did not find or read a support policy. `v2.5.2` is the version `qubership-ratelimit` uses, and the later releases carry the same pattern.
- **Reason for the tag at line 392.** I read only the `grep 'uses:'` output, not the lines around it. Open `generic-go-build.yaml` at that line and check for a comment explaining the tag before filing. The body does not claim there is none.
- **Other callers of `docker-build.yaml@<tag>`.** Not searched. Run, in a clone of core-infra: `grep -rn 'docker-build.yaml@' .github/`.
- **How the 16 repositories from #367 reference the workflow.** Not checked.
- **The tracker search** ran as the queries listed in the body. It was by title and body only, and I do not know whether it covered closed PRs fully. Re-run `docker-build.yaml@` and `pin` with `is:pr is:closed` before filing.
- **Reporting template.** core-infra has no `.github/ISSUE_TEMPLATE`. The org `Netcracker/.github` has `bug_report.yml` (Describe the bug, To Reproduce, Version, Logs, Additional information, `[Bug]: ` prefix) and `feature_request.yml`, whose fields I did not read. I used your usual structure (Goal, Context, Scope, Definition of done) and added the two sections the request genre needs ("Why this repository", "Prior proposals"). If the org form is applied at creation, check that this fits.
- **Markup.** I assumed GitHub Markdown with fenced blocks, as in your earlier issues. I did not open one.
- **The expected result of the second Definition of done item.** I ran the `jq` command only on a run that uses `v2.5.2`. That a SHA-pinned nested reference prints a SHA there is my expectation, not an observation.

## Left out of the body on purpose

- **The `skip-docker: true` plus `docker-build.yaml@<sha>` workaround.** Not tried. If it works it would be a caller-side change in `qubership-ratelimit`'s `go-build.yml` and does not need core-infra. Try it before deciding whether to mention it. `skip-docker` is a documented input of `generic-go-build.yaml`.
- **A `./` reference inside the callee.** GitHub's reuse docs say a same-repository `./` call runs from the same commit as the caller, but the page does not say how that works inside a nested workflow. I did not run it, so I did not propose it. It might remove the need for a pin, but only if the nested case behaves like the documented one.
- **The org conventions file** (`qubership-ai-packages`, `.agents/skills/qubership-workflow-conventions/SKILL.md`, "Pin every action ... as a full 40-character commit SHA"). It is written for actions, not reusable workflows, and I could not tell whether it counts as internal policy content, which your rule excludes. Add it if you are sure it is public and fine to cite.
- **The source finding's ID and text**, since it came from an internal review.
- **Unpinned `actions/upload-artifact@v4` in `qubership-workflow-hub`.** Mentioned in the body only as out of scope. If you want it fixed, it is a separate report to that repository.
- Impact beyond what I saw. The body states that no different logic has run and makes no claim about what a moved tag would do beyond the quoted GitHub documentation.
