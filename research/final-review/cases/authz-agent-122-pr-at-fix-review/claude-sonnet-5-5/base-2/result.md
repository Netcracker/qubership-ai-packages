# Final review: `58316ca..HEAD` (4 commits)

**Inputs and caveats**
- I had no task statement. The claimed cases come from the four commit messages and the comments in the diff.
- `comment-drift.py 58316ca HEAD` printed nothing, although `main.go`, `main_test.go` and `helpers.go` changed. I treated its output as unreliable and read every changed comment by hand.
- No previous report exists.
- Skills loaded: `test-authoring`, `english-developer-style`. The repository has no `godoc-authoring` copy in the skills directory, so Go doc comments were read against the style skill only.
- Run locally: `go test` in `test/integration/pipstub` (passes). `helm lint` of the chart in a scratch copy, with hand-populated `files/`, passes for both values files. I rendered the e2e values with `helm template`; the Job renders as expected.
- Helm here is 4.3.0, and CI pins 4.3.1.

## Item 1: comments consistent with the code and with each other
- **Substantive.** `README.md:59` still reads "CI builds both via `.github/docker-dev-config.json` and publishes them". That file now lists five images. The sentence two lines below was updated; this one was not.
- **Substantive.** `Makefile:104` says `$(4)` is "no shorter than its `suite.activeDeadlineSeconds`", and `Makefile:49-50` says a longer suite "raises this together with `suite.activeDeadlineSeconds`". The suite args in `test/k8s/test-stand-values.yaml:46-52`, `values.yaml:76-82` and the parity values all carry `-test.timeout 600s`. A suite given a longer deadline still dies at 10 minutes, so the comment's recipe and the commit message's claim are both incomplete. See Item 3, limits.
- **Taste.** `pipstub/main.go:34-38` says "No request path is `*`". That is true only because an HTTP path starts with `/`. A caller can still register a route at a path like `/*`, which is not `*`, so the sentence holds.
- Otherwise none:
  - `main.go:29-38` matches the new lookup order: rules, then path route, then default route, then 404.
  - The `helpers.go` and `testify/Dockerfile` comments now point at `test-stand-values.yaml`, which exists.
  - No narrating words (`now`, `no longer`) in the comments I read.

## Item 2: claimed cases covered

| Claim (commit) | Test or evidence |
|---|---|
| Unrouted path gets the default route (9d25da7) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| Routed path keeps its own answer | `.../a routed path keeps its own answer` |
| Route with no responses falls through to the default | `.../a routed path with no responses gets the default answer` |
| No default route gives 404 as before | `.../an unrouted path without a default route is 404` |
| Empty default route gives 404 | `.../an unrouted path with an empty default route is 404` |
| Route with no responses and no default gives 404 | **no case**. The table has no row with `routedResponses: []` and a nil default. This is the original `-1` index panic path. |
| `/pip-stub/configure` takes `*` | **no test**. Routes are written straight into the map. The handler stores the path as given, so it works, but nothing exercises the wire path. |
| Default route sequence is shared across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` is recorded as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent`. The test reads the struct field. The JSON key `requestUri` is not asserted. |
| Restricted PSS: non-root, seccomp, drop ALL, no escalation, read-only root filesystem except Keycloak, `/tmp` emptyDir (17b17fc) | none. CI only runs `helm lint` (`integration-tests.yaml:83-84`). `test/scripts/test-chart-render.sh` has no assertion for the new chart. |
| `app.kubernetes.io/*` labels, `helm.sh/chart`, selectors stay `app: <name>` | none, same reason |
| Realm change restarts Keycloak (checksum annotation) | none |
| `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` set the wait (5dcb6be) | none. No run with a raised deadline. |
| README `kubectl logs job/<name>` after `helm test`; Helm 4.3.1 prints nothing; Helm 3.22.1 fails with "unable to get pod logs for parity-suite" | none. No cluster here, and no recorded run. |
| `make e2e-down` clears the "invalid ownership metadata" error | none. No upgrade-from-old-stand run is stated. |
| Transfer image carries three charts with `files/` generated | none. CI never builds the transfer image or installs from it. |
| `parity-mt-b` second tenant realm | exists in the generated files. Nothing in this change references it: no tenant-manager entry, no trusted provider, no test. |

