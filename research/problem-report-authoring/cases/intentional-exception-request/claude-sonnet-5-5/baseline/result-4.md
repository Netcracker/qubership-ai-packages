Title: No way to require a token on every management endpoint while keeping a Kubernetes liveness probe

Paste everything below this line into the form, one section per field.

---

### Problem

I run Tallyqueue 2.3.1 on Kubernetes 1.30 with three replicas, and I need every endpoint on the management port to require the bearer token. My organization's security review blocks the production rollout until that holds, and a temporary exception for it ends on 2026-12-31. I cannot get there: `GET /healthz` on port 9401 answers without a token, and the kubelet liveness probe (`httpGet` on port 9401, path `/healthz`, every 10 seconds) cannot send one.

The internal standard behind the review requires authentication on every listener that exposes administrative or diagnostic functions. It exempts a liveness endpoint only when the listener serves nothing else and the endpoint returns nothing beyond the status. `/healthz` sits on the management listener and returns more than a status.

Observed on 2026-09-23 against one pod of 2.3.1 (the latest release), with `management.auth.enabled = true` and the token in `management.auth.token_file`. The command is unchanged; `mgmt-paths.txt` lists the 23 paths below, one per line:

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

The unauthenticated body of `/healthz` from the same pod:

```text
$ curl -s http://10.0.0.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.corp.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

I replaced the pod IP and the PostgreSQL host name in the output above with stand-ins. No token or other secret was in it.

The exemption is deliberate, and I am not reporting it as a bug. `docs/operations/management.md` says: "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." The comment in `internal/mgmt/router.go` (v2.3.1, lines 41-43) says `/healthz` is left open because the liveness probe cannot carry a token, and points to #412.

**How we would know it works.** With the new option enabled, an unauthenticated request to any path on the management port, `/healthz` included, returns `401`. A kubelet `httpGet` probe with no headers succeeds against a listener that serves only a status response.

**Out of scope.** The default stays as it is, so existing probes keep working. The contents of the `/healthz` body (that is #977), TLS, and response headers are not part of this request.

### Proposal

One possible shape. I have not implemented, built, or tested it.

What I need is two things: a way to make `/healthz` on the management port require the token, and a status-only endpoint on a separate listener that a probe can reach. The setting name, the port, the path, and the body are the project's to choose.

A sketch: a setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token like every other endpoint. From reading `internal/mgmt/server.go`, the management listener is one `http.Server` started in `Start()`, so a second one looks feasible. That is a reading of the source and nothing more.

### Alternatives considered

- **Network policy limiting port 9401 to the node.** This is the maintainer's suggestion in #412. My standard says network restrictions do not substitute for authentication, so it does not satisfy the review. I did not try it.
- **A static token in the probe's `httpHeaders`.** The Kubernetes documentation ("Configure Liveness, Readiness and Startup Probes") says `httpHeaders` takes literal values, so the token would sit in the workload manifest. My standard forbids credentials there. I did not try it.
- **An `exec` probe running `tallyqueuectl ping`.** The image is distroless and has no `tallyqueuectl` binary. I did not try it.
- **Pointing the probe at `/ping` on the data port.** `/ping` on port 9400 answers `200` with `pong` and no token, but `/healthz` on port 9401 stays open whatever the probe targets, so the review still fails. Whether `/ping` fails when the management side is wedged, I have not established.

### Additional context

#412 (closed, fixed in 1.8.0) made `/healthz` open so the kubelet probe stops failing with `401`. This request keeps a probe-reachable endpoint and asks for the management port to be closeable as well.

#977 (open) asks to hide version and store details from `/healthz`, with no design agreed. It would shrink what the endpoint returns. It would leave `/healthz` reachable without a token on the management listener, which my standard does not allow. I know of no one else with this exact requirement; #977 is the closest sign that others dislike what `/healthz` returns.
