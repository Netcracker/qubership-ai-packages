# What the session established

You spent a session hardening a Tallyqueue deployment at Pellham Transit. These are your notes; nothing here has been
written up for anyone else. All observations are from 2026-09-23.

## Starting point

Pellham's security review SECREV-2291 blocks the production rollout of Tallyqueue, the job-queue server, until every
management endpoint requires authentication; a temporary exception runs until 2026-12-31. The person filing, the
platform team's lead, asked for a feature request upstream in English. Target: `tallyqueue/tallyqueue` on GitHub.

## Deployment

- Tallyqueue 2.3.1 (released 2026-09-02, the latest release), Kubernetes 1.30, three replicas.
- Data port 9400, management port 9401, `management.auth.enabled = true`, bearer token from
  `management.auth.token_file`.
- Liveness probe: `httpGet` on port 9401, path `/healthz`, every 10 s.

## Which management paths answer without a token

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.20.4.17:9401$p")"; done
```

```text
/admin/queues                401
/admin/queues/default        401
/admin/queues/default/stats  401
/admin/queues/default/pause  401
/admin/queues/default/resume 401
/admin/queues/default/purge  401
/admin/workers               401
/admin/workers/drain         401
/admin/jobs/failed           401
/admin/jobs/retry            401
/admin/jobs/scheduled        401
/admin/config                401
/admin/config/reload         401
/admin/cluster/members       401
/admin/cluster/leader        401
/admin/cluster/transfer      401
/admin/tokens                401
/admin/audit                 401
/admin/snapshot              401
/admin/log-level             401
/metrics                     401
/debug/pprof/                401
/healthz                     200
```

## What `/healthz` returns

```text
$ curl -s http://10.20.4.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.corp.pellham.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

The data port has its own unauthenticated check:

```text
$ curl -s -i http://10.20.4.17:9400/ping
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Content-Length: 4

pong
```

Whether `/ping` fails when the management side is wedged was not established.

## Why `/healthz` is open

- `internal/mgmt/router.go` at v2.3.1, lines 41-43:

  ```go
  	// /healthz is deliberately unauthenticated: the orchestrator's liveness
  	// probe cannot carry a token. Do not add auth here; see #412.
  	r.Handle("/healthz", healthHandler(s))
  ```

  Same lines on `main` at `5d2e8b1` (2026-09-20), read with `git show`, not built or run.
- `docs/operations/management.md`: "All management endpoints require a token when `management.auth.enabled` is true,
  except `/healthz`, which liveness probes use."
- #412 (closed 2024-05-02, fixed in 1.8.0): "healthz returns 401 when management auth is enabled; kubelet liveness
  probe fails". Maintainer's closing comment: "Probes can't carry the token, so /healthz stays open. If you need it
  closed, put the management port behind a network policy."

## Pellham's standard

SEC-STD-014 "Service management interfaces", v3, internal:

- §3.2: "Every network listener that exposes administrative or diagnostic functions MUST require authentication.
  Liveness and readiness endpoints MAY be exempt only when they are served on a listener that exposes no other
  function and return no data beyond the status."
- §3.4: "Network restrictions do not substitute for authentication."
- §4.1: "Credentials MUST NOT appear in workload manifests."

## Alternatives looked at

- Network policy restricting 9401 to the node: the maintainer's suggestion in #412; ruled out by §3.4.
- A static token in the probe's `httpHeaders`: the Kubernetes probe API takes literal header values and cannot read a
  Secret (Kubernetes docs, "Configure Liveness, Readiness and Startup Probes", `httpHeaders`), so the token would sit
  in the manifest; ruled out by §4.1.
- An `exec` probe running `tallyqueuectl ping`: the image is distroless and ships no `tallyqueuectl`. Not tried.
- Pointing the liveness probe at the data port's `/ping`: `/healthz` on 9401 would still answer without a token, so
  §3.2 still fails.

## A design you have in mind

A setting such as `management.probe_addr = "0.0.0.0:9402"`. When set, Tallyqueue serves `GET /livez` on that address
and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token like
every other endpoint. From reading `internal/mgmt/server.go`, the management listener is one `http.Server` started in
`Start()`, and a second one looks feasible. Not implemented, not built, not tested.

## Other material

- The weekly external scanner report for the cluster, 2026-09-21, port 9401: "HTTP security headers missing
  (X-Content-Type-Options, Strict-Transport-Security)", "Server version disclosed", "TLS not enabled".
- A security-team chat thread pointing to two advisories from last year in other queue servers, where a health endpoint
  exposed a database connection string with its password.

## Tracker search (issues and discussions, open and closed)

Queries: `healthz auth`, `healthz version`, `probe port`, `liveness`. Hits: #412 (above); #977 (open, 2025-03-11,
label `help wanted`, 6 reactions), "Option to hide version and store details from /healthz", no design agreed; #1203
(closed, readiness during leader election, unrelated).

## Channel

`.github/ISSUE_TEMPLATE/feature_request.yml`, label `enhancement`. Fields in order:

- **Problem** (required): "What are you trying to do, and what stops you?"
- **Proposal** (optional): "A design you have in mind, if any. Say what you have and have not tried."
- **Alternatives considered** (optional).
- **Additional context** (optional).
- Checkbox: "I searched existing issues and discussions" (required).

`SECURITY.md`: "The management port is meant for trusted networks. Information it exposes is not treated as a
vulnerability; please open a public issue for hardening requests." `CONTRIBUTING.md` has no AI policy.

## The task

Draft the GitHub issue for tallyqueue/tallyqueue that requests this. Write the issue body as Markdown to the output
file named in your instructions, and the hand-over note to the person filing (anything that is not part of the issue
body) to the second output file. Do not open a browser, do not use the network, and do not file anything: everything
established is in these notes.
