# Hand-over note: tallyqueue/tallyqueue feature request

Proposed title: Cannot require authentication on every management endpoint and keep a Kubernetes liveness probe

## Filing

Nothing was filed. The issue form is `.github/ISSUE_TEMPLATE/feature_request.yml`; the body in `result.md` carries its fields as headings in the form's order, because `gh` does not use the form. File with:

```bash
gh issue create --repo tallyqueue/tallyqueue \
  --title "Cannot require authentication on every management endpoint and keep a Kubernetes liveness probe" \
  --label enhancement \
  --body-file result.md
```

`--label` fails without triage rights on the repository; drop it in that case, or file through the web form and paste each section into its field.

## Decisions for you

- **New issue or a comment on #977.** I drafted a new issue: #977 asks to hide data from `/healthz`, and your requirement is that no management path answers without a token, which #977 does not deliver. If you would rather add your case to #977, the Problem section is the comment.
- **How much of the internal standard to show publicly.** The body paraphrases SEC-STD-014 §3.2, §3.4, and §4.1 without naming the document, its ID, the security review SECREV-2291, or the company. Confirm that the paraphrase may be published, or cut it further.
- **The rollout deadline.** The body says the exception runs until December 31, 2026. Remove the sentence if you do not want the date public.
- **AI disclosure.** `CONTRIBUTING.md` has no AI policy and the form has no disclosure field, so nothing is required. Whether to mention that a tool drafted it is your call.

## What was changed or left out

- Names changed: the pod IP `10.20.4.17` is `10.0.0.17`, and the store hostname is `pg-queue-01.corp.example.net`. The data came from captured output and is not re-run with the new values.
- Left out: the external scanner report (missing headers, TLS, version disclosure) and the security-team chat about advisories in other queue servers. Neither is observed on Tallyqueue, and `SECURITY.md` says management-port information exposure is not treated as a vulnerability, so they add nothing to this request.
- Left out: the reading of `internal/mgmt/server.go` that a second `http.Server` looks feasible. It is unverified, and the maintainers know their own code.
- The trimmed path table: the full 23-line output is in your notes; `mgmt-paths.txt` itself is not in the issue.

## Not established

- **Tracker search.** The queries `healthz auth`, `healthz version`, `probe port`, and `liveness` were run in the earlier session (issues and discussions, open and closed; hits #412, #977, #1203). No network was used for this draft; re-run them before filing to catch anything opened since 2026-09-23.
- **`main` behavior.** `main` at `5d2e8b1` was read with `git show`, not built or run. To confirm: `git -C <tallyqueue clone> fetch && git show origin/main:internal/mgmt/router.go | sed -n '35,50p'`.
- **The Kubernetes docs link.** Written from the page title in your notes, not fetched. Open https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ and confirm the `httpHeaders` section says what the body claims.
- **An `exec` probe** running `tallyqueuectl ping` was not tried; the image is distroless. The body does not list it, because the third alternative covers every probe that moves away from `/healthz`. A maintainer may still ask; `kubectl exec <pod> -- tallyqueuectl ping` shows whether the binary exists.
- **`/ping` on the data port** was not checked for failing when the management side is wedged. The body does not rely on it.
