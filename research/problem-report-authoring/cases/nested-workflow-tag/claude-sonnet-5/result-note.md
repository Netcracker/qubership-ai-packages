## Hand-over note (not part of the issue body)

**Channel and form.** `Netcracker/qubership-core-infra` has no `.github/ISSUE_TEMPLATE` of its own, so GitHub falls back to the org default at `Netcracker/.github/.github/ISSUE_TEMPLATE/bug_report.yml`: fields "Describe the bug" and "To Reproduce" (required), "Version", "Logs", "Additional information" (optional), title prefix `[Bug]: `, label `bug`. `result.md` is written to match those field names and order. A form's required fields and its title prefix/label are enforced only in the web UI — filing with `gh issue create --body-file result.md` will not add the `[Bug]: ` prefix or the `bug` label on its own. Suggested command, once you've reviewed the body:

```
gh issue create --repo Netcracker/qubership-core-infra \
  --title "[Bug]: generic-go-build.yaml calls docker-build.yaml by a mutable tag, so pinning the caller by commit SHA does not pin the Docker build/push job" \
  --body-file result.md \
  --label bug
```

Adjust the title if you'd rather phrase it differently — this is a suggestion, not something I filed.

**Open decision — file a new issue, or comment on PR #321 instead?** PR #321 already changes exactly this line on `main` (and the equivalent lines in `generic-maven-build.yaml`, `maven-deploy.yml`, `maven-verify.yml`) from a tag to a SHA. It's been open since 2026-07-27 with zero human reviews. It's plausible it's stalled because, as a Renovate PR, its description gives no rationale — it doesn't say this is what breaks a caller's own SHA pin, and it doesn't cover already-tagged releases. You may prefer to post this as a comment on #321 asking for it to be merged, rather than opening a new issue that largely restates the same fix. I filed it as a separate issue because the skill this was drafted under treats "comment vs. new issue vs. PR" as your call to make, not mine, and because this report's scope (the recurring pattern across releases, and the fact that already-tagged commits like `v2.5.2` can never be fixed after the fact) is broader than that one PR's diff. If you comment on #321 instead, most of `result.md`'s "Describe the bug" section can be pasted as the comment, and the "To Reproduce" / "Expected behavior" content still applies.

**Not established — steps I did not take, with what would close them:**

1. Whether the 16 repositories that issue #367 says depend on `generic-go-build.yaml` also pin it at a commit that still contains the bare-tag `docker-build.yaml@` line. Not checked. To close it: for each of those 16 repos, find their `uses: .../generic-go-build.yaml@<ref>` line, resolve `<ref>` to a commit, and grep that commit's `generic-go-build.yaml` for `docker-build.yaml@` to see whether it's a tag or a SHA.
2. Whether the `skip-docker: true` input plus a caller-side job that calls `docker-build.yaml@<sha>` directly works as a workaround today, letting `qubership-ratelimit` (or another caller) get a fully SHA-pinned run without waiting for a core-infra fix. Not tried. To close it: add such a job to a branch of the caller, run it, and check the run's `referenced_workflows` the same way this report did, to confirm no tag-resolved reference remains.
3. I did not check the AI-disclosure policy beyond confirming none exists in this repo's or the org's `CONTRIBUTING.md`/`SECURITY.md` — if `Netcracker/qubership-core-infra` maintainers have an unwritten expectation about tool-assisted reports, that's yours to know and mine not to guess.

**Redaction:** nothing in this report needed redacting — every name, commit, run ID, and URL is already public (public repositories, public Actions runs, public GitHub docs), and no secrets or personal data appear in any of the pasted output.

**Not routed as a security report.** This is a design gap in workflow-pinning discipline, not a demonstrated compromise (the `v2.5.2` tag today still points to the pinned commit), and the project already discusses closely related pinning issues in its public tracker (#321, #401). Filing it publicly matches that precedent. If you disagree and want it handled as a vulnerability instead, `Netcracker/qubership-core-infra` has private vulnerability reporting turned off; the org's `SECURITY.md` route is `opensourcegroup@netcracker.com`.
