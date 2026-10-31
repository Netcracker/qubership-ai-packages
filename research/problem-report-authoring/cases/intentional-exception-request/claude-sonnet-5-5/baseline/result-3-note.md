# Hand-over note for the person filing

Nothing was filed or sent. The draft is `draft.md`: the body is for the `feature_request.yml` form (label `enhancement`), and the title is on its first line. Paste each `###` section into the field with that name. The checkbox is ticked based on the search recorded in the notes; confirm it.

## Decide before filing

1. **New issue or a comment on #977?** #977 is open, has `help wanted`, and covers the data `/healthz` returns. I drafted a new issue because the ask (a separate probe listener) differs. A maintainer may want to merge them, so your call.
2. **Quoting the internal standard.** The draft paraphrases the conditions of the standard's §3.2, §3.4, and §4.1 without its ID, title, or version, and leaves out the review ID and your organization's name. Check that your organization allows even that on a public tracker. The 2026-12-31 exception date is in the draft as the cost of leaving it undone; delete it if you would rather not state it.
3. **Disclosure.** `CONTRIBUTING.md` has no AI policy, so the draft carries no disclosure. Add one if you want to.
4. **You must be able to defend the draft** without me, including the proposal and the claims about `internal/mgmt`.

## Redactions

Replaced: the management IP (`10.20.4.17` is `10.0.0.5` in the draft) and the store host (`pg-queue-01.corp.pellham.net` is `pg-queue-01.corp.example.net`). The curl commands and `/healthz` output are the real ones with only those substitutions, so the output was not produced by the substituted commands; the draft says that. The `/healthz` body is otherwise verbatim. Check that `db` = `tallyqueue` and the version, commit, and pool numbers are fine to publish.

## Not established (the draft says so where a claim rests on it)

- Whether `/ping` fails when the management side is wedged. Close it with: stop or hang the management listener on a test replica, then `curl -s -i http://<ip>:9400/ping`.
- The `exec` probe: the draft says it was not tried. The missing `tallyqueuectl` comes from your notes, not from a transcript. Check with `kubectl exec <pod> -- tallyqueuectl` (or `kubectl debug`, since the image is distroless).
- Feasibility of a second listener. The proposal is marked untested, from a reading of `internal/mgmt/server.go`.
- `main` at `5d2e8b1` was read with `git show`, not built or run.
- `mgmt-paths.txt` is not attached; the draft describes it in words. Attach the file or paste its 23 lines if you want the reproduction to be re-runnable.

## Left out on purpose

- The external scanner report of 2026-09-21 (missing security headers, version disclosure, TLS not enabled). It is about port 9401 in general and does not show the gap in this request. The "TLS not enabled" finding fits the draft's out-of-scope line.
- The security-team chat about two advisories in other queue servers. Nothing was observed in Tallyqueue's `/healthz` that matches them (no credentials in the body), so citing them would be speculative impact.
- Wording about a patch: you have none, so the draft offers none.

`SECURITY.md` asks for a public issue for hardening requests and says information on the management port is not treated as a vulnerability. I judged the draft within that. If you think the version and store details are a vulnerability, stop and use a private channel instead.
