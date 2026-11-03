Title: No way to run a liveness probe while every management endpoint requires a token

### Problem

I need to run Tallyqueue on Kubernetes with a liveness probe, and with every endpoint on the management port requiring the bearer token. Tallyqueue 2.3.1 does not allow both. With `management.auth.enabled = true`, `/healthz` on the management port answers without a token, as `docs/operations/management.md` documents: "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." #412 settled that `/healthz` stays open because probes cannot carry the token.

Our internal security standard blocks the production rollout until that last endpoint requires authentication. It says:

> Every network listener that exposes administrative or diagnostic functions MUST require authentication. Liveness and readiness endpoints MAY be exempt only when they are served on a listener that exposes no other function and return no data beyond the status.

`/healthz` fails both conditions of the exemption. I ran this against one replica on 2.3.1 with no `Authorization` header; `mgmt-paths.txt` holds the 23 paths in the first column:

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

```text
$ curl -s http://10.0.0.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.internal.example:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

Pointing the liveness probe at `/ping` on the data port (9400) does not solve this, because `/healthz` on 9401 still answers without a token.

I know of no other user who needs this. #977 (open) asks to hide the version and store details from `/healthz`. That would cover the second condition of the exemption and leave the first: `/healthz` would still be served on the management listener without a token.

The cost of leaving it as is: our production rollout is blocked, and the temporary exception we run under ends on December 31, 2026.

### Proposal

I have not implemented, built, or tested anything, and I have no patch.

What we need: a liveness endpoint that answers without a token on a listener that serves nothing else and returns no data beyond the status. With that endpoint enabled and `management.auth.enabled = true`, every endpoint on the management port, `/healthz` included, requires the token. The setting name, the port, the path, the response body, and what the probe checks are yours to choose.

One possible shape: a setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token like every other endpoint.

How to tell it works: with the new setting on, the loop above prints `401` for every path, `/healthz` included. A `GET` on the probe endpoint without a token returns `200` with a body that carries only the status, and any other path or method on the probe listener returns a non-2xx status.

Out of scope: the default. With the setting unset, `/healthz` keeps answering without a token, so existing probes keep working as #412 decided. What `/healthz` returns is #977's question, and this request does not depend on it.

### Alternatives considered

- A network policy that restricts port 9401, as suggested in #412. Our standard rules it out: "Network restrictions do not substitute for authentication."
- A static token in the probe's `httpHeaders`. The probe API takes literal header values and cannot read a Secret ([Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)), so the token would sit in the manifest. Our standard rules that out too: "Credentials MUST NOT appear in workload manifests."
- An `exec` probe running `tallyqueuectl ping`. The image we run is distroless and has no `tallyqueuectl`, so I did not try it.

### Additional context

- Tallyqueue 2.3.1 (commit `9e41c07`), the latest release when I ran the commands above on September 23, 2026; Kubernetes 1.30; three replicas. The liveness probe is an `httpGet` on port 9401, path `/healthz`, every 10 s.
- On `main` at `5d2e8b1` (September 20, 2026), `internal/mgmt/router.go` registers `/healthz` without authentication, as in v2.3.1. I read this with `git show` and did not build or run it.
- I replaced internal addresses and hostnames in the commands and output above.

- [x] I searched existing issues and discussions
