# Hand-over note: feature request for tallyqueue/tallyqueue

This note is for you, the person filing. None of it goes into the issue.

## Filing

Title: `Liveness probe needs an unauthenticated endpoint on the management port`

Form: `.github/ISSUE_TEMPLATE/feature_request.yml`. The body's headings follow its fields in order: Problem (required), Proposal, Alternatives considered, Additional context, then the required search checkbox. In the web form, paste each section into its field. From the command line:

```bash
gh issue create --repo tallyqueue/tallyqueue \
  --title "Liveness probe needs an unauthenticated endpoint on the management port" \
  --label enhancement \
  --body-file out/draft.md
```

The form's required fields are enforced only in the web UI. `--label` fails if your account can't set labels on the repository; if it does, drop the flag.

## Routing

`SECURITY.md` says information the management port exposes is not treated as a vulnerability and asks for a public issue for hardening requests. Based on that, this goes to the public tracker. I didn't have `.github/ISSUE_TEMPLATE/config.yml` in the notes. Check whether its contact links send feature requests to Discussions before you file.

## Lookups I couldn't do (no network in this session)

Everything in the draft comes from the session notes dated September 23, 2026. Before filing:

- Rerun the tracker search, open and closed, issues and discussions: `healthz auth`, `healthz version`, `probe port`, `liveness`. Also try `livez`, `probe_addr`, and `separate listener`, which weren't searched. If anything new matches, tell me and I'll update the draft.
- Check that #412 is still closed and #977 is still open with no agreed design. If #977 now has a design that puts the probe on its own listener, a comment there may be better than a new issue. That's your call.
- Check https://github.com/tallyqueue/tallyqueue/releases for a release newer than 2.3.1.
- Open the two links in the body and confirm they resolve: the v2.3.1 `docs/operations/management.md` (the quoted sentence must be there word for word) and the Kubernetes probes page (the `httpHeaders` section must still say header values are literal).

## Claims resting on less than a transcript

- "The image is distroless and ships no `tallyqueuectl`" comes from the notes and has no transcript behind it. To confirm, list the image contents (for example, `crane export <image>@<digest> - | tar -t | grep tallyqueuectl`) or check the image's Dockerfile.
- Whether `/ping` fails when the management side is wedged isn't established. The body says so. Leave it that way unless someone tests it.
- The `main` check at `5d2e8b1` was a source read with `git show`, not a build. The body says so.

## Redactions and what to confirm before publishing

- Replaced `pg-queue-01.corp.pellham.net` with `pg-queue-01.corp.example.net`, and `10.20.4.17` with `10.0.0.17`, in every command and output. The body says names were changed.
- Left out the company name, the security review ID, and the standard's internal ID. The body calls it "our organization's security standard for service management interfaces".
- The body quotes §3.2, §3.4, and §4.1 of the internal standard word for word and mentions that the exception ends on December 31, 2026. Confirm that both are fine to publish. If they aren't, paraphrase the three requirements. The request still holds, but it is weaker, because those requirements explain why each alternative fails.
- The `/healthz` output still shows the real version, commit, uptime, pool size, and worker count. None of those are secrets, but check them.

## Left out of the body on purpose

- **The external scanner report from September 21, 2026** (missing security headers, server version disclosed, TLS not enabled on port 9401). The notes don't say which endpoint the version finding came from, and the other findings aren't part of this request. The body lists TLS and headers as out of scope. File them separately if you want them fixed.
- **The security team's chat thread about advisories in other queue servers**, where health endpoints leaked database passwords. Our `/healthz` shows a host but no password, so citing those advisories would claim an impact we didn't observe.
- **The reading of `internal/mgmt/server.go`**, which suggests a second `http.Server` is feasible. It's an unchecked guess, and the Proposal leaves the mechanism to the maintainers. If a maintainer asks, you can offer it in a comment, marked as a guess.

## Your call

- `CONTRIBUTING.md` has no AI policy, so nothing has to be disclosed. Whether to mention that a tool drafted this is up to you.
- Be ready to answer follow-up questions without the tool, especially about the security standard and the alternatives you ruled out.
