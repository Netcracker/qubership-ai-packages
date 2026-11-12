# Hand-over note: feature request for tallyqueue/tallyqueue

Nothing has been filed. `draft.md` is the issue body. The first line is the title, so remove it from the body before filing. The headings follow `.github/ISSUE_TEMPLATE/feature_request.yml` in its order: Problem, Proposal, Alternatives considered, Additional context, and the required checkbox. If you file through the web form, paste each section into its field. If you file with `gh`, the form isn't applied, so the headings stay in the body:

```bash
# save the body without the "Title:" line as body.md first
gh issue create --repo tallyqueue/tallyqueue \
  --title 'Liveness probing forces `/healthz` to stay open on an authenticated management port' \
  --label enhancement \
  --body-file body.md
```

## Decisions for you

- **Naming the organization and the standard.** The draft says "our internal security standard" and doesn't name Pellham, SECREV-2291, or SEC-STD-014. It paraphrases §3.2, §3.4, and §4.1 without quoting them. Decide whether you're comfortable publishing even that much, or whether you'd rather name the company.
- **AI disclosure.** `CONTRIBUTING.md` has no AI policy and the form has no disclosure checkbox, so the project asks for nothing. Whether to mention that a tool drafted this is your call. You should be able to explain and defend every point without the tool, because maintainers will ask follow-up questions.
- **Comment on #977 instead?** I don't recommend it. #977 asks to hide fields from `/healthz`, and that wouldn't satisfy §3.2 because the listener still serves the admin endpoints. The draft links it as a related issue. You could also leave a short comment on #977 that links the new issue.
- **The checkbox.** The search was done during the session on September 23, 2026. Re-run it before you tick the box (see below).
- **Offering a patch.** The draft doesn't offer one. If you plan to implement `probe_addr`, add one line at the end saying so.

## Gaps and checks to run before filing

The session had no network access, so none of the following was checked after September 23, 2026.

- **New releases.** 2.3.1 was the latest release on September 23. Check https://github.com/tallyqueue/tallyqueue/releases for anything newer, and its changelog for `/healthz`, probe, or listener changes. If a newer release exists, update the version line in Additional context.
- **Duplicate search.** Re-run on issues and discussions, open and closed: `healthz auth`, `healthz version`, `probe port`, `liveness`. Also try `livez`, `probe_addr`, `separate listener`, and `health port`, which weren't run. Check whether #977 has gained a design since then.
- **Title convention.** Check whether recent `enhancement` issues use a component prefix, and match it if they do.
- **Markup.** Fenced code blocks and a task-list checkbox are assumed. Glance at an existing feature request to confirm.
- **`exec` probe claim.** Your notes say the image is distroless and ships no `tallyqueuectl`, but don't say which image or tag was checked, or how. Confirm it on the official image, for example with `docker run --rm --entrypoint tallyqueuectl <image>:2.3.1 ping`, which should fail if the binary is absent. If you can't confirm it, drop that bullet.
- **Kubernetes docs citation.** The draft cites the page by title. If you want a link, check the URL for "Configure Liveness, Readiness and Startup Probes" on kubernetes.io and add it.

## What I left out, and why

- **Whether `/ping` on 9400 fails when the management side is wedged.** This was not established, and the draft makes no claim about it.
- **The reading of `internal/mgmt/server.go`** (one `http.Server` started in `Start()`, so a second listener "looks feasible"). It's an unverified guess about their code, and a maintainer can judge feasibility better than we can. The draft says only that the proposal is untested.
- **The external scanner report (September 21, 2026).** The missing security headers and the lack of TLS are separate hardening topics. "Server version disclosed" overlaps with #977. If you want any of these upstream, they need their own issues or a comment on #977.
- **The security-team chat about advisories in other queue servers.** `/healthz` on 2.3.1 shows a store host but no credentials. Citing leaked passwords in other products would be speculative impact, and triagers dismiss that. `SECURITY.md` says information exposed on the management port isn't treated as a vulnerability and asks for a public issue, so the public tracker is the right channel.
- **The probe settings** (three replicas, `httpGet` every 10 s). They don't change what a maintainer would decide.

## Redaction

- `10.20.4.17` became `10.0.0.17` in both commands.
- `pg-queue-01.corp.pellham.net` became `pg-queue-01.corp.example.net` in the `/healthz` output.
- The outputs are captured evidence and weren't re-run with the substitutes. The draft says the address and the host name were changed. Nothing else in the transcripts is private: version `2.3.1` and commit `9e41c07` are public, and no token appears anywhere.
