Title: Cannot require a token on every management-port endpoint and still use a Kubernetes liveness probe

Label: `enhancement`

### Problem

I run Tallyqueue 2.3.1 on Kubernetes and need every endpoint on the management port to require authentication, including the one the liveness probe uses. I found no way to do that. A kubelet probe cannot send the bearer token, so `/healthz` has to stay open, and it sits on the same port as the `/admin/*` endpoints.

My organization's security standard (internal, so I can't link it) requires authentication on every listener that exposes administrative or diagnostic functions. It allows an unauthenticated liveness endpoint only on a listener that serves no other function and returns nothing beyond the status. Today `/healthz` fails both conditions, so our security review blocks the production rollout. A temporary exception expires on 2026-12-31.

Observed on 2026-09-23 against Tallyqueue 2.3.1 (commit `9e41c07`, the latest release), Kubernetes 1.30, three replicas, with `management.auth.enabled = true` and the token from `management.auth.token_file`. I ran this from a host in the cluster network, without a token:

```bash
for p in $(cat mgmt-paths.txt); do printf '%-28s %s\n' "$p" "$(curl -s -o /dev/null -w '%{http_code}' "http://10.0.0.5:9401$p")"; done
```

`mgmt-paths.txt` holds 23 paths, one per line. The 22 `/admin/*` paths, `/metrics`, and `/debug/pprof/` returned `401`. The last line of the output was:

```text
/healthz                     200
```

The response body of `/healthz` (redacted, see below) is:

```text
$ curl -s http://10.0.0.5:9401/healthz
{"status":"ok","version":"2.3.1","commit":"9e41c07","uptime_s":184233,"store":{"driver":"postgres","host":"pg-queue-01.corp.example.net:5432","db":"tallyqueue","pool_in_use":7,"pool_max":32},"workers":12}
```

The data port also has an unauthenticated check:

```text
$ curl -s -i http://10.0.0.5:9400/ping
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Content-Length: 4

pong
```

Pointing the liveness probe at `/ping` does not help, because `/healthz` on port 9401 keeps answering without a token. I did not try `/ping` as a probe, and I did not establish whether it fails when the management side is wedged.

This exemption is intentional. `docs/operations/management.md` says: "All management endpoints require a token when `management.auth.enabled` is true, except `/healthz`, which liveness probes use." The comment in `internal/mgmt/router.go` (lines 41-43 at v2.3.1, same lines on `main` at `5d2e8b1`, which I read with `git show` and did not build or run) says the probe cannot carry a token. I agree with that reasoning. This request is about where the exemption lives.

**Requirement.** When an operator opts in, the liveness endpoint is served on a listener that exposes nothing else and returns only a status, and the management port requires the token on `/healthz` like on every other endpoint.

**Acceptance criterion.** With that option set, an anonymous `GET /healthz` on the management port returns `401`, and the Kubernetes liveness probe succeeds against the new listener. A request to any other path on the new listener fails, and no response from it contains the version, the store details, or the uptime.

**Out of scope.** The default behavior (the option is off unless set), TLS and response headers on the management port, and what an authenticated `/healthz` returns.

### Proposal

One possible shape, not built or tested. I have not read enough of the code to know whether it is feasible. From reading `internal/mgmt/server.go`, the management listener is one `http.Server` started in `Start()`, and a second one looks feasible.

A setting such as `management.probe_addr = "0.0.0.0:9402"`. When it is set, Tallyqueue serves `GET /livez` on that address and nothing else, answering `200` with the body `ok`. `/healthz` on the management port then requires the token. The setting name, the path, and the body are the project's to choose. The requirement above is what I need.

### Alternatives considered

- **Network policy limiting port 9401 to the node.** This is the maintainer's suggestion in #412. The standard states that network restrictions do not substitute for authentication, so it does not pass our review.
- **A static token in the probe's `httpHeaders`.** The Kubernetes documentation ("Configure Liveness, Readiness and Startup Probes", `httpHeaders`) says the probe takes literal header values. A Secret cannot be referenced, so the token would sit in the workload manifest, which the standard forbids.
- **An `exec` probe running `tallyqueuectl ping`.** The 2.3.1 image is distroless and has no `tallyqueuectl`. I did not try this.

### Additional context

Nearest existing report: #977 (open, `help wanted`, 6 reactions), "Option to hide version and store details from /healthz", with no design agreed. It covers what `/healthz` returns. Even with that done, `/healthz` would stay on the authenticated management listener, which is the part this request changes. #412 (closed, fixed in 1.8.0) made `/healthz` unauthenticated on purpose, and this request keeps a probe endpoint that needs no token.

I searched issues and discussions, open and closed, for `healthz auth`, `healthz version`, `probe port`, and `liveness`.

I know of no one else with this exact constraint. #977 suggests other operators care about what the endpoint exposes.

Names were changed for this public tracker: the host, the IP address, and the store hostname are substitutes. The `/healthz` body is redacted evidence and was not re-run with them.

- [x] I searched existing issues and discussions
