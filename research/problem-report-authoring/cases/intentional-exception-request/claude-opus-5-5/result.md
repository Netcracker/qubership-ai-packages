### Problem

We run Tallyqueue 2.3.1 (commit `9e41c07`) on Kubernetes 1.30 with `management.auth.enabled = true`, and a kubelet liveness probe on `/healthz` of the management port. Our organization's security standard requires every management endpoint to require authentication. We cannot meet that and keep the liveness probe: `/healthz` is the one management path that answers without the token, and it has to, because a probe cannot send one.

With auth enabled, every other management path returns 401 and `/healthz` returns 200. Observed on 2026-09-23; output trimmed to the lines below, the other 16 paths under `/admin/` also return 401:

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.0.17:9401$p")"; done
```

```text
/admin/queues                401
/admin/queues/default        401
/admin/config/reload         401
/admin/tokens                401
/metrics                     401
/debug/pprof/                401
/healthz                     200
```

This is documented and intended. `docs/operations/management.md` says: "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." #412 made `/healthz` unauthenticated in 1.8.0 so that probes work, and `main` at `5d2e8b1` still exempts it. We are not asking to change that default.

Our standard exempts a liveness or readiness endpoint from authentication only when it is served on a listener with no other function and returns nothing beyond the status. It also says that a network restriction does not replace authentication, and that credentials must not appear in workload manifests. `/healthz` fails the exemption on both counts: it shares the listener with the admin API, and it returns more than the status (store hostname replaced):

```text
$ curl -s http://10.0.0.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.corp.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

Our security review blocks the production rollout until this is met; a temporary exception runs until December 31, 2026. We are the only case we know of with this requirement. #977 asks to hide the version and store details from `/healthz`. That would shrink the response, but `/healthz` would still answer without a token on the management listener, so #977 alone does not meet the requirement.

**How we would know it works**, with the new option set and `management.auth.enabled = true`:

- `GET /healthz` on the management port without a token returns 401, like every other management path.
- A separate listener answers a liveness `GET` without a token with 200 and a body that carries only the status.
- That listener serves no other path.

With the option unset, behavior stays as it is, so the case #412 fixed keeps working.

**Out of scope:** the default behavior of `/healthz`, what `/healthz` returns to an authenticated caller (#977), and the data port.

### Proposal

One possible shape; the names are yours to choose. A setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token like every other endpoint.

What we need is the behavior in the list above: an unauthenticated liveness check on a listener of its own that returns only the status, and no unauthenticated path on the management port. The setting name, the path, the body, and whether readiness gets the same treatment are the project's decision. We have not implemented, built, or tested this.

### Alternatives considered

- **A network policy that restricts port 9401**, as suggested in #412. Our standard does not accept a network restriction in place of authentication.
- **A static token in the probe's `httpHeaders`.** The probe API takes literal header values and cannot read a Secret ([Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)), so the token would sit in the manifest, which our standard forbids.
- **Pointing the liveness probe somewhere else**, such as `/ping` on the data port. The probe moves, but `/healthz` on port 9401 still answers without a token, so the management port still has an unauthenticated path.

### Additional context

_No response_

### Checklist

- [x] I searched existing issues and discussions
