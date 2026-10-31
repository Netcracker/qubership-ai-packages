### Problem

I need to run Tallyqueue where every management listener must require authentication, and still use a Kubernetes liveness probe. I can't do both. With `management.auth.enabled = true`, the only path on the management port that answers without a token is `/healthz`, and the kubelet probe can't send a token. My organization's security review treats that open path as a blocker for the production rollout.

Observed on 2026-09-23 with Tallyqueue 2.3.1 (commit `9e41c07`, the latest release that day) on Kubernetes 1.30, three replicas, data port 9400, management port 9401, token from `management.auth.token_file`. I ran this against one replica (the address is replaced, see the last paragraph):

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.0.5:9401$p")"; done
```

```text
/admin/config                401
/metrics                     401
/debug/pprof/                401
/healthz                     200
```

I trimmed this output to four lines. The other 19 paths in `mgmt-paths.txt` (`/admin/queues`, `/admin/tokens`, `/admin/config/reload`, and so on) also returned `401`.

`/healthz` returns more than a status:

```text
$ curl -s http://10.0.0.5:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.example.internal:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

The organization's standard allows an unauthenticated liveness endpoint only on a listener that serves no other function, and only if it returns nothing beyond the status. Port 9401 fails both conditions. The same standard states that network restrictions don't substitute for authentication, and that credentials must not appear in workload manifests.

The project documents the exemption and the reason for it. `docs/operations/management.md` says: "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." The comment in `internal/mgmt/router.go` (lines 41-43 at v2.3.1, and the same lines on `main` at `5d2e8b1`, which I read with `git show` and did not build or run) says: "/healthz is deliberately unauthenticated: the orchestrator's liveness probe cannot carry a token. Do not add auth here; see #412."

### Proposal

This is one possible shape. I have not implemented, built, or tested it.

A setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`. When it is set, `/healthz` on the management port requires the token like every other endpoint. When it is unset, behavior is unchanged. From reading `internal/mgmt/server.go`, the management listener is one `http.Server` started in `Start()`, so a second one looks feasible.

What I need is the requirement below. The setting name, the path, the body, and whether `/healthz` keeps its payload are the project's to choose.

- The liveness probe has an address that serves no management function and returns no data beyond the status.
- The management port can then require a token on every path.

**Acceptance criterion:** with the new setting enabled and `management.auth.enabled = true`, a kubelet `httpGet` probe with no headers succeeds against the probe address. Every request to the management port without a token, `/healthz` included, returns `401`.

**Out of scope:** changing the default, TLS, response headers, or the data port's `/ping`.

### Alternatives considered

- **Network policy limiting port 9401 to the node.** This is the maintainer's suggestion in #412. It doesn't meet the standard, which says network restrictions don't substitute for authentication.
- **A static token in the probe's `httpHeaders`.** The Kubernetes probe API takes literal header values and can't read a Secret (Kubernetes docs, "Configure Liveness, Readiness and Startup Probes", `httpHeaders`). The token would sit in the manifest, which the standard forbids.
- **An `exec` probe running `tallyqueuectl ping`.** The image is distroless and ships no `tallyqueuectl`, so this isn't possible without building a custom image. I did not try it.
- **Pointing the probe at `/ping` on the data port.** `http://<host>:9400/ping` returns `200` with body `pong` and no token. This leaves `/healthz` on 9401 answering without a token, so the standard is still not met. I did not establish whether `/ping` fails when the management side is wedged.

### Additional context

Nearest existing reports:

- #412 (closed, fixed in 1.8.0) made `/healthz` open because the probe failed with `401`. This request keeps that: a probe works without a token, on an address that exposes nothing else.
- #977 (open, `help wanted`, 6 reactions) asks for an option to hide version and store details from `/healthz`. That covers the "no data beyond status" condition and not the "listener with no other function" one. A probe-only listener would make the first condition simple to meet, since its body is fixed.

I know of no other user with this constraint. #977 suggests others dislike what `/healthz` returns, which is a different request.

I replaced the IP address, the database host name, and organization-specific names with placeholders of the same shape. The captured output above is otherwise as the tools printed it.
