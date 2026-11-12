# Hand-over note for the person filing

Nothing has been filed or sent. `draft.md` is the body for `tallyqueue/tallyqueue`, written into the fields of `.github/ISSUE_TEMPLATE/feature_request.yml` in their order (Problem, Proposal, Alternatives considered, Additional context, then the checkbox). Label: `enhancement`.

Suggested title: `No way to run a liveness probe while every management endpoint requires a token`

## Decide before filing

- **The request reverses a maintainer decision.** #412 closed with "put the management port behind a network policy". The draft cites it and argues from the standard rather than from the project's docs. Confirm you want the issue framed this way.
- **Comment on #977 instead?** It is open with the `help wanted` label and is about the same endpoint, but it asks to hide fields, not to remove the unauthenticated path. I wrote a new issue and distinguished it. A comment there is the alternative.
- **Your internal standard.** I paraphrased it ("network restrictions do not substitute for authentication", credentials not in manifests) and left out its ID, version, and section numbers because it is internal. I also left out SECREV-2291 and the 2026-12-31 exception. Tell me if you want the standard quoted, or want the organization named.
- **Offering a patch.** The draft does not offer one. Add a line if you or the team would write it.
- **Defending the issue.** `CONTRIBUTING.md` has no AI policy, so no disclosure is required. You should still be able to explain and answer follow-up questions on it yourself.
- **The checkbox is ticked** on the strength of the search below. Re-run it if you want to be sure.

## Names changed in the draft

Because the tracker is public, I replaced the node address `10.20.4.17` with `10.0.0.17` (in the command and both outputs) and the database host `pg-queue-01.corp.pellham.net` with `pg-queue-01.corp.example.net`. The draft says so in one sentence. "Pellham" does not appear in it. The captured output is otherwise as pasted in the session notes. The output was trimmed in the draft to three lines.

## Not established

- The tracker search is from the session notes, not re-run. Queries (issues and discussions, open and closed): `healthz auth`, `healthz version`, `probe port`, `liveness`. Hits were #412, #977, and #1203 (closed, readiness during leader election, unrelated). Re-run them before filing, since the notes are dated 2026-09-23.
- The `main` reading (`5d2e8b1`) is from `git show` only. Check whether `main` has moved: `git log --oneline 5d2e8b1..origin/main -- internal/mgmt`.
- The design in Proposal was neither implemented, built, nor tested, and the draft says so. The `server.go` claim is from reading the source.
- Whether `/ping` fails when the management side is wedged. The draft says this was not established. A check: stop or block the management goroutine in a test pod and request `/ping`.
- The `exec` probe was not tried. The draft states the image is distroless with no `tallyqueuectl`, which came from the notes with no transcript. Check it: `kubectl debug` with an ephemeral container, or `docker export` on the 2.3.1 image, then look for `tallyqueuectl`.
- The Kubernetes docs claim (probe `httpHeaders` take literal values only) is cited from the docs page named in the notes. I did not re-read the page, and the URL in the draft is the standard location of that page. Open it and confirm the sentence before filing.
- I did not check whether other versions (2.3.0 or earlier) behave the same. The draft reports 2.3.1 only.

## Left out on purpose

- The external scanner report (missing security headers, version disclosure, TLS not enabled). It does not bear on this request, and TLS and headers are separate asks. The draft only says they are out of scope.
- The two advisories from other queue servers where a health endpoint exposed a connection string with its password. Tallyqueue's `/healthz` shows the database host and name but no password, so the comparison would read as a speculative consequence. If you want to raise impact, paste only what `/healthz` was observed to return, which the draft already does.
- `SECURITY.md` says information exposed by the management port is not treated as a vulnerability and asks for a public issue for hardening requests, so a public issue is the right channel.
