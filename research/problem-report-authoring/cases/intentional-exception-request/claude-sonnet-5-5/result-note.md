# Hand-over note for the person filing

Nothing was filed or sent. `draft.md` is the issue body; its first line, `Title: ...`, is the title and is not part of the body.

## Before you file

1. **Check for a newer release and for changes to #412 and #977.** All observations are from 2026-09-23 on 2.3.1, and `main` was read at `5d2e8b1` on 2026-09-20. Today is 2026-10-31. If a release after 2.3.1 exists, re-run the `/healthz` check on it, or say in the issue that you saw this on 2.3.1 only.
2. **Redactions.** The captured output was edited in place and the issue says so. I replaced the node address `10.20.4.17` with `10.0.4.17` and the database host `pg-queue-01.corp.pellham.net` with `pg-01.corp.example.net`. I left out the organization's name, SECREV-2291, and the SEC-STD-014 number and quotes, and paraphrased the standard. Confirm you are happy with that, and check that the rest of the `/healthz` output (uptime, pool sizes, commit) is fine to publish.
3. **The tracker search was not repeated here.** The queries were `healthz auth`, `healthz version`, `probe port`, `liveness`, over issues and discussions, open and closed. The hits were #412, #977, and #1203 (readiness during leader election, unrelated, not cited). A search that finds nothing else is not proof that no duplicate exists, so try one or two more wordings, such as `unauthenticated health`, `separate listener`, and `livez`.
4. **The form.** `.github/ISSUE_TEMPLATE/feature_request.yml` was not available to me; the fields come from your notes. In the web form, paste the text under each `##` heading into the field of the same name and omit the headings. Then tick the required "I searched existing issues and discussions" box yourself. With `gh issue create` the form is not enforced and the headings stay in the body:

   ```bash
   gh issue create --repo tallyqueue/tallyqueue \
     --title "Can't require a token on every management endpoint and keep a Kubernetes liveness probe" \
     --body-file draft-body.md --label enhancement
   ```

   `draft-body.md` is `draft.md` without the `Title:` line. Applying a label may need triage permission; if `gh` refuses, drop `--label`.

## Not established

- **The design in the Proposal.** Not implemented, built, or tested. The remark about `internal/mgmt/server.go` comes from reading it. Your notes do not give the commit I read, so name one if a maintainer asks.
- **Whether `tallyqueuectl` is absent from the image.** Your notes state it and also say the exec probe was not tried. The issue says "I expect ... (not checked)". To check: `crane export <image> - | tar -t | grep tallyqueuectl`, with the image tag you deploy.
- **Whether `/ping` on 9400 fails when the management side is wedged.** I left it out of the issue because the `/ping` alternative fails on `/healthz` staying open either way. Say so if a maintainer asks.
- **Whether kubelet can reach a pod IP on 9402**, if the sketch is used. Not relevant to the request.

## Left out on purpose

- The external scanner report (missing HTTP security headers, version disclosure, no TLS on 9401). These are different asks. Including them would widen the request, which the non-goals line works against.
- The security-team chat thread about two advisories in other queue servers. It is speculation about this server, and `SECURITY.md` already says exposure through the management port is not treated as a vulnerability. The issue states only the exposure observed in the `/healthz` output.
- The tracker queries and the unrelated #1203, as above.

## Decisions for you

- **Opt-in.** I wrote the sketch so that the default does not change and said that a default change is out of scope. That is my assumption. If you want `/healthz` to require the token by default, the issue needs a different acceptance criterion and a compatibility argument, because the documentation promises the exception.
- **Comment or new issue.** I chose a new issue because #977 asks for something different (hiding content, not requiring authentication) and #412 is closed. You could instead comment on #977 and link it.
- **Pull request.** None is offered. If you or your team would write the patch, add one line saying so.
- **Quoting the standard.** The issue does not name SEC-STD-014 or the organization. If you are allowed to, naming them might make the constraint stronger; the issue does not depend on it.
- **Disclosure.** `CONTRIBUTING.md` has no AI policy, so the issue carries no disclosure line. You are the one who will answer follow-ups, and I could not verify the organizational facts in it (the review, the exception date, the standard's content); please check them against the source before filing.