**Commands the change tells someone to run**

| Command | Runs in CI or a make target |
|---|---|
| `make test-stand-files` | yes: the CI step and the `e2e-harness` and `parity-harness` prerequisites |
| `docker create ... true; docker cp authz-charts:/charts ./charts; docker rm` (`authz-test-stand/README.md`) | **none**. The property it depends on is a `FROM scratch` image with no `CMD`. `docker create` accepts `true` because it does not check the command exists. That is not verified here. |
| `helm upgrade --install authz-test-stand ./charts/authz-test-stand --set TAG=<version> -f my-test-stand-values.yaml` | none. The kind form differs: it installs from the checkout, with `IMAGE_PULL_POLICY` and local repositories. The documented edits (delete `TAG` and the repositories) are never run. |
| `helm test authz-test-stand --timeout 15m` then `kubectl logs job/parity-suite` | partial. `run-suite` runs `helm test` and streams with `kubectl logs -f`. |
| `make e2e-down` then `make e2e` (troubleshooting row) | none |
| `helm ... upgrade authz-test-stand ... --reuse-values --set suite.env.RUNTIME_SUITE_RUN=... --set-string suite.env.FULL_RUNTIME_SUITE=false` (`docs/local-integration-tests.md`) | **none**. Before this change the suite was applied as a Job manifest; now the same recipe edits Helm values. The outcome depends on `--reuse-values` with `upgrade`. For a chart with only a test hook, that creates a new revision and does not run the hook. That works, but `--set` of a key under the map `suite.env` with `--reuse-values` is not run anywhere. |

