### Problem

We run Tallyqueue 2.3.1 (commit `9e41c07`, the latest release) on Kubernetes 1.30 with `management.auth.enabled = true` and a bearer token from `management.auth.token_file`. Our security rules require every endpoint on a listener that serves administrative or diagnostic functions to require authentication. The only exemption is a liveness or readiness endpoint served on a listener that serves nothing else and returns only the status. With these rules we cannot put Tallyqueue into production, because the management port always serves `/healthz` without a token, and there is no setting that changes this.

This is documented and intentional. `docs/operations/management.md` says all management endpoints require a token "except `/healthz`, which liveness probes use", and `internal/mgmt/router.go` has the same comment at v2.3.1 and on `main` at `5d2e8b1`, referring to #412. I am not asking to reverse #412: probes that cannot carry a token have to keep working. I am asking for an opt-in way to run the liveness check somewhere other than the management port, so that the management port can require the token on every path.

Observed on 2026-09-23 against our deployment, management port 9401, no token sent (`mgmt-paths.txt` holds the paths shown in the output; the address is changed):

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.0.17:9401$p")"; done
```

<details><summary>Output: every path answers 401 except <code>/healthz</code></summary>

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

</details>

`/healthz` also returns more than a status, so it does not qualify for the exemption even on its own (store host redacted):

```text
$ curl -s http://10.0.0.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"<redacted: internal hostname>:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

**Pointing the liveness probe at the data port does not fix it.** The data port has its own unauthenticated `GET /ping` (on port 9400 it answers `200` with the body `pong`), but moving the probe there leaves `/healthz` on the management port answering without a token, so the management port still fails the rule. I have also not established whether `/ping` fails when the management side is wedged, so I do not know whether it is a usable liveness signal.

As far as I know we are the only case with this exact rule. #412 shows the probe-versus-token conflict itself is not unique to us, and #977 (open, 6 reactions) asks to reduce what `/healthz` exposes.

**How we would know it works:** with the new setting enabled, `GET /healthz` on the management port without a token returns `401` like every other management path; a liveness endpoint on a separate listener returns `200` without a token while the server is healthy, returns no data beyond the status, and that listener serves nothing else (any other path returns `404`). With the setting unset, behavior is exactly as in 2.3.1.

**Out of scope:** changing the default (the #412 decision stays as it is), the content of `/healthz` itself (#977), and TLS or response headers on the management port.

### Proposal

One possible shape, not implemented, built, or tested:

```toml
management.probe_addr = "0.0.0.0:9402"
```

When set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token like every other endpoint. When unset, nothing changes.

What we need is the requirement in the acceptance paragraph above: a token-less liveness endpoint on a listener of its own that returns only the status, and a management port with no unauthenticated path. The setting name, the path, the body, whether a readiness endpoint joins it, and whether a Unix socket or something else serves better are the project's to choose.

### Alternatives considered

- **Network policy restricting port 9401**, as suggested in #412. Our rules state that network restrictions do not substitute for authentication, so this does not meet them.
- **A static token in the probe's `httpHeaders`.** The Kubernetes probe API takes literal header values and cannot read a Secret ([Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/), `httpHeaders`), so the token would sit in the workload manifest, which our rules forbid.
- **An `exec` probe running `tallyqueuectl ping`.** Not tried: the image we deploy is distroless and does not include `tallyqueuectl`.

### Additional context

Searched issues and discussions, open and closed, for `healthz auth`, `healthz version`, `probe port`, `liveness`. Nearest hits: #412 (closed, fixed in 1.8.0), where `/healthz` was made unauthenticated so kubelet probes work; this request keeps that working and adds an opt-in alternative. #977 (open) asks to hide version and store details from `/healthz`; that is related but would not make the management port fully authenticated, so it does not cover this. #1203 (readiness during leader election) is unrelated.

The IP address and the store hostname in the output above were changed or redacted; nothing else was edited.

- [x] I searched existing issues and discussions
