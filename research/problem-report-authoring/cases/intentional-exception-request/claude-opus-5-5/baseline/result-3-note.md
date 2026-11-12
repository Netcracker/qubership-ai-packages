# Hand-over note: feature request for tallyqueue/tallyqueue

This note is for you and is not part of the issue. `draft.md` is the issue body. Its first line is the title; remove that line before you paste the body.

## How to file

- **Web UI (recommended):** use the "Feature request" form (`feature_request.yml`, label `enhancement`). Paste each section of `draft.md` into the field with the same name, and tick the search checkbox.
- **CLI:** the form's fields are not enforced there, so the `###` headings in the draft stand in for them. Delete the title line from the file first, then run:

  ```bash
  gh issue create --repo tallyqueue/tallyqueue --label enhancement \
    --title "No way to run a liveness probe while every management endpoint requires a token" \
    --body-file draft.md
  ```

Nothing was filed or sent.

## Decisions for you

1. **New issue or a comment on #977.** #977 is open, labeled `help wanted`, and has 6 reactions, but no design has been agreed. It asks for less data from `/healthz`, and that alone does not meet SEC-STD-014 §3.2, because the listener also serves admin functions. I drafted a separate issue that links to #977. If you would rather add a comment there, I can cut the draft down to a comment.
2. **What you are willing to make public.** The draft quotes SEC-STD-014 §3.2, §3.4, and §4.1 word for word, without the document's name or number. It also gives the exception end date (December 31, 2026). It does not name Pellham, SECREV-2291, or SEC-STD-014. Check that quoting the standard publicly is allowed. If it is not, paraphrase the three clauses.
3. **Whether `/ping` on the data port would be enough.** If the security team would accept a liveness probe on 9400 `/ping` under §3.2, you only need an option that makes `/healthz` require the token, which is a smaller ask. The draft leaves this out, because §3.2 could be read either way and only the security team can decide. Separately, nobody checked whether `/ping` fails when the management side is wedged.
4. **Tool disclosure.** `CONTRIBUTING.md` has no AI policy and the form has no disclosure checkbox, so the draft says nothing about how it was written. Whether to mention it is up to you. Be ready to answer follow-up questions on the issue yourself.

## Checks to run before filing (session notes date from 2026-09-23)

- **Re-run the tracker search,** with open and closed issues and discussions included: `healthz auth`, `healthz version`, `probe port`, `liveness`. Look for anything new since September 23, and check whether #977 has moved.
- **Check for releases after 2.3.1:** open https://github.com/tallyqueue/tallyqueue/releases and read the changelog. If a newer release exists, re-run the curl loop against it and update the version in "Additional context".
- **Re-check `main`:** `git fetch && git show origin/main:internal/mgmt/router.go | sed -n '35,50p'`. Then update the commit and date in "Additional context".
- **Verify the Kubernetes docs link** in "Alternatives considered". It was written from memory, and the session only recorded the page title. Check that its `httpHeaders` section says that values are literal.
- **Confirm the image has no `tallyqueuectl`.** The notes state this, but nobody ran it. For example: `kubectl exec <tallyqueue-pod> -- tallyqueuectl ping`, which should fail with "executable file not found". Alternatively, list the image filesystem. If the binary is present, the `exec`-probe alternative needs a real reason or has to go.
- **curl version:** not recorded. Add it under "Additional context" if a maintainer asks.

## What I changed or left out

- **Substitutions:** the pod IP `10.20.4.17` became `10.0.0.17`, and the store host `pg-queue-01.corp.pellham.net` became `pg-queue-01.internal.example`. Each appears the same way in every place. The release commit `9e41c07` and the `main` commit `5d2e8b1` are public and kept as they are. `SECURITY.md` treats information exposed on the management port as a hardening matter for public issues, so a public issue is the right route. The `/healthz` output shows no credential.
- **Left out:**
  - The source reading of `internal/mgmt/server.go` ("a second listener looks feasible") is a guess about the project's code, and maintainers know their own code.
  - The security chat's two advisories from other queue servers describe a password leak that nothing here shows, so citing them would be speculative impact.
  - The weekly scanner findings for port 9401 (missing `X-Content-Type-Options` and `Strict-Transport-Security`, version disclosed, no TLS) are separate problems. Version disclosure overlaps #977. File them separately if you want them.