**Hunks no commit sentence claims**
- **Substantive.** `test/svt/common/compose/docker-compose.yml`: Keycloak `26.0` moves to `26.3.5@sha256:…`. No message mentions it, and the SVT compose file is otherwise untouched. The request is a sentence that claims it, with a run, or a separate change.
- **Substantive.** `test/k8s/parity/idp-seed/parity-realm.json`: +318 lines (new roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`, the `parity-level-claim` mapper, tenant-A users and clients). The commit says only "The parity realm gains a second tenant realm, parity-mt-b". Nothing in this change uses these additions. The request is a sentence for the additions plus the case that uses them, or a move to the change that adds the cases.
- **Taste.** The following carry no sentence of their own: the `.github/workflows/integration-tests.yaml` lint and `make test-stand-files` step, `.dockerignore`, `.gitignore`, and the `docker-release.yaml` comment edit. They follow from "chart" and the release sentence.

## Item 3: boundaries, partitions, and the negative control
- **Missing case.** Route with no responses and no default (see Item 2).
- **Negative control** for the default route is present: `without a default route is 404`.
- **Substantive, limits on the same work (the suite run).** I list the limits, each with the place that sets it:
  - `helm test --timeout`, now `E2E_SUITE_TIMEOUT` or `PARITY_SUITE_TIMEOUT` (Makefile, default 15m);
  - Job `activeDeadlineSeconds` (chart `values.yaml`, default 900);
  - Go `-test.timeout 600s` (the `suite.args` default and both harness values);
  - `kubectl wait --for=create ... --timeout=2m` and the 90×2s log poll (Makefile `run-suite`).
  
  The first two are not "derived": both default to 15m, so helm's timer starts before the Job exists and fires seconds before the Job's deadline. Raise only `activeDeadlineSeconds` and helm gives up at 15m. Raise the Makefile variable and the Job still stops at 900s. Raise both past 10m and `-test.timeout 600s` fires first, with a Go panic dump. The documented recipe (raise the variable plus the deadline) therefore has no effect past 10 minutes. The request is to derive `-test.timeout` and `--timeout` from `suite.activeDeadlineSeconds`, or to state the third limit, and to run a suite longer than 10 minutes.
- **Substantive, replaced mechanism (`e2e-suite`, `parity-suite`).**
  - Old: `kubectl wait --for=condition=Ready pod` for 3 minutes, then a log stream, then a 1-minute `Complete` wait.
  - New: `helm test` in the background, `wait --for=create` for 2 minutes, a poll of up to 3 minutes, then `logs -f`.
  - Fault met most often (`ErrImageNeverPull`, per the troubleshooting row). Old: fails after 3 minutes with a Pod-not-Ready error. New: `logs -f` errors, but that is not the exit status. The target exits with `wait $$helm_pid`, and helm waits up to `--timeout` (15 minutes) for the Job to finish or fail. Nothing in the target stops it earlier. A pull failure now reports after up to 15 minutes instead of 3, and the log is empty. No sentence accepts this.
  - The request is a run of that fault with its duration and output, and a bound on the helm wait.
- **Pre-existing state.** `5dcb6be` says an older `make e2e` cluster fails with "invalid ownership metadata" and names `make e2e-down` as the remedy. No run starts from that state. The user-visible values partition is below.
- **Substantive, values users already pass.** `E2E_HELM_ARGS` now reaches the test-stand install as well. The example `--set IMAGE_PULL_POLICY=Never` is harmless. The agent and stub charts also read `TAG` and `IMAGE_PULL_POLICY`, so `--set TAG=x` retags the stub images, which is intended. `-f` files that set `idp`, `suite` or `pipStub` for those charts would also be read here. Only `TAG` and `IMAGE_PULL_POLICY` appear in the other charts' `values.yaml`, so I found no collision, but nothing tests it. The request is the Makefile comment naming those two keys, or `--set`-free separation.
- Also note: Keycloak's `idp.imagePullPolicy` is separate from `IMAGE_PULL_POLICY`. `--set IMAGE_PULL_POLICY=Never` therefore leaves Keycloak on `IfNotPresent`. The `Makefile` comment says "Extra arguments for every chart install" without that distinction. This is taste.

## Item 3a: level, placement, and the environment
- **Substantive.** Chart behavior is observable in-process with `helm template`, with no cluster. CI runs only `helm lint`. `test/scripts/test-chart-render.sh` already exists and has no assertions for `authz-test-stand`. The request is render assertions for: security context on every Pod and container, the `/tmp` emptyDir, `readOnlyRootFilesystem: false` only for Keycloak, labels versus selectors, the checksum annotation, and parts off by default.
- The pipstub tests sit beside the existing ones and share `resetState`. None.
- `helm lint` in CI needs `make test-stand-files` and Docker, which the lint job now runs. The step is present (`integration-tests.yaml:76`). None.

## Item 4: names by content, not by position
- **Taste.** `test-stand-values.yaml` ("A second instance for the entitlements endpoint") and the docs ("a second stub instance as `entitlements-mock`") use an ordinal where the content name is available and already given in the same sentence. The ordinal is harmless there.
- Otherwise none. The test case names are by content.

## Item 5: the failure report
- None. `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` prints method, path, got and want. The sequence test prints both slices. The URI test prints both values. The `if len(calls) != 1` check prints the count.

## Item 6: what the writer says it verified
- None stated in any of the four messages: no red run on the base commit, no mutation verdict, no run of `make e2e` or `make parity` on kind. The reviewer did not supply it, per the skill. The pipstub tests pass on HEAD only.

## Item 7: siblings of the change
- **Substantive.** Set size: `README.md:59` counts "both" images (see Item 1). `test/k8s/README.md:56` ("Builds the two product images, pip-stub, …") and the `Makefile` comment ("the two stubs") are the old size and are still true of what they list.
- **Substantive.** The `test/k8s/README.md` file table lists `values.yaml` and `policy-admin-values.yaml` but not the parity `values.yaml` (pre-existing, unchanged).
- **Helper `handlePIP`/`routes`:** `git grep` shows callers only in `main.go` and its tests. The `defaultRoute` lookup applies to every unrouted request on every stub. The e2e `pip-stub` and `entitlements-mock` tests (`check_resource_test.go:278`, `entitlements_test.go:82`, `pip_admin_test.go:183`) configure explicit paths and none uses `*`, so the existing behavior stays. This is claimed and unchanged.
- **Twin paths:**
  - `parity-harness` uses the same `run-suite` as `e2e-suite`. Both get the timeout variable. Good.
  - The README log remedy names `kubectl logs job/<suite.name>`, but the troubleshooting row for "Need logs after a run" (`make e2e-logs`) and `make parity-logs` read the logs through the artifacts targets, which were not checked here.
  - The ownership-metadata remedy covers both namespaces, since `e2e-down` deletes the cluster. None.
- **Substantive.** The new test-stand `values.yaml` comment says "`test/k8s/test-stand-values.yaml` and `test/k8s/parity/test-stand-values.yaml`", and `README` step 2 starts from the parity file. A stand with the `e2e` realms (`idp.realms: e2e`) has no documented starting file. That is taste.

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | Longer `activeDeadlineSeconds` has no effect past 10 min: `-test.timeout 600s` fires first; the claim in `5dcb6be` is not demonstrated | substantive | `Makefile:49-52,104`, `helm-templates/authz-test-stand/values.yaml:76-82`, both harness values | Derive `-test.timeout` and `--timeout` from `suite.activeDeadlineSeconds`; run a suite longer than 10 min |
| 2 | Image-pull fault: old target failed in ~3 min, new target waits for helm up to 15 min with no log | substantive | `Makefile:105-113` (`run-suite`) | Run that fault; bound the helm wait; print what the old target printed |
| 3 | No render assertions for the new chart (PSS contexts, labels vs selectors, `/tmp`, checksum, defaults off); CI runs `helm lint` only | substantive | `.github/workflows/integration-tests.yaml:83-84`, `test/scripts/test-chart-render.sh` | Add `helm template` assertions |
| 4 | Missing pipstub case: routed path with empty responses and no default route (the original `-1` path) | substantive | `main_test.go` table | Add the case |
| 5 | `/pip-stub/configure` with path `*` and the JSON key `requestUri` are claimed and not exercised through the handler | substantive | `main_test.go` | One test that PUTs `[{"path":"*",...}]` and reads `/pip-stub/calls` |
| 6 | Unclaimed hunk: Keycloak image bump in the SVT compose file | substantive | `test/svt/common/compose/docker-compose.yml:3` | Claim it with a run, or move it out |
| 7 | Unclaimed hunk: `parity-realm.json` +318 lines and `parity-mt-b` unused by anything in the change | substantive | `test/k8s/parity/idp-seed/parity-realm.json`, `parity-mt-b-realm.json` | Add a sentence and the case that uses them, or move them |
| 8 | Stale count: "builds both" images | substantive | `README.md:59` | Say "builds the images it lists" |
| 9 | Commands with no run: transfer-image `docker create`/`docker cp`, documented install from the unpacked charts, `--reuse-values` subset recipe, `make e2e-down` remedy, Helm 3/4 log claims | substantive | `helm-templates/authz-test-stand/README.md`, `docs/local-integration-tests.md`, `test/k8s/README.md` | Run each on kind, or document the form that runs; build the transfer image in CI |
| 10 | No evidence the new tests can fail (no red run or mutation verdict) | substantive | commit messages | State the evidence |
| 11 | `E2E_HELM_ARGS` reaches the test stand; `TAG` and `IMAGE_PULL_POLICY` overlap with the other charts, and Keycloak ignores `IMAGE_PULL_POLICY` | taste | `Makefile:45-48` | Name the two keys in the comment |
| 12 | Ordinal "second instance" | taste | `test/k8s/test-stand-values.yaml` | Name by content |

**Not checked:** the full suites on kind and any Kubernetes behavior (no cluster), Helm 3 behavior, Docker builds of the transfer image, the Keycloak realm contents beyond the diff stats, and wording beyond sentences that read wrongly (the style pass was not done).
