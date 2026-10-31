Title: Cannot require authentication on every management endpoint and still run a liveness probe

### Problem

We run Tallyqueue 2.3.1 (commit `9e41c07`) on Kubernetes 1.30 with `management.auth.enabled = true` and a kubelet liveness probe (`httpGet` on port 9401, path `/healthz`). Our security standard requires authentication on every listener that exposes administrative or diagnostic functions. It exempts a liveness endpoint only when that endpoint is served on a listener with no other function and returns nothing beyond the status. A network restriction does not count as authentication under the standard. We can't meet these rules and keep a liveness probe, so the standard blocks our production rollout.

With auth enabled, every management path we tried returns `401` without a token, except `/healthz`:

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.0.12:9401$p")"; done
```

```text
/admin/queues                401
/admin/config                401
/admin/tokens                401
/metrics                     401
/debug/pprof/                401
/healthz                     200
```

The output is trimmed: 17 more `/admin/...` paths in `mgmt-paths.txt` also returned `401`. This matches `docs/operations/management.md`: "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use."

`/healthz` also returns more than a status, on the same listener as `/admin/*`:

```text
$ curl -s http://10.0.0.12:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.corp.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

The pod IP and the store hostname in both outputs are changed.

### Proposal

What we need is an opt-in mode with three properties:

1. A liveness endpoint that needs no token, served on a listener that serves nothing else.
2. That endpoint returns only a status, with no version, commit, or store details.
3. With the mode enabled, `/healthz` on the management port requires the token like every other management endpoint.

How to check it: with the mode enabled and `management.auth.enabled = true`, a request without a token to `/healthz` on the management port returns `401`. A `GET` on the probe endpoint returns `200` with a body that carries only the status, and any other path on the probe listener returns `404`. A kubelet `httpGet` liveness probe against the probe listener passes.

With the mode off, nothing changes: `/healthz` stays open, as decided in #412.

One possible shape, which we have not implemented or tested; the names, the path, and the body are yours to choose. A setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token.

### Alternatives considered

- Restricting port 9401 with a network policy, as suggested in #412: our standard does not accept a network restriction in place of authentication.
- A static token in the probe's `httpHeaders`: the probe API takes literal header values and cannot read a Secret ([Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)), so the token would sit in the manifest. Our standard forbids credentials in workload manifests.
- An `exec` probe running `tallyqueuectl ping`: the image we run is distroless and does not include `tallyqueuectl`. We have not tried this.
- Pointing the probe at the data port's `/ping` (port 9400, returns `200` with the body `pong`): `/healthz` on 9401 still answers without a token, so the standard still fails.

### Additional context

- #977 asks to hide the version and store details from `/healthz`. That alone would not meet our requirement, because `/healthz` would still share a listener with `/admin/*`. This request does not depend on #977, and #977 does not depend on it.
- On `main` at `5d2e8b1` (2026-09-20), `internal/mgmt/router.go` still registers `/healthz` without auth. We read the source there; we did not build or run it.
- We know of no other users with this requirement.

- [x] I searched existing issues and discussions
