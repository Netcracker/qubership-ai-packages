### Problem

I could not deploy Tallyqueue 2.3.1 (the latest release, commit `9e41c07`) on Kubernetes 1.30 with a liveness probe while every management endpoint requires a token. With `management.auth.enabled = true`, `/healthz` on the management port (9401) is the only path that answers without one. My organization's security review does not allow an unauthenticated endpoint on the management port, so the production rollout is blocked.

Observed on 2026-09-23. `mgmt-paths.txt` holds 23 paths, and I trimmed the output to four lines. The other 19 paths, all under `/admin/`, return `401`.

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.0.17:9401$p")"; done
```

```text
/admin/queues                401
/metrics                     401
/debug/pprof/                401
/healthz                     200
```

Without a token, `/healthz` also returns the version, the commit, the uptime, and the database driver, host, name, and pool usage:

```text
$ curl -s http://10.0.0.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.corp.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

The open `/healthz` is documented. `docs/operations/management.md` says: "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." Issue #412 (closed, fixed in 1.8.0) made it open on purpose, because the kubelet probe failed with `401`. The maintainer's closing comment there was: "Probes can't carry the token, so /healthz stays open. If you need it closed, put the management port behind a network policy." The first alternative below explains why a network policy does not work for me. I found no way to keep a probe and close `/healthz`, because the probe and the management endpoints share one listener.

**Acceptance criterion.** With a new opt-in setting enabled, the `curl` loop above prints `401` for every path including `/healthz`. A separate address then answers a probe request with `200` and a fixed body that contains no version, commit, or store details, and any other path on that address does not return `200`. Without the setting, behavior is unchanged.

**Who else is affected.** I know of no other party. Issue #977 shows interest in what `/healthz` exposes, but it asks for a different change (see Additional context).

**Out of scope.** I am not asking to change the default, to remove `/healthz`, or to add TLS or other hardening to the management port.

### Proposal

The requirement is a liveness endpoint that is served on its own listener, so that the management listener can require a token on every path. The setting name, the path, the body, and the port are the project's to choose.

One possible shape, which I have not implemented, built, or tested: a setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`, and `/healthz` on the management port requires the token like every other endpoint. From reading `internal/mgmt/server.go`, the management listener is a single `http.Server` started in `Start()`, so a second one looks feasible. This is a reading of the source only.

### Alternatives considered

- **Network policy restricting port 9401 to the node** (the suggestion in #412). Our security standard states that network restrictions do not substitute for authentication, so a policy cannot satisfy the review.
- **A static token in the probe's `httpHeaders`.** The Kubernetes probe API takes literal header values and cannot read them from a Secret ([Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/), `httpGet` `httpHeaders`), so the token would sit in the workload manifest, which our standard forbids.
- **Pointing the liveness probe at `/ping` on the data port (9400).** I saw `/ping` answer `200` with the body `pong`. This does not help, because `/healthz` on 9401 still answers without a token. I did not establish whether `/ping` fails when the management side is wedged.
- **An `exec` probe running `tallyqueuectl ping`.** Not tried: the image is distroless and ships no `tallyqueuectl`.

### Additional context

- On `main` at `5d2e8b1` (2026-09-20), `internal/mgmt/router.go` still registers `/healthz` without authentication. I read it with `git show` and did not build or run it.
- Issue #977 (open) asks for an option to hide the version and store details from `/healthz`. That would reduce what the endpoint returns, and the endpoint would still answer without a token, so it does not meet the acceptance criterion above.
- The address and the database host in the output above were changed. The output contains no tokens or credentials.

- [x] I searched existing issues and discussions
