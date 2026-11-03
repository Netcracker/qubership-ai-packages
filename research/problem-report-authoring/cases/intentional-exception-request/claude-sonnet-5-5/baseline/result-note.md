# Hand-over note for the person filing

Nothing has been filed. `draft.md` is the issue body, with the title on its first line. Remove that line from the body file before filing.

## Filing

`.github/ISSUE_TEMPLATE/feature_request.yml` is enforced only in the web UI. I wrote its four fields (Problem, Proposal, Alternatives considered, Additional context) as headings, followed by the required checkbox. To file from the command line:

```bash
gh issue create --repo tallyqueue/tallyqueue --label enhancement \
  --title "Cannot require a token on every management endpoint and still run a Kubernetes liveness probe" \
  --body-file <body file without the title line>
```

Applying a label may need triage rights. If you lack them, drop `--label` and the maintainers will add it.

## Decide before filing

1. **New issue or a comment on #977?** #977 is open and covers the same response body, but asks for something different (hiding details, not a separate listener). I wrote a new issue. A comment there may serve better if you want to avoid a second thread.
2. **Is the project likely to want this?** #412's closing comment says `/healthz` stays open and points at network policy. The router comment says "Do not add auth here". The request is framed as opt-in to respect that, but you know whether the maintainers will welcome it.
3. **Publishing internal material.** The issue is public. I paraphrased the internal standard without its number or section numbers, and I left out the review ID. It does state that a security review blocks production and that a temporary exception ends on 2026-12-31. Confirm your organization accepts both, or cut the date.
4. **Voice.** The report speaks as you ("I requested", "I deploy"). The observations are from the 2026-09-23 session. Be sure you can stand behind them. `CONTRIBUTING.md` has no AI policy, so no disclosure is required.

## Not established

- **Currency.** The observations are from 2026-09-23 and the notes say 2.3.1 was the latest release then. Check for a newer release since, and re-run the curl loop against it if there is one. The same applies to the tracker search: re-run `healthz auth`, `healthz version`, `probe port`, and `liveness` (issues and discussions, closed included). The checkbox is ticked on the strength of the earlier search.
- **Image contents.** The claim that the distroless image has no `tallyqueuectl` has no transcript in the notes. For example, run `crane export <image> - | tar -t | grep tallyqueuectl`, or `docker create` then `docker export`. The exec probe was never tried.
- **Docs version.** I could not tell which version of `docs/operations/management.md` the quoted sentence comes from. Check that it is in the 2.3.1 tag.
- **Proposal.** Never built or run. It rests on reading `internal/mgmt/server.go`, and the report says so.
- **`/ping` on 9400.** Whether it fails when the management side is wedged was not established, so the report does not use it either way.

## Redaction

The curl command, both captures, and the prose use `192.0.2.17` for the node address and `pg-queue-01.example.net` for the database host. The captures are labeled as redacted. The commit `9e41c07` and the cluster details are left as they were. If you paste fresh output, make the same substitutions.

## Left out on purpose

- The external scanner report (missing security headers, version disclosure, TLS not enabled). It is not about the probe, and it would widen the ask.
- The two advisories from the security-team chat about a health endpoint exposing a connection string with a password. Nothing like that was observed in `/healthz` here (no password in the response). Including them would be a speculative consequence.

`SECURITY.md` says information the management port exposes is not treated as a vulnerability and asks for a public issue for hardening requests, so a public issue is the right route.
