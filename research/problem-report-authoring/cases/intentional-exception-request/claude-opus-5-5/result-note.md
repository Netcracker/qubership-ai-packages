# Hand-over note: Tallyqueue feature request (not part of the issue body)

## Filing

The body is in `result.md`. The repository's form (`feature_request.yml`) is enforced only in the web UI, so the body writes the field labels as headings and ticks the search checkbox itself. To file from the CLI:

```bash
gh issue create --repo tallyqueue/tallyqueue \
  --title "No way to require the management token on every management-port path while keeping a token-less liveness probe" \
  --label enhancement \
  --body-file result.md
```

Or paste each section into the matching field of the web form: Problem, Proposal, Alternatives considered, Additional context, then tick the checkbox.

## Decisions for you

- **Naming Pellham and the standard.** The issue refers to "our security rules" and paraphrases SEC-STD-014 §3.2, §3.4, and §4.1 without naming the company, the standard, or SECREV-2291, because those are internal. If you want to name them or quote the clauses, that is your call.
- **Deadline.** The temporary exception ends on 2026-12-31. The issue leaves the date out so it does not read as a milestone set for the project. Add it as a cost if you want the maintainers to know it.
- **Offer a patch?** The notes say a second `http.Server` in `internal/mgmt/server.go` `Start()` looks feasible from reading the code (not built or run). If your team is willing to send a PR, add one line at the end of the Proposal field. The issue does not say so now.
- **AI disclosure.** `CONTRIBUTING.md` has no AI policy and the form has no disclosure field, so the issue says nothing. Whether to mention that it was drafted with a tool is up to you. Be ready to answer maintainer follow-ups yourself.

## Left out on purpose

- The external scanner report (missing security headers, version disclosed, no TLS): separate hardening topics, not this request. File separately if wanted; version disclosure overlaps #977, so a comment there fits better than a new issue.
- The security-team pointer to advisories in other queue servers where a health endpoint leaked a DB password: nothing like that was observed in Tallyqueue (`/healthz` shows host and database name, no credentials), so it would be speculative impact. `SECURITY.md` also says information the management port exposes is not treated as a vulnerability and hardening requests go to public issues, so the public tracker is the right channel.

## Gaps not established, and how to close them

- **Whether `/ping` on port 9400 fails when the management side is wedged.** The issue says this is unknown. To check: block the management side (for example stop the worker pool or freeze the process's management goroutines in a test deployment) and watch `curl -s -i http://<pod-ip>:9400/ping`.
- **`tallyqueuectl` absent from the image.** The notes state the image is distroless without it, but not how that was checked. Confirm before filing: `kubectl debug -it <pod> --image=busybox --target=tallyqueue -- ls /proc/1/root/usr/local/bin /proc/1/root/usr/bin` (or `crane export <image> - | tar t | grep tallyqueuectl`).
- **Tracker search was done in the session notes, not re-run here.** Before filing, re-run the queries on the live tracker in case something new appeared: `healthz auth`, `healthz version`, `probe port`, `liveness`, plus `probe_addr` and `livez` (issues and discussions, open and closed).
- **Behavior on `main`.** Only `router.go` on `main` at `5d2e8b1` was read, not built or run. If you want certainty that `main` has not added such an option elsewhere, grep `main` for `probe` in the config docs: `git -C <clone> grep -n -i probe origin/main -- docs internal/config`.
