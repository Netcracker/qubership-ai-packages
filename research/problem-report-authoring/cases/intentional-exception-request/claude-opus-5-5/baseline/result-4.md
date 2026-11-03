### Problem

We can't put Tallyqueue into production until every endpoint on the management port requires authentication, and our Kubernetes liveness probe still needs an endpoint it can call without a token. With `management.auth.enabled = true`, every management path we tried returns 401 without a token except `/healthz`. That one returns 200 with the version, the commit, and the store's host and connection pool usage.

Setup: Tallyqueue 2.3.1 (the latest release), Kubernetes 1.30, three replicas, data port 9400, management port 9401, token from `management.auth.token_file`. Observed on September 23, 2026. Internal hostnames and addresses in the output below were replaced; nothing else was changed.

`mgmt-paths.txt` holds one management path per line:

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.0.17:9401$p")"; done
```

Output trimmed to five of its 23 lines; the 18 other `/admin/*` paths also returned 401:

```text
/admin/queues                401
/admin/tokens                401
/metrics                     401
/debug/pprof/                401
/healthz                     200
```

```text
$ curl -s http://10.0.0.17:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.corp.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

This is the documented behavior. [`docs/operations/management.md`](https://github.com/tallyqueue/tallyqueue/blob/v2.3.1/docs/operations/management.md) says: "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." #412 left `/healthz` open because probes can't carry the token. That constraint holds for us too, and we aren't asking for the probe to send one.

Our organization's security standard for service management interfaces is what rules this setup out. Its §3.2 says:

> Every network listener that exposes administrative or diagnostic functions MUST require authentication. Liveness and readiness endpoints MAY be exempt only when they are served on a listener that exposes no other function and return no data beyond the status.

`/healthz` fails both conditions: port 9401 also serves the admin API, and the response carries more than the status. Our security review gave the rollout a temporary exception that ends on December 31, 2026.

I don't know of another deployment under the same rule. #977 (open, 6 reactions) asks to hide the version and store details from `/healthz`. That would meet the second condition but not the first, so it doesn't unblock us on its own.

### Proposal

What we need is a way to run Tallyqueue where both of these hold:

- The liveness probe has an endpoint that needs no token, on a listener that serves nothing else and returns only the status.
- Every path on the management port, `/healthz` included, requires the token.

The setting name, the port, the path, and the response body are yours to choose. The default can stay as it is for deployments that don't opt in.

One possible shape, not implemented, built, or tested: a setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves only `GET /livez` on that address and answers `200` with the body `ok`, and `/healthz` on the management port requires the token like every other management path.

How anyone could check it: with the option set and no token, `/healthz` on the management port returns 401, the probe endpoint returns 200 with only the status in its body, any other path on the probe address returns 404, and a kubelet `httpGet` liveness probe against the probe address passes.

Out of scope: TLS and security headers on the management port, and what `/healthz` returns when the option is not set (that part is #977).

### Alternatives considered

- **A network policy restricting port 9401**, as suggested in #412. Our standard's §3.4 says: "Network restrictions do not substitute for authentication."
- **The token in the probe's `httpHeaders`.** Probe headers are literal values and can't be read from a Secret ([Kubernetes docs, "Configure Liveness, Readiness and Startup Probes"](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)), so the token would sit in the manifest. Our standard's §4.1 says: "Credentials MUST NOT appear in workload manifests."
- **An `exec` probe running `tallyqueuectl ping`.** The image is distroless and ships no `tallyqueuectl`, so we didn't try this.
- **Pointing the liveness probe at `/ping` on the data port**, which answers without a token:

  ```text
  $ curl -s -i http://10.0.0.17:9400/ping
  HTTP/1.1 200 OK
  Content-Type: text/plain; charset=utf-8
  Content-Length: 4

  pong
  ```

  `/healthz` on port 9401 would still answer without a token, so §3.2 still fails. We also haven't established whether `/ping` fails when the management side is wedged.

### Additional context

`main` at `5d2e8b1` (September 20, 2026) still registers `/healthz` without authentication in `internal/mgmt/router.go`. I read the source there and did not build or run it.

- [x] I searched existing issues and discussions
