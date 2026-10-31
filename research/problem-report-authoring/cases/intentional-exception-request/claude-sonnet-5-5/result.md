Title: Can't require a token on every management endpoint and keep a Kubernetes liveness probe

## Problem

I want to run Tallyqueue 2.3.1 on Kubernetes 1.30 with a token required on every endpoint of the management port, and with a kubelet liveness probe that still works. I can't. With `management.auth.enabled = true`, `/healthz` on port 9401 still answers without a token, and a kubelet probe has no way to send one.

My organization's security review blocks the production rollout until every management endpoint requires authentication. A temporary exception runs until 2026-12-31. The organization's standard allows an unauthenticated liveness endpoint only on a listener that serves no other function and returns nothing beyond the status. Port 9401 also serves `/admin/*`, `/metrics`, and `/debug/pprof/`, and `/healthz` returns more than a status (see below).

Observed by me on 2026-09-23, on Tallyqueue 2.3.1 (the latest release), three replicas, data port 9400, management port 9401, bearer token from `management.auth.token_file`. Hostnames and addresses in the output below are replaced with placeholders; the output is otherwise as captured.

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.4.17:9401$p")"; done
```

`mgmt-paths.txt` holds the paths in the first column:

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

```text
$ curl -s http://10.0.4.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-01.corp.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

This is intentional. `docs/operations/management.md` says "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." The comment at `internal/mgmt/router.go` lines 41-43 in v2.3.1 refers to #412.

**Acceptance criterion:** on a deployment with `management.auth.enabled = true`, a liveness probe with no credentials passes against a listener that serves only the liveness check and returns only the status, and an unauthenticated request to any path on port 9401 returns `401`.

## Proposal

Everything in this section is one possible shape, not the requirement. What I need is a liveness check on a listener of its own, and `/healthz` on the management listener requiring the token like the other paths. The setting name, the path, and the port are the project's to choose.

A setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token. When it is not set, nothing changes.

From reading `internal/mgmt/server.go`, the management listener is one `http.Server` started in `Start()`, so a second one looks feasible. I have not implemented, built, or tested any of this.

Not part of this request: TLS, security headers, a change to the default, or what `/healthz` returns. #977 covers the last of these.

## Alternatives considered

- **Network policy restricting 9401 to the node.** The closing comment on #412 suggests it. My organization's standard says network restrictions do not substitute for authentication, so it does not clear the review.
- **A static token in the probe's `httpHeaders`.** The Kubernetes probe API takes literal header values and cannot read a Secret (Kubernetes docs, "Configure Liveness, Readiness and Startup Probes"). The token would sit in the workload manifest, which the standard forbids.
- **An `exec` probe running `tallyqueuectl ping`.** I have not tried it. The image is distroless, and I expect it not to include `tallyqueuectl` (not checked).
- **A probe on the data port's `/ping`.** `GET /ping` on 9400 returns `200` with `pong` without a token. `/healthz` on 9401 would still answer without one, so the listener would still fail the standard.

## Additional context

- #412 (closed, fixed in 1.8.0) reported that `/healthz` returned `401` with management auth enabled and the kubelet probe failed. The maintainer kept `/healthz` open. This request keeps an unauthenticated liveness check and moves it to a listener of its own, so the probe in #412 would still work.
- #977 (open) asks for an option to hide version and store details from `/healthz`. It would not satisfy the standard on its own, because `/healthz` would still be open on the management listener. If `/healthz` required a token, #977 would matter less on the management port.
- I know of no other party affected by this.
- The `main` branch at `5d2e8b1` (2026-09-20) has the same lines in `internal/mgmt/router.go`. I read them with `git show` and did not build or run that commit.
