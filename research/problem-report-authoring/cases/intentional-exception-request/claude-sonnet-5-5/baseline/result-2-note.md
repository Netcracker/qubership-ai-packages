# Hand-over note (not part of the issue)

## How to file

The issue form's required fields are enforced only in the web UI, so with `gh` the body carries the form's labels as headings (`Problem`, `Proposal`, `Alternatives considered`, `Additional context`). The "I searched existing issues and discussions" checkbox is yours to tick. Title and command:

```bash
gh issue create --repo tallyqueue/tallyqueue \
  --title "Liveness probe needs an unauthenticated endpoint on the management port" \
  --label enhancement \
  --body-file draft.md
```

## Decisions for you

- **Defend it.** Please confirm you can explain and answer follow-ups on this without me. `CONTRIBUTING.md` has no AI policy, so I added no disclosure; whether to mention the tool is your call.
- **Your internal standard.** The issue paraphrases SEC-STD-014 (§3.2, §3.4, §4.1) as "my organization's standard" and leaves out its name, the review number SECREV-2291, the exception date, and the company name. Check that you may describe it publicly, and whether you want to name Pellham.
- **Issue or comment on #977.** I wrote a new issue because #977 asks for a different change (hiding fields). A comment there is the alternative if you prefer one thread.
- **Patch.** I did not offer a pull request. Add one line if you intend to write it.

## Not established

- **Redaction.** I replaced the IP `10.20.4.17` with `10.0.0.5` and `pg-queue-01.corp.pellham.net` with `pg-queue-01.example.internal`. The pasted output was captured with the real values and edited in place, not re-run. The `/healthz` JSON, `commit`, and `uptime_s` are as captured. Check the output once more for anything you consider private.
- **Currency.** The observations are from 2026-09-23 on 2.3.1, the latest release that day. Today is 2026-10-31. Check the releases page for anything newer and re-run the `/healthz` check there; if the behavior changed, the issue needs updating. I also have no timezone for the observations.
- **Source reads.** `main` at `5d2e8b1` was read, not built. I did not record which revision I read `internal/mgmt/server.go` from for the "a second `http.Server` looks feasible" sentence. Treat it as an untested guess, as the issue says.
- **Alternatives I did not run.** The `exec` probe was not tried. The claim that the image ships no `tallyqueuectl` comes from your notes, not from a run in this session. Whether `/ping` fails when the management side is wedged is open.
- **Tracker search.** The results come from your notes: queries `healthz auth`, `healthz version`, `probe port`, `liveness` over issues and discussions, open and closed. Hits were #412, #977, and #1203 (unrelated, readiness during leader election). I left the queries out of the issue. I did not reopen #412 or #977 to check the quoted text.
- **Routing and security lookups.** Read from your notes only: `SECURITY.md` says information the management port exposes is not a vulnerability and asks for a public issue for hardening requests, so a public issue is the right channel. I did not open the form or `config.yml` contact links. `gh issue create` skips the form, so confirm the issue renders under the `feature_request.yml` headings.

## Left out on purpose

- The external scanner findings (missing security headers, version disclosure, no TLS). They are about port 9401 generally and don't bear on this request.
- The two advisories from other queue servers where a health endpoint exposed a connection string. No such exposure was observed in Tallyqueue (`/healthz` shows host and database name, not credentials), so the issue would carry speculative impact.
- The temporary exception date.
