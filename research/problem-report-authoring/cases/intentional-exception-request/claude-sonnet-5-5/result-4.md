<!-- Title: No way to run a Kubernetes liveness probe when every management endpoint must require a token -->
<!-- Label: enhancement -->

### Problem

I run Tallyqueue 2.3.1 (commit `9e41c07`, the latest release) on Kubernetes 1.30 with `management.auth.enabled = true`. My organization's security review will not approve a production rollout while any management endpoint answers without a token, and a temporary exception ends on 2026-12-31. The kubelet liveness probe (`httpGet` on port 9401, path `/healthz`, every 10 s) cannot send a token, and `/healthz` is the one path on the management port that answers without one.

On 2026-09-23 I requested 22 management paths on port 9401 without a token. Twenty-one returned `401` and `/healthz` returned `200`:

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.4.17:9401$p")"; done
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

The unauthenticated `/healthz` response also carries the version, the store driver, host, and database name, and the connection pool counts:

```text
$ curl -s http://10.0.4.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.corp.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

This is intended behavior. `docs/operations/management.md` says "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." The router comment says "Do not add auth here; see #412" (`internal/mgmt/router.go` lines 41-43 at v2.3.1, unchanged on `main` at `5d2e8b1`, which I read with `git show` and did not build or run).

Probing the data port's `/ping` (port 9400) instead does not help, because `/healthz` on port 9401 still answers without a token. Whether `/ping` fails when the management side is wedged is not established.

The request is done when, with `management.auth.enabled = true`, a request without a token to any path on the management port returns `401`, and a Kubernetes `httpGet` liveness probe without headers can succeed against an endpoint that sits on a listener serving no other path and returns only a status.

### Proposal

My organization's security standard (internal, so I can't link it) exempts a liveness endpoint from authentication only when it is served on a listener that exposes no other function and returns nothing beyond the status. I need Tallyqueue to offer such a listener and to stop answering `/healthz` on the management port without a token. The setting name, the address, the path, and the response body are the project's to choose.

One possible shape: a setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token like every other endpoint. From reading `internal/mgmt/server.go`, the management listener is one `http.Server` started in `Start()`, so a second one looks feasible. I have not implemented, built, or tested this.

### Alternatives considered

- A network policy that restricts port 9401 to the node, as the maintainer suggested in #412. The standard says network restrictions do not substitute for authentication.
- A static token in the probe's `httpHeaders`. The Kubernetes probe API takes literal header values and cannot read a Secret (Kubernetes documentation, "Configure Liveness, Readiness and Startup Probes"), so the token would sit in the workload manifest, which the standard forbids.
- An `exec` probe running `tallyqueuectl ping`. The image is distroless and ships no `tallyqueuectl`. I have not tried it.

### Additional context

- #412 (closed, fixed in 1.8.0) asked for `/healthz` to stop returning `401` when management auth is enabled, because the kubelet probe failed. The closing comment says "Probes can't carry the token, so /healthz stays open. If you need it closed, put the management port behind a network policy." This request keeps the probe working and moves it to a separate listener, so the management port can require a token on every path.
- #977 (open) asks for an option to hide version and store details from `/healthz`. Removing the details would not satisfy this request, because `/healthz` would still answer without a token on the listener that serves the management endpoints.
- I am not asking for TLS, security headers, or changes to what `/healthz` returns once it requires a token.

- [x] I searched existing issues and discussions

Hostnames and addresses in the output above were changed. I did not remove any secrets.
