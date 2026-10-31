### Problem

We need every endpoint on the Tallyqueue management port to require the token, while the kubelet liveness probe, which cannot send one, keeps working. With `management.auth.enabled = true`, every management path we tested returns `401` without a token except `/healthz`. That endpoint returns `200` with the version, the commit, and the database host and name. Our production rollout is blocked until no management endpoint answers without a token.

This is documented behavior, so this is a feature request, not a bug report. [`docs/operations/management.md`](https://github.com/tallyqueue/tallyqueue/blob/v2.3.1/docs/operations/management.md) says: "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." #412 explains why: probes can't carry the token. We read `internal/mgmt/router.go` on `main` at `5d2e8b1` (read only, not built or run), and `/healthz` is still registered without authentication there.

The rule we have to meet, from our organization's internal standard for service management interfaces:

> Every network listener that exposes administrative or diagnostic functions MUST require authentication. Liveness and readiness endpoints MAY be exempt only when they are served on a listener that exposes no other function and return no data beyond the status.

Environment: Tallyqueue 2.3.1 (commit `9e41c07`), Kubernetes 1.30, three replicas. Data port 9400, management port 9401, token read from `management.auth.token_file`. The liveness probe is an `httpGet` on port 9401, path `/healthz`, every 10 s.

What we observed on 2026-09-23, with no token sent. `mgmt-paths.txt` lists the 23 management paths we know of. The output is trimmed: the 17 omitted lines also show `401`.

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.0.17:9401$p")"; done
```

```text
/admin/queues                401
/admin/config                401
/admin/tokens                401
/metrics                     401
/debug/pprof/                401
/healthz                     200
```

```text
$ curl -s http://10.0.0.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.corp.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

Pointing the liveness probe at `/ping` on the data port does not fix this: `/healthz` on port 9401 still answers without a token.

### Proposal

What we need: an opt-in setting that serves a liveness endpoint without a token on a listener of its own, and makes `/healthz` on the management port require the token like every other management endpoint. The listener has to be separate because our standard exempts a probe endpoint only on a listener that serves nothing else. The setting name, the path, the port, and the response body are yours to choose.

How we would check it, with the setting enabled and `management.auth.enabled = true`:

- `GET /healthz` on the management port without a token returns `401`.
- The liveness path on the new listener returns `200` without a token, and its body contains the status only: no version, commit, or store details.
- Any other path on the new listener is not served (for example, `404`).
- A kubelet `httpGet` liveness probe with no `httpHeaders` passes against the new listener.
- With the setting unset, `/healthz` behaves as in 2.3.1, so the probe setup from #412 keeps working.

One possible shape, which we have not implemented, built, or tested: a setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves only `GET /livez` on that address, answering `200` with the body `ok`, and `/healthz` on port 9401 requires the token.

Out of scope: the default behavior, the content of the `/healthz` response (#977), and `/ping` on the data port.

### Alternatives considered

- A NetworkPolicy that restricts port 9401 to the node, as suggested in #412. Our standard rules it out: "Network restrictions do not substitute for authentication."
- A static token in the probe's `httpHeaders`. The probe API takes literal header values and cannot read a Secret ([Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)), so the token would sit in the manifest. Our standard rules that out: "Credentials MUST NOT appear in workload manifests."
- An `exec` probe that runs `tallyqueuectl ping`. The distroless image we run ships no `tallyqueuectl`, so we have not tried it.

### Additional context

- #412 (closed, fixed in 1.8.0) made `/healthz` unauthenticated so probes work. This request keeps that default and adds an opt-in.
- #977 (open) asks to hide the version and store details from `/healthz`. That change would trim the response but still leave an unauthenticated endpoint on the management listener, so it does not meet the requirement above.
- We searched issues and discussions, open and closed, for `healthz auth`, `healthz version`, `probe port`, and `liveness`. Besides the two above, only #1203 matched, and it is unrelated.
- `SECURITY.md` asks for hardening requests on the management port to be filed as public issues, so this is one.
- In the output above, the host address and the database hostname are replaced. Nothing else was changed.

- [x] I searched existing issues and discussions
