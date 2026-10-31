# Hand-over note (not part of the issue)

## To filing

- Target: `tallyqueue/tallyqueue`, form `feature_request.yml`, label `enhancement`. The title is in an HTML comment at the top of `draft.md`: "No way to run a Kubernetes liveness probe when every management endpoint must require a token". Move it to the title box and delete the comments.
- The fields follow the form's order: Problem, Proposal, Alternatives considered, Additional context, then the required checkbox. I put the checkbox in as ticked because the search was done (queries below). Confirm that is right when you file.
- `CONTRIBUTING.md` has no AI policy and the form has no disclosure field, so the draft says nothing about how it was written.
- `SECURITY.md` says information exposed by the management port is not a vulnerability and asks for hardening requests as public issues, so a public issue is the right channel.

## Decide before filing

1. **Naming your organization and its standard.** I wrote "my organization" and "our security standard (internal)" and left out Pellham Transit, SECREV-2291, and SEC-STD-014. The draft paraphrases the standard's §3.2 (listener rule), §3.4 (network restrictions), and §4.1 (no credentials in manifests). Check that you may paraphrase it publicly, and say if you want the name or the document ID in.
2. **Comment on #977 instead?** I filed a new request because #977 asks for something different (hide details, no design agreed). You may prefer a cross-linking comment there. Your call.
3. **Can you explain and defend the request** (the 9402 listener idea and the standard's rules) in the thread yourself? No policy requires it here.
4. **The temporary exception date** (2026-12-31) is in the draft as the cost of not doing this. Remove it if you don't want to publish a deadline.

## Redaction

- Replaced for the public tracker, consistently in the command and the output: management address `10.20.4.17` became `10.0.4.17`, and the store host `pg-queue-01.corp.pellham.net` became `pg-queue-01.corp.example.net`. The last line of the draft says names were changed.
- The command and output are otherwise as captured on 2026-09-23. I did not re-run them after the substitution; the substitution does not change any status code. The `mgmt-paths.txt` file is not attached, but the pasted output lists every path in it.
- No tokens or credentials appeared in the notes.

## Left out on purpose

- The external scanner report for 2026-09-21 (missing security headers, version disclosure, TLS not enabled). It does not bear on the liveness probe, and the draft says TLS and headers are out of scope.
- The security-team chat thread about two advisories in other queue servers where a health endpoint leaked a connection string. No such leak was observed in Tallyqueue, so citing it would be a speculative consequence. If you want it in, add a link only if the advisories are public.

## Not established (the draft states the first three where a claim depends on them)

- The proposal was not implemented, built, or tested, and the `internal/mgmt/server.go` reading did not record a commit. Open the file on `main` and confirm the single `http.Server` in `Start()` before you rely on that sentence.
- The `main` reading at `5d2e8b1` is a source read only, not a run.
- Whether `/ping` on port 9400 fails when the management side is wedged. To check: wedge or block the management listener on a test replica and call `curl -i http://<host>:9400/ping`.
- The `exec` probe was not tried. To check: `kubectl exec <pod> -- tallyqueuectl ping` fails if the binary is absent; the image is distroless, so expect "executable file not found".
- The Kubernetes documentation claim (`httpGet` header values are literals and cannot reference a Secret) comes from the page named in the draft, which I could not fetch in this session. Re-read the `httpHeaders` section for 1.30 before filing.

## Tracker search to repeat or confirm

Issues and discussions, open and closed: `healthz auth`, `healthz version`, `probe port`, `liveness`. Hits: #412, #977 (both in the draft), and #1203 (closed, readiness during leader election, unrelated, not mentioned). Run the same queries again just before filing, and add `livez`, `probe listener`, and `management.probe_addr` in case a request opened since 2026-09-23 covers this.
