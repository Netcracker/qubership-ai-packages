### Problem

We run Tallyqueue 2.3.1 (the latest release) on Kubernetes 1.30 with three replicas, `management.auth.enabled = true`, and the bearer token read from `management.auth.token_file`. Our security review blocks the production rollout until every endpoint on the management port requires authentication. We can't get there, because the kubelet liveness probe needs `/healthz` on port 9401 to answer without a token, and a probe can't carry one.

With auth enabled, the management paths return 401 and `/healthz` returns 200 (observed on 2.3.1, 2026-09-23):

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://192.0.2.17:9401$p")"; done
```

```text
/admin/queues                401
/admin/config                401
/admin/tokens                401
/metrics                     401
/debug/pprof/                401
/healthz                     200
```

`mgmt-paths.txt` holds 23 paths. The listing is trimmed to six of them; the 17 omitted ones, all under `/admin/`, also return 401.

The unauthenticated response carries more than a status:

```text
$ curl -s http://192.0.2.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"db-primary.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

This is documented behavior, not a defect. `docs/operations/management.md` says: "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." Setting `management.auth.enabled = true` therefore does not close `/healthz`, and I found no other setting that does.

Our organization's security standard (internal, so I can't link it) allows a liveness endpoint to skip authentication only when it is served on a listener that exposes no other function and returns nothing beyond the status. It also says network restrictions do not replace authentication, and that credentials must not appear in workload manifests. The `/healthz` on the management port meets none of that.

This is done when, with `management.auth.enabled = true`, an unauthenticated request to every path on the management port returns 401, `/healthz` included, and a liveness probe that carries no credential in the manifest still passes on a healthy instance. The endpoint that probe uses serves no other function and returns only a status.

### Proposal

The requirement is a liveness endpoint that answers without a credential on its own listener, returns only a status, and leaves `/healthz` on the management port authenticated while the endpoint is in use. The setting name, the path, the body, and whether the existing `/healthz` behavior stays the default are the project's to choose. I am not asking for `/healthz` to require a token by default.

One possible shape: a setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token like every other endpoint. From reading `internal/mgmt/server.go`, the management listener is one `http.Server` started in `Start()`, so a second one looks feasible. I have not implemented, built, or tested this.

### Alternatives considered

- **Network policy limiting 9401 to the node.** This is the suggestion in #412. Our standard says network restrictions do not replace authentication, so it doesn't meet the requirement.
- **A static token in the probe's `httpHeaders`.** The Kubernetes probe API takes literal header values and cannot read a Secret (Kubernetes docs, "Configure Liveness, Readiness and Startup Probes", `httpHeaders`), so the token would sit in the manifest, which our standard forbids.
- **An `exec` probe running `tallyqueuectl ping`.** The image we run is distroless and has no `tallyqueuectl`, so I did not try it.
- **Pointing the probe at `/ping` on the data port.** `/ping` on 9400 returns `200` with the body `pong` without a token (observed 2026-09-23), but `/healthz` on 9401 still answers without one, so the management port stays open. I have not established whether `/ping` fails when the management side is wedged.

### Additional context

- #412 (closed, fixed in 1.8.0) is where `/healthz` was left open. Its closing comment says: "Probes can't carry the token, so /healthz stays open. If you need it closed, put the management port behind a network policy." What differs here is that our standard rules out the network policy, and I am asking for a separate probe listener rather than a token on `/healthz`.
- #977 (open) asks for an option to hide version and store details from `/healthz`. It would remove the data shown above. `/healthz` would still answer without a token on the listener that also serves `/admin/*`, so it does not meet the requirement here. The two changes can be made independently.

Names in the pasted output were changed: the IP address and the database host are example values.
