# Hand-over note for the person filing

Nothing has been filed. The draft is `draft.md`. Use the `Title:` line as the issue title, then paste the sections under the rule into the matching fields of `.github/ISSUE_TEMPLATE/feature_request.yml` (Problem, Proposal, Alternatives considered, Additional context). Label: `enhancement`.

## Before you file

1. **Tick the required checkbox yourself** ("I searched existing issues and discussions"). I could not run the search. It was done in the session, per the notes, with these queries over issues and discussions, open and closed: `healthz auth`, `healthz version`, `probe port`, `liveness`. Hits: #412, #977, and #1203 (closed, readiness during leader election, unrelated). Re-run them if you want a current result.
2. **Attribution.** The report says "I" and "observed on 2026-09-23" for the curl loop, the `/healthz` body, and the `/ping` check. Confirm those are yours (or your team's) observations. I did not run anything.
3. **Source reads are unrun.** The `router.go` lines and the `server.go` reading come from reading source. The `main` comparison at `5d2e8b1` (2026-09-20) was a `git show`, not a build, and I left it out of the report.
4. **Redaction on a public tracker.** I replaced the pod IP `10.20.4.17` with `10.0.0.17` and the PostgreSQL host `pg-queue-01.corp.pellham.net` with `pg-queue-01.corp.example.net`. The curl output was edited in place and the report says so. I did not name Pellham, the review ID SECREV-2291, or the standard's number (SEC-STD-014), and I paraphrased the standard instead of quoting it. If you want to quote §3.2 and §3.4 verbatim or name the organization, that is your decision.
5. **The 2026-12-31 date** is the exception deadline from your notes. It is internal. Keep it only if you are happy to disclose it; the cost-of-delay sentence reads fine without it.
6. **Unverified claim to check.** The report says the 2.3.1 image is distroless and has no `tallyqueuectl`. The notes list it as "not tried", and I could not tell whether the missing binary was observed. Check with, for example, `docker create <image>` then `docker export <container> | tar -t | grep tallyqueuectl`, or fix the sentence.
7. **Not established, and stated as such in the report:** whether `/ping` fails when the management side is wedged. A quick test would be to block the management listener on a test instance and probe `/ping`.

## Questions for you

- **Is there anyone besides you with this requirement?** The report says you know of no one else. Add a name or a team if there is one.
- **Would a pull request serve better?** You have a design in mind but no patch. A comment on #977 is the other option, but it asks for something different (hiding details), so I wrote a new issue and linked it.
- **Do you want to be the person who answers follow-up questions?** CONTRIBUTING.md has no AI policy, so no disclosure is required, and I added none.

## Left out on purpose

- The external scanner report (missing security headers, version disclosure, TLS not enabled). It does not bear on the `/healthz` request and would widen the scope.
- The security-team thread about two advisories in other queue servers. Nothing observed here shows a connection string or password in `/healthz`, so including it would be a speculative consequence.
- Routing: `SECURITY.md` says information the management port exposes is not a vulnerability and asks for hardening requests as public issues, so a public issue is the right channel.
