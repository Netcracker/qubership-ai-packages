# Hand-over note (not part of the issue)

## Filing

Target: `tallyqueue/tallyqueue`, form `.github/ISSUE_TEMPLATE/feature_request.yml`, label `enhancement`. The draft body is `draft.md`. Its headings follow the form's field labels (Problem, Proposal, Alternatives considered, Additional context). The web form enforces the required checkbox, but `gh` does not, so the checkbox is yours to tick if you file in the browser.

Suggested title: `Liveness probe without an unauthenticated /healthz on the management port`

```bash
gh issue create --repo tallyqueue/tallyqueue --label enhancement \
  --title "Liveness probe without an unauthenticated /healthz on the management port" \
  --body-file draft.md
```

Nothing has been filed. I had no network access, so I never opened the form, the issue tracker, or the repository.

## Decide before filing

- **Whether to say who we are.** The draft names neither Pellham Transit nor the review ticket (SECREV-2291). It describes "our security review" and "our organization's security standard". Say if you want either named.
- **The internal standard.** SEC-STD-014 is internal. The draft paraphrases §3.2, §3.4 and §4.1 and does not quote them or give the number. Check that your organization is happy with that paraphrase being public.
- **The exception date.** The 2026-12-31 exception is left out. It would show urgency, but it is an internal fact and does not help a maintainer decide.
- **Whether to file at all, or comment on #977 instead.** #977 is open, labeled `help wanted`, and has 6 reactions. The draft treats it as a different change (hide data versus a separate probe listener). A maintainer may prefer one thread, so you may want to comment there.
- **Whether you can explain and defend the issue yourself.** `CONTRIBUTING.md` has no AI policy, so the draft carries no disclosure. Whether to mention that a tool drafted it is your call.
- **The project's activity.** I did not check whether maintainers are responding. #977 has no agreed design since 2025-03-11.

## Left out on purpose

- The external scanner report of 2026-09-21 (missing security headers, version disclosure, no TLS). It is a different request and would widen the scope.
- The chat thread about two advisories in other queue servers. It supports a speculative impact and nothing observed here. `SECURITY.md` also says exposure through the management port is not treated as a vulnerability and asks for public hardening issues, so I treated this as a public issue.
- The comment in `internal/mgmt/router.go` (lines 41-43 at v2.3.1 and on `main` at `5d2e8b1`). The documentation and #412 already say the same thing.

## Not established, and how to close each

1. **Quotes and claims about documents.** I took the `docs/operations/management.md` quote and the #412 text (title, closing comment, closed 2024-05-02, fixed in 1.8.0) from the notes, and did not re-read them. Compare them against the repository at v2.3.1 and the tracker. Also check that the Kubernetes docs page for `httpHeaders` still says header values are literal.
2. **The distroless image has no `tallyqueuectl`.** The notes state this, and no check is recorded. Run `docker run --rm --entrypoint ls <image> /` or `kubectl debug` against a pod. If the binary exists, the `exec` alternative needs rewriting.
3. **`internal/mgmt/server.go`.** The "one `http.Server` started in `Start()`" claim comes from reading the code, and the notes do not record the revision. Check it at v2.3.1 and fix the sentence if it differs. The proposal is marked untested.
4. **`main` was not run.** The notes show the `/healthz` source lines are unchanged on `main` at `5d2e8b1`, read with `git show`. The draft makes no claim about `main`. A newer release or commit may behave differently, so a quick check of the release notes after 2.3.1 would help.
5. **Whether `/ping` fails when the management side is wedged.** Stated in the draft as not established. To test it, stall or block the management listener on a test instance and probe `/ping`.
6. **"I found no other setting that closes `/healthz`".** This rests on the documentation. If you went through the full configuration reference, say so. If not, read it.
7. **Searches.** The tracker searches (issues and discussions, open and closed) were `healthz auth`, `healthz version`, `probe port`, `liveness`. The hits were #412, #977, and #1203 (unrelated, readiness during leader election). Trackers match titles poorly, so a search for `livez`, `probe listener`, and `separate port health` is worth running before you tick the checkbox.
8. **The `curl` loop.** I ran it against the live deployment before the draft. `mgmt-paths.txt` is not in the draft, which lists 6 of its 23 paths. If you'd rather the reader can re-run it, add the 23 paths.

## Redactions

I replaced the node IP address `10.20.4.17` with `192.0.2.17` and the database host `pg-queue-01.corp.pellham.net` with `db-primary.example.net`. The `curl` command, both outputs, and the prose use the same substitutes. The pasted `/healthz` body is otherwise verbatim and was not re-run with them. No secrets were present. The database name `tallyqueue` is unchanged, since it is the product's name for the database.
