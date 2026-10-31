### Problem

We run Tallyqueue 2.3.1 (the latest release) on Kubernetes 1.30 with `management.auth.enabled = true`. We need every endpoint on the management port to require the token, and we need the kubelet's liveness probe to keep working. We can't have both: `/healthz` is the only management path that answers without a token, and our production rollout is blocked on it.

Requests without a token to each management path on one replica, on 2026-09-23 (`mgmt-paths.txt` holds the paths in the left column, one per line):

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.0.12:9401$p")"; done
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

This is documented: `docs/operations/management.md` says "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." Without a token, `/healthz` also returns the version, the commit, and the store's host and database (host redacted):

```text
$ curl -s http://10.0.0.12:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-01.example.internal:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

Our security standard requires authentication on every listener that exposes administrative or diagnostic functions. It exempts a liveness or readiness endpoint only when that endpoint is served on a listener with no other function and returns nothing beyond the status. The standard also states that network restrictions don't replace authentication, and that credentials must not appear in workload manifests. `/healthz` fails the exemption on both counts.

Pointing the liveness probe at `/ping` on the data port (9400) doesn't fix this: `/healthz` on 9401 still answers without a token.

Our security team granted a temporary exception that ends on 2026-12-31. We are the only case we know of that needs `/healthz` authenticated. #977 asks to hide the version and store details from `/healthz`. That would remove the data, but the endpoint would stay open on the management listener, which our standard still rejects.

### Proposal

What we need is an opt-in way to get both of these with management auth enabled:

- Every path on the management port, `/healthz` included, returns `401` without a token.
- A liveness endpoint that a Kubernetes `httpGet` probe can reach without credentials. It is served on a listener that serves nothing else, and it returns only the status.

The setting name, the path, the port, and the response body are yours to choose. One possible shape, which we haven't implemented or tested: a setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token like every other endpoint.

How to know it works: with the setting enabled and no token, `/healthz` on the management port returns `401`, the probe endpoint returns `200` with a body that carries no version, commit, or store details, and any other path on the probe listener returns no `2xx`.

Out of scope: the default behavior. With the setting unset, `/healthz` stays open as it is today, so the probes that #412 fixed keep working. Removing fields from `/healthz` is #977.

### Alternatives considered

- **Restrict port 9401 with a network policy.** This is the suggestion in the closing comment on #412 ("If you need it closed, put the management port behind a network policy."). Our standard doesn't accept a network restriction in place of authentication.
- **Send the token in the probe's `httpHeaders`.** The Kubernetes probe API takes literal header values and can't read a Secret (Kubernetes docs, "Configure Liveness, Readiness and Startup Probes", `httpHeaders`). The token would then sit in the manifest, which our standard forbids.
- **An `exec` probe running `tallyqueuectl ping`.** Our image is distroless and doesn't contain `tallyqueuectl`. We didn't try this.

### Additional context

- Deployment: three replicas, data port 9400, management port 9401, bearer token read from `management.auth.token_file`, liveness probe `httpGet` on port 9401, path `/healthz`, every 10 s.
- On `main` at `5d2e8b1`, `internal/mgmt/router.go` lines 41–43 still register `/healthz` with the comment "Do not add auth here; see #412." We read the source there and didn't build or run `main`.
- We replaced our internal IP address and database hostname with substitutes.

- [x] I searched existing issues and discussions
