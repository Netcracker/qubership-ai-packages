# Hand-over note: Tallyqueue feature request (not part of the issue body)

## How to file

- Form: `.github/ISSUE_TEMPLATE/feature_request.yml` (label `enhancement`). The body in `draft.md` uses the form's field labels as headings, in the form's order: Problem, Proposal, Alternatives considered, Additional context, then the required checkbox. In the web form, paste each section into its field and drop the headings.
- Suggested title: `No way to require a token on every management endpoint and keep a liveness probe`
- From the command line instead (form validation does not run there, and `--label` may need triage rights, so drop it if it fails):

  ```bash
  gh issue create --repo tallyqueue/tallyqueue \
    --title "No way to require a token on every management endpoint and keep a liveness probe" \
    --label enhancement \
    --body-file out/draft.md
  ```

## Lookups this session could not make (no network)

- **Search again before you tick the checkbox.** The search was run on 2026-09-23, more than five weeks ago. Re-run `healthz auth`, `healthz version`, `probe port`, and `liveness` over issues and discussions, open and closed, and add `probe listener`, `livez`, and `healthz token`. If a newer issue covers this, comment there instead.
- **Check for releases after 2.3.1** (https://github.com/tallyqueue/tallyqueue/releases) and the changelog. If a newer release adds a probe listener or auth on `/healthz`, the request may be moot.
- **Routing:** `.github/ISSUE_TEMPLATE/config.yml` was not read. Check whether its contact links send feature ideas to Discussions first.
- **Links:** the docs link points at tag `v2.3.1`. That tag name is assumed from the notes. Open the link and confirm the quoted sentence is on that page.
- **Kubernetes patch version:** only `1.30` is recorded. Add the patch version (`kubectl version`) if you have it.

## Facts the report states that you should confirm

- The `exec` probe bullet says the image ships no `tallyqueuectl`. The notes say so but do not say how it was checked. Confirm it, for example with `kubectl debug` or by listing the image, or delete that bullet.
- Transcripts come from this session's runs on 2026-09-23 against the production-candidate deployment. The report says "we" for those runs.

## Decisions for you

- **Quoting the internal standard.** The report quotes SEC-STD-014 §3.2, §3.4, and §4.1 verbatim but does not name the standard, SECREV-2291, or Pellham Transit. Confirm that the quotes may be published, and decide whether to name the organization.
- **Redaction.** The pod address `10.20.4.17` was replaced with `10.0.0.17`, and `pg-queue-01.corp.pellham.net` with `pg-queue-01.corp.example.net`. The real `/healthz` response does expose your internal database hostname on an unauthenticated port, which you may want to tell your security team.
- **AI disclosure.** `CONTRIBUTING.md` has no AI policy and the form has no checkbox, so nothing is required. Decide whether to say the draft was written with a tool. Either way, be ready to answer follow-up questions on the design yourself.
- **A comment on #977 instead?** The report links #977 and explains the difference, so I drafted a new issue. Adding a comment on #977 that links the new issue is optional.
- **Offering a patch.** The proposal is untested. From a reading of `internal/mgmt/server.go` (not built or run), the management listener is one `http.Server` started in `Start()`, so a second listener looks feasible. If you want to offer a PR, add one line at the end of the issue. Don't include the reading itself, since maintainers know their own code.

## Left out of the report on purpose

- **The exception deadline (2026-12-31).** It is your timeline, not the project's. Mention it only if a maintainer asks about urgency.
- **The external scanner findings for port 9401** (missing security headers, version disclosed, no TLS). These are separate requests. The version disclosure overlaps #977. File them separately if you want them.
- **The chat thread about advisories in other queue servers.** Those were health endpoints that leaked passwords. Our `/healthz` showed no credentials, so citing them would be speculative impact. `SECURITY.md` also says information exposed on the management port is not treated as a vulnerability.
- **Whether `/ping` fails when the management side is wedged.** Not established, and the request does not depend on it.
