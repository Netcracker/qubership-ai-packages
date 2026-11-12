Clean — no files were touched during investigation. Here's the test plan.

---

**The move owes tests, except where it doesn't**

The pip-stub default-route change already carries small tests in this commit (`TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, `...ServesItsSequenceAcrossPaths`, `...RecordsTheRequestTargetAsSent`) — partitioned, red-on-base-commit-able, no action needed there.

What the commit doesn't cover is the move itself: the new chart `helm-templates/authz-test-stand`, the generated-files pipeline behind it, and the rewritten wait/retry logic in `e2e-suite`/`parity-suite`. All three are new or changed behavior, and none is exercised anywhere in the diff. I verified every test below actually runs here, with neither Docker nor a cluster — `helm`, `jq`, and `go` are all present, and that's all any of this needs.

**1. Chart-render assertions — small, `helm template`, extend `test/scripts/test-chart-render.sh`**

This is the existing small-level home for chart behavior (no cluster, runs in the `chart` CI job); the new chart is a new unit in it, not a new file. Its `.Files.Glob`/`.Files.Get` calls read the real filesystem, so the fixture can't be injected with `--set` — copy the chart to a temp dir (as the file already does for `SIZING`) and drop minimal synthetic realm/pip-stub files under `files/`. I confirmed this renders correctly with a one-line fixture realm and no Docker build. Per part, from a chart copy with such a fixture, asserting on the rendered YAML:

- *idp*: disabled by default (no Keycloak objects in a bare install) → catches a part that isn't actually opt-in. Missing `files/realms/<realms>/*.json` fails at render time naming the remedy ``run `make test-stand-files` ``→ catches the guard message rotting. The realms ConfigMap carries every file the glob returns, one key per file. `checksum/realms` changes when a realm file's content changes and stays put when something unrelated changes → catches the restart-on-change trigger silently breaking.
- *pip-stub*: zero instances by default → no Deployment. Two instances render two independent Deployments/Services, each on its own port, keyed by name → catches instance keys colliding. `config` omitted renders no ConfigMap/volume; set, it does, and `PIP_STUB_CONFIG` points at it. Missing `port` is refused naming `pipStub.instances.<name>.port is required`.
- *tenant-manager*: disabled by default. Empty `tenants` is refused naming `tenantManager.tenants is required`. `TENANT_MANAGER_TENANTS` renders as the exact `name=id,...` join for ≥2 tenants (map iteration is key-sorted in Helm, so the literal string is a safe assertion).
- *client-credentials*: disabled by default (no Secret). Enabled without `username`/`password` is refused naming each.
- *suite*: disabled by default. Enabled renders the Job with `helm.sh/hook: test`, `backoffLimit: 0`; `env` entries render as plain values, `secretEnv` as `secretKeyRef`; `serviceAccount: true` adds the SA with `automountServiceAccountToken: false ` both there and on the Job, `false` adds neither. The `/tmp` `emptyDir`'s `sizeLimit` follows `suite.resources.limits.ephemeral-storage` when set and falls back to `256Mi` when the limits block omits that key (two partitions of the `dig` call) → catches a typo'd key silently losing the cap.
- *PSS, across every part, on one render with everything enabled*: every container's `securityContext` carries `allowPrivilegeEscalation: false` and `capabilities: drop: [ALL]`; every Pod's carries `runAsNonRoot: true` and `seccompProfile: RuntimeDefault`; `readOnlyRootFilesystem` is `false` for Keycloak alone and `true` for every other container (I rendered this exact shape: 4 containers, 1 `false`, 3 `true`). This is the one check that would catch a future part added to the chart without wiring the shared security-context helpers — the current templates all call them, but nothing fails if a new template skips them.
- Labels: one object (e.g. the `idp` Deployment) carries the full `app.kubernetes.io/*` + `helm.sh/chart` set, and every object's selector still matches on bare `app: <name>` alone, as the helper promises.

**2. `profile.jq` and the realm-merge pipeline — small, `jq` directly, new `test/scripts/test-profile-jq.sh`**

This logic has never run against a non-empty `test/parity/suite/testdata/realm/` (the commit message says "none so far"), so the merge and both duplicate guards are currently dead code in every CI run. I ran `profile.jq` directly (no Docker) against the commit's own documented example and it's correct:

- `profile()` partitions on the username's hyphen-separated parts: a part matching `^[a-z][0-9]+$` (`r29`) upper-cases whole; the literal `m2m` upper-cases whole; an ordinary word (`level`) capitalizes only its first letter. Case: `parity-r29-level-m2m` → `firstName: Parity`, `lastName: R29LevelM2M`, `email: parity-r29-level-m2m@example.test` (the literal from the Dockerfile's own comment, not pasted from a run).
- Control: a user that already sets `firstName`/`lastName`/`email` passes through unchanged (`//=` only fills nulls) — this is the case that shows the merge doesn't clobber a user file that opts to self-describe.
- The merge pipeline (`jq --slurp '.[0].users += (...) | .[0]'`) run on a base realm with zero and with one synthetic user file: zero files reproduces today's actual shipped behavior (base realm unchanged — worth pinning explicitly, since it's the only partition exercised today); one file merges it in with `profile()` applied.
- Both `jq -e` duplicate guards (`username`, `id`), each with a case that has two files sharing a username (or, with distinct usernames, sharing an `id`) and must fail (non-zero exit, matching the Dockerfile's `&&` chain aborting the build), and a control with distinct values that must pass.

**3. The replaced `run-suite` wait/retry mechanism — small, faked `kubectl`/`helm`/`sleep` on `PATH`**

This is the one piece I'd flag as a judgment call rather than hand you a ready script for. §3 of the test-authoring skill says a mechanism that's replaced (the old `kubectl wait --for=condition=Ready` / `logs -f` / `wait --for=condition=Complete` became `helm test` backgrounded + `wait --for=create` + a 90×2s log-readability poll + `logs -f` + `wait $helm_pid`) owes a run of the fault the old one met most often and the fault on which the new one's own loop waits longest. Both are reachable without a cluster by extracting the `run-suite` `define` into something callable on its own and putting fake `kubectl`/`helm` scripts earlier on `PATH` — and faking `sleep` as a no-op too, so the 90×2s path doesn't cost three real minutes per test run. Worth doing, but it's more invasive to set up than 1 and 2, and I'd want your read on whether it's worth the coupling to the macro's exact shape before I write it — happy to do it if you want it in this pass.

**Stays where it is:** the full install-on-kind path (`kind-e2e`, `kind-parity` CI jobs) is the large-level test for all of this and already exists; it doesn't need a new test, but given how much of the harness this commit rewrites, it's worth you re-running it once before merging, since nothing here can.
