Title: Cannot require a token on every management endpoint and still run a Kubernetes liveness probe

### Problem

I want to run Tallyqueue 2.3.1 on Kubernetes with a liveness probe and have every endpoint on the management port (9401) require the bearer token. The two cannot both hold. A kubelet `httpGet` probe cannot send the token, so it needs an endpoint that answers without one, and `/healthz` is that endpoint. It is exempt from `management.auth.enabled = true`, and `docs/operations/management.md` says so: "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use."

On 2026-09-23 I requested 23 management paths without a token, on a three-replica cluster (Tallyqueue 2.3.1, the latest release at that time; Kubernetes 1.30) with `management.auth.enabled = true` and the token read from `management.auth.token_file`. Twenty-two paths return `401`. `/healthz` returns `200`:

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://192.0.2.17:9401$p")"; done
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

The unauthenticated `/healthz` response includes the version, the commit, and the store connection details:

```text
$ curl -s http://192.0.2.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

(Both captures are redacted: the node address and the database hostname are placeholders.)

**Who is blocked and what it costs.** My organization's internal standard for service management interfaces requires authentication on every listener that exposes administrative or diagnostic functions. It allows a liveness endpoint to be exempt only if its listener serves nothing else and the response carries nothing beyond the status. `/healthz` fails both conditions. The standard also says that network restrictions do not replace authentication and that credentials must not appear in workload manifests. Our security review blocks the production rollout until every management endpoint requires a token, and a temporary exception ends on 2026-12-31. I know of no other affected user by name. Issue #977 asks to hide version and store details from `/healthz`; it is open with 6 reactions.

### Proposal

**What I need:** an opt-in way to give the liveness probe an endpoint on a listener that serves nothing else and returns only a status, and, when that is configured, to have `/healthz` on the management port require the token like the other endpoints. The default behavior stays as it is today.

**How we would know it worked:** with the option set, the loop above prints `401` for all 23 paths, including `/healthz`, and an unauthenticated `httpGet` probe against the new endpoint returns `200` with a body that contains no version, commit, or store details.

**Out of scope:** changing the default for existing deployments, and hiding details from `/healthz` for deployments that do not opt in (that is #977).

**One possible shape, untested:** a setting such as `management.probe_addr = "0.0.0.0:9402"`. When set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`. From reading `internal/mgmt/server.go`, the management listener is one `http.Server` started in `Start()`, so a second one looks feasible. I have not implemented, built, or run this. The setting name, the path, and the body are the project's to choose.

### Alternatives considered

- **Network policy limiting 9401 to the node.** This is the suggestion in #412. Our standard rules it out, because network restrictions do not replace authentication.
- **A static token in the probe's `httpGet.httpHeaders`.** The Kubernetes probe API takes literal header values and cannot read a Secret ("Configure Liveness, Readiness and Startup Probes", `httpHeaders`), so the token would sit in the workload manifest. Our standard rules that out.
- **An `exec` probe running `tallyqueuectl ping`.** The image I deploy is distroless and has no `tallyqueuectl` in it. I did not try this.
- **Pointing the probe at `/ping` on the data port (9400).** This does not change what `/healthz` on 9401 answers, so the loop above still prints `200` for it.

### Additional context

- #412 (closed 2024-05-02, fixed in 1.8.0), "healthz returns 401 when management auth is enabled; kubelet liveness probe fails", is why `/healthz` is open. The closing comment reads: "Probes can't carry the token, so /healthz stays open. If you need it closed, put the management port behind a network policy." `internal/mgmt/router.go` at v2.3.1 (lines 41-43) carries the same decision as a comment: "Do not add auth here; see #412". The lines are identical on `main` at `5d2e8b1` (2026-09-20); I read that with `git show` and did not build or run it. This request does not ask to add auth to the existing probe path. It asks for a way to move the probe elsewhere.
- #977 is the nearest open issue. It asks to hide version and store details from `/healthz`, with no design agreed. This request asks for a separate listener, and it would also let `/healthz` itself require the token.
- Names changed: the node address and the database hostname. No tokens or credentials appeared in any output.

- [x] I searched existing issues and discussions
