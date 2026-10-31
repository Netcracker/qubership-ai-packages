Title: Liveness probing forces `/healthz` to stay open on an authenticated management port

### Problem

We run Tallyqueue 2.3.1 on Kubernetes 1.30 with `management.auth.enabled = true` and a kubelet liveness probe on `GET /healthz` on the management port (9401). We can't take this deployment to production. Our internal security standard requires a token on every endpoint of a listener that exposes administrative functions. It exempts a liveness endpoint only when that endpoint is served on a listener that exposes no other function and returns nothing beyond the status.

`/healthz` meets neither condition. It is the only path on the management port that answers without a token (`mgmt-paths.txt` holds the paths in the first column):

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.0.17:9401$p")"; done
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

Its response carries the version, the commit, and the store's driver, host, and database:

```text
$ curl -s http://10.0.0.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.corp.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

This matches `docs/operations/management.md` ("All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use.") and the decision in #412. The reason given there, that a probe can't carry a token, applies to us too. What we're missing is a liveness endpoint that needs no token and doesn't keep `/healthz` open on the management listener. Our rollout runs on a temporary exception that ends on December 31, 2026.

We'd know this is solved when, with an opt-in setting enabled:

- an unauthenticated `GET` to every path on the management port, `/healthz` included, returns `401`;
- an unauthenticated probe request returns `200` from a listener that serves nothing else, with a body that carries only the status.

With the setting off, `/healthz` behaves as it does in 2.3.1. We aren't asking to change that default.

### Proposal

One possible shape. We haven't implemented, built, or tested it.

A setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token like every other management endpoint.

What we need is the separate listener with a status-only response, and the token on `/healthz` when that listener is configured. The setting's name, the path, and the response body are yours to choose.

### Alternatives considered

- A network policy that limits port 9401 to the node, as suggested in #412. Our standard states that network restrictions don't substitute for authentication.
- A token in the probe's `httpHeaders`. The Kubernetes probe API takes literal header values and can't read a Secret (Kubernetes docs, "Configure Liveness, Readiness and Startup Probes"), so the token would sit in the manifest, which our standard forbids.
- An `exec` probe running `tallyqueuectl ping`. The image is distroless and doesn't ship `tallyqueuectl`.
- Pointing the probe at `/ping` on the data port (9400). `/healthz` on 9401 would still answer without a token.
- #977, which asks for an option to hide the version and store details from `/healthz`. That would cut the response down to the status, but `/healthz` would still be open on a listener that serves the admin endpoints.

### Additional context

The observations above are from September 23, 2026, on 2.3.1, the latest release at the time. `internal/mgmt/router.go` on `main` at `5d2e8b1` still registers `/healthz` without authentication; we read that from the source and didn't build or run it. The IP address and the store host name in the output were changed.

- [x] I searched existing issues and discussions
