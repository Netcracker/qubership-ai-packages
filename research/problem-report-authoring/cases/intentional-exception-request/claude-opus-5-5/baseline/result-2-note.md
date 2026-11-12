# Hand-over note: Tallyqueue probe-listener request

The issue body is in `draft.md`, written to the fields of `.github/ISSUE_TEMPLATE/feature_request.yml` in its order (Problem, Proposal, Alternatives considered, Additional context, then the search checkbox). Nothing was filed and no network was used. Everything in the body comes from the session of 2026-09-23.

## How to file

Proposed title:

> Cannot require a token on every management endpoint and keep a liveness probe

The web form applies the `enhancement` label and enforces the fields. With the CLI, the headings in `draft.md` stand in for the fields:

```bash
gh issue create --repo tallyqueue/tallyqueue \
  --title "Cannot require a token on every management endpoint and keep a liveness probe" \
  --label enhancement \
  --body-file draft.md
```

## Decisions for you before filing

- **Internal standard, paraphrased in public.** The body paraphrases SEC-STD-014 §3.2, §3.4, and §4.1 without naming the standard, Pellham, or SECREV-2291. Confirm that publishing the paraphrase is acceptable, or tell me to cut it down to "our security policy requires it".
- **The exception date.** The body states that the exception ends on 2026-12-31. It shows maintainers what the gap costs you. Remove it if you would rather not publish your rollout timeline.
- **Defending the report.** `CONTRIBUTING.md` has no AI policy, so nothing requires disclosure and nothing forbids an agent-drafted issue. Whether to say so anyway is your call. Either way, you will be answering the follow-up questions, so read the body as your own.
- **A patch.** The body doesn't offer one. If you plan to write it, add one line at the end saying so.
- **#977.** That issue is related but asks for something else, so the body cites it rather than commenting there. A short comment on #977 linking the new issue is optional.

## Gaps to close

- **The tracker search is from 2026-09-23.** Re-run it with closed items included, in issues and in discussions: `healthz auth`, `healthz version`, `probe port`, `liveness`, and add `probe listener`, `livez`, `management port auth`. Re-tick the checkbox only after you do.
- **Currency.** Confirm 2.3.1 is still the latest release and that `main` has not changed `/healthz`:
  `gh release list --repo tallyqueue/tallyqueue --limit 3` and
  `git fetch origin && git show origin/main:internal/mgmt/router.go | sed -n '35,50p'`.
  If it has changed, the body's "Additional context" line about `5d2e8b1` needs updating.
- **The `exec` probe claim.** The notes say the image is distroless and ships no `tallyqueuectl`, but no listing of the image is recorded. Check before filing, for example `crane export <image>@<digest> - | tar -t | grep tallyqueuectl`. If the binary is there, the alternative needs a different reason or should go.
- **`/ping` as a liveness signal.** It was not established whether `/ping` on 9400 fails when the management side is wedged. The body doesn't depend on it, because `/healthz` stays open either way. A maintainer may ask, though.
- **Link targets.** `docs/operations/management.md` and the Kubernetes probe page are cited by name. Add the links if you want them clickable, for example `https://github.com/tallyqueue/tallyqueue/blob/v2.3.1/docs/operations/management.md`, and check that the page still has the quoted sentence.

## Left out of the body on purpose

- **The `server.go` reading.** The notes say a second `http.Server` looks feasible. Nothing was built or run, and maintainers know their own code, so the body leaves the mechanism to them.
- **The external scanner findings for port 9401** (missing headers, version disclosed, no TLS). They're a different request, and none of them is the blocker here.
- **The chat thread about advisories in other queue servers.** Nothing similar was observed in Tallyqueue: `/healthz` shows a host and database name, not credentials. Mentioning those advisories would be speculating about impact.
- **Redaction.** `10.20.4.17` became `10.0.0.12`, and `pg-queue-01.corp.pellham.net` became `pg-01.example.internal`, the same everywhere in the body. The command and the output are otherwise verbatim. `mgmt-paths.txt` isn't attached. Its contents are the left column of the listing.
- **`SECURITY.md`** sends hardening requests about the management port to public issues, so a public issue is the right channel.
