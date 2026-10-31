# Hand-over note: Tallyqueue probe-listener request

The issue body is in `draft.md`. Its first line is the title, and the rest follows the fields of `.github/ISSUE_TEMPLATE/feature_request.yml` in order: Problem, Proposal, Alternatives considered, Additional context, and the search checkbox. Nothing has been filed.

## Filing

- Web UI: pick the feature request form, paste each section into the field with the same label, and tick the checkbox.
- CLI: drop the `Title:` line from the file first. `gh` does not enforce the form's fields, so the `###` headings stand in for them.

  ```bash
  gh issue create --repo tallyqueue/tallyqueue \
    --title "Cannot require authentication on every management endpoint and still run a liveness probe" \
    --label enhancement \
    --body-file draft.md
  ```

## Re-check before filing (all observations are from 2026-09-23)

- **Latest release.** 2.3.1 was the latest release on 2026-09-23. Check https://github.com/tallyqueue/tallyqueue/releases and the changelog for anything newer that adds a probe listener or changes `/healthz`. If a release does, re-run the curl loop against it and update the version in the Problem field.
- **Tracker search.** Re-run the queries, covering issues and discussions, open and closed: `healthz auth`, `healthz version`, `probe port`, `liveness`. Also try `livez` and `probe_addr`. Check #977 for a design that has been agreed since.
- **Routing.** The notes don't say whether `.github/ISSUE_TEMPLATE/config.yml` sends feature requests to Discussions. Open the "New issue" page and check the contact links.
- **`tallyqueuectl` in the image.** The issue says the image does not include `tallyqueuectl`, but the notes don't record how that was established. Confirm it, for example with `kubectl debug` and an ephemeral container that lists the image's filesystem, or by reading the image's build file. If it can't be confirmed, drop that bullet.

## Decisions for you

- **New issue or a comment on #977.** I wrote a new issue because #977 asks only to strip details from `/healthz`, and that would not meet the standard. If you'd rather keep the discussion in one place, the Proposal section could go on #977 as a comment instead.
- **What to say about Pellham.** The issue says "our security standard" and paraphrases §3.2, §3.4, and §4.1 of SEC-STD-014. It does not name Pellham, the document ID, review SECREV-2291, or the exception that expires on December 31, 2026. Add any of these only if you're cleared to publish them. Quoting the standard word for word is the same decision.
- **Offering a patch.** The notes say a second `http.Server` in `Start()` (`internal/mgmt/server.go`) looks feasible, but that comes from reading the code, not from building anything. I left it out. If you want to offer a pull request, add one line at the end of the issue.
- **Defending it.** `CONTRIBUTING.md` has no AI policy, so the issue carries no disclosure. You should still be able to answer follow-up questions without the tool.

## Changed or left out

- **Substituted.** The pod IP `10.20.4.17` became `10.0.0.12`, and `pg-queue-01.corp.pellham.net` became `pg-queue-01.corp.example.net`. The issue says both were changed.
- **Trimmed.** The path listing shows 6 of its 23 lines and says so. `mgmt-paths.txt` is not attached. If you want the full listing in the issue, it's in the session notes.
- **The scanner report** from 2026-09-21 (missing security headers, server version disclosed, no TLS on 9401) is about other problems. If you want those raised, they belong in separate hardening issues, which `SECURITY.md` says go to the public tracker.
- **The chat thread about advisories** in other queue servers: nobody saw this issue in Tallyqueue, and `/healthz` here shows no credentials, so mentioning it would be speculative impact.
- **Not established:** whether the data port's `/ping` fails when the management side is wedged. The issue doesn't depend on it. If you want it settled, block the management listener in a test pod and probe `/ping` on port 9400.
