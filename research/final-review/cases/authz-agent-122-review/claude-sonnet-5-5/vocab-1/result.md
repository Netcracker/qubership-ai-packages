# Final review: `58316ca..HEAD` (commits `8b85515`, `9d25da7`, `17b17fc`)

**Inputs.** There is no separate task statement, so the claimed cases come from the three commit messages alone. The class comments of the tests were read too. I loaded `test-authoring` and `english-developer-style` from the given skills directory. The change has no JVM code, so I used no doc-comment skill. The Go doc comments were read against the same item 1 questions.

**Drift script.** I ran `comment-drift.py 58316ca HEAD`. It exited 0 and printed nothing, because it parses only Java, Kotlin, Groovy and Scala files. This change is Go, YAML, Makefile, Dockerfile and Markdown. I read every changed comment by hand instead.

**Checks I ran.**
- `go test` in `test/integration/pipstub` passes.
- I copied the chart to the scratchpad and filled `files/` by hand from the sources, because there is no docker build here. `helm lint` passes for both values files, and `helm template` renders for both.
- The render matches the security-context claims. `runAsNonRoot` is set on every Deployment and Job, `readOnlyRootFilesystem` is `true` on all containers except Keycloak, and no `runAsUser` is set.
- The `jq` profile function gives `R29LevelM2M` and `parity-r29-level-m2m@example.test` for the example in the Dockerfile. It also works when `testdata/realm/` holds no JSON file.
- The `checksum/realms` annotation changes when a realm file changes.

## Item 1: Comments consistent with the code and with each other

Three findings.

1. **`test/integration/pipstub/main.go:19-21` against `:34-37`.** The file header still says routes are "served sequentially per path (clamped to the last)". The new paragraph says the default route answers "in sequence like any other route". The code keys the counter on `*`, so all unrouted paths share one sequence. The test `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` confirms this: it expects 503, 200, 200 for `/a`, `/b`, `/a`. A reader of the new paragraph would assume the sequence is per path. Request: replace "like any other route" with "one sequence shared by all unrouted paths, clamped to the last response". Substantive.
2. **`main.go:73-75`, the `RequestURI` comment.** "so that a caller that encodes a value in the path differently from one that does not can be told apart" needs two passes, because of the stacked relative clause and the elided verb. Request: "so that a test can see whether a client percent-encoded a value in the path". Substantive (`english-developer-style` §4, "Stacked relative" row).
3. **`main.go:34`.** "A stub nobody configures with it" is a stacked relative with its pronoun dropped, and "it" has no antecedent nearby. Request: "A stub that no one configured with `*` answers an unrouted request 404, as it did before the default route existed." Substantive. This is the same shape as finding 2, so I list it with that one.

Other results for this item:
- No comment narrates the change with "now", "no longer" or "used to".
- "Default route" is defined once, in the package comment, before other comments use it, so it is not a coinage.
- The stale `runtime-suite-job.yaml` references in `testify/Dockerfile` and `helpers.go` were updated.
- No file still names the deleted manifests (`git grep`).

## Item 2: Claimed cases covered

| Claimed case | Test |
| --- | --- |
| An unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| A routed path keeps its own answer | `.../a routed path keeps its own answer` |
| "A route with no responses falls through to the default route" | `.../a routed path with no responses gets the default answer` |
| "A stub nobody configures with `*` answers 404 as before" | `.../an unrouted path without a default route is 404` |
| An empty default route answers 404 | `.../an unrouted path with an empty default route is 404` |
| The default route serves a sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| "A route with no responses falls through to … 404" | **No test** |
| "/pip-stub/configure now takes the path `*`" | **No test** (the tests set `routes[defaultRoute]` directly) |
| Rules take precedence over the default route (package comment) | **No test** |
| Every Pod non-root, RuntimeDefault seccomp, all capabilities dropped, no escalation, read-only root except Keycloak, `/tmp` emptyDir, no `runAsUser`, `app.kubernetes.io` labels, selectors unchanged | **No test.** I checked the render by hand. CI only runs `helm lint` on the stand chart, and lint passes with none of these set. `test/scripts/test-chart-render.sh` asserts the same properties for the agent chart and has no stand case. |
| `make test-stand-files`, `e2e-harness`, `parity-harness`, `e2e-suite`, `parity-suite` | CI runs them (`integration-tests.yaml`, the lint job and the two kind jobs) |
| Realm and stub files regenerated, duplicate users fail | Dockerfile `jq -e` checks run in `make test-stand-files`. Only the no-user-files path is exercised, since `testdata/realm/` holds only a README. |

Findings:
- **Missing pipstub cases.** The original defect was a route with an empty `responses` list indexing `-1`. The case "routed path with no responses and no default route" is absent; it should give 404. Add it to the table in `main_test.go:225-255`. Also add a case where a matching rule beats the default route, and a `handleConfigure` call that registers `*` and then serves an unrouted path. Substantive.
- **Security properties untested.** Request: a render assertion for the stand chart, alongside `test-chart-render.sh:828`. It should cover restricted-PSS fields on every workload, Keycloak as the one writable root, and the `/tmp` emptyDir. Substantive.
- **Unclaimed hunks.**
  - `test/svt/common/compose/docker-compose.yml` bumps Keycloak from `26.0` to `26.3.5@sha256…`. No commit message mentions it. It changes the SVT stack's Keycloak major behavior, and it is not part of the test-stand change.
  - `parity-realm.json` gains 8 users or clients (14 users now, 6 before), including `mt-a`, `mt-a-admin` and four `service-account-parity-m2m-tenant-*` accounts. The commit says only that the parity realm "gains a second tenant realm, parity-mt-b". The idp-seed README does describe them.
  - Request for both: add a sentence that claims the hunk with the run that checks it, or move the hunk to its own change. Substantive.
- **Commands the change tells readers to run.**
  - `docker create` / `docker cp` from the transfer image, `helm upgrade --install … -f my-test-stand-values.yaml` and `helm test --timeout 15m --logs` (chart `README.md`): no CI job runs this form. CI builds the transfer image but never installs from it. The suite is run only as `helm test` without `--logs`, from the Makefile.
  - `helm upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string suite.env.FULL_RUNTIME_SUITE=false` (`docs/local-integration-tests.md`): no job runs it. The outcome depends on `--reuse-values` keeping `suite.env.BASE_URL` from the earlier `--set`, and on Helm replacing the stored test hook. I did not check either on the Helm versions the change supports, 4.3.1 in CI and 3.x locally.
  - Request: one run of each on kind, or replace the subset command with one that is run. Substantive.

## Item 3: Boundaries, partitions, and the negative control

**Pipstub.** The table has the control (a routed path keeps its answer) and the no-default case. It lacks the empty-route and no-default combination (see item 2). The sequence test covers the clamp but not a single-response default route.

**Inherited state (substantive).**
- `e2e-cluster` reuses an existing kind cluster. The old `e2e-harness` created `Deployment/keycloak`, `Service/keycloak`, `ConfigMap/keycloak-realms` and `Secret/authz-agent-client-credentials` (and the parity equivalents) with `kubectl apply`.
- The new chart renders objects with the same names. Helm refuses to adopt objects that lack the `meta.helm.sh/release-name` annotation, so on such a cluster `helm upgrade --install` should fail with an "exists and cannot be imported" error. I could not run this here.
- Every test and CI run starts from a fresh cluster, and no document names a remedy: `make e2e-down` appears only as "Cluster left behind". Request: a run of `make e2e-harness` over a namespace left by the previous commit, or a documented remedy (`make e2e-down`, or delete the namespace), run on that state.

**Replaced mechanism fails later (substantive).**
- The old `e2e-suite` ran `kubectl wait --for=condition=Ready pod … --timeout=3m`. For a pod stuck in `ImagePullBackOff` or `Pending` it failed after 3 minutes with "timed out waiting for the condition". The old harness waited 2 minutes per stub rollout.
- The new `run-suite` (`Makefile`, `define run-suite`) waits up to 2 minutes for the Job and polls logs for up to 3 minutes, so that part runs about 5 minutes. When the pod never starts, `kubectl logs -f` returns an error at once and `wait $$helm_pid` blocks until `helm test` ends. That is at `--timeout 15m`, or when the Job's `activeDeadlineSeconds: 900` fires, since the deadline counts from Job start. The stub rollouts now share `helm --wait --timeout 10m`, against 2 minutes before.
- A stuck pod therefore fails after about 15 minutes instead of 3, and the failing step prints Helm's timeout text rather than the pod condition. No sentence in the change accepts this. Request: run the stuck-pod fault on the new target and add a deadline for the whole wait at the old 3 minutes (for example `helm test --timeout 4m` on the first wait, or kill the helm process once the log wait fails). Alternatively, print the pod state when the wait fails.

**Other limits on the same work (substantive).**
- `suite.activeDeadlineSeconds` (default 900, `values.yaml`) is documented as a setting.
- `helm test --timeout 15m` is fixed in the Makefile `run-suite` and in the chart README, so raising `activeDeadlineSeconds` past 900 has no effect: Helm gives up first and leaves the Job running.
- The `-test.timeout 600s` in `suite.args` is a separate fixed number. At the defaults the inner limit fires first (600 < 900 ≤ 900), which is fine.
- Request: derive the Helm `--timeout` from the deadline, or document and test the relation. The two harness values files also override `args` without the same derivation.

**Existing settings reaching a new consumer.** `E2E_HELM_ARGS` now also reaches the stand install. Both charts define `TAG` and `IMAGE_PULL_POLICY`, and no workflow passes the variable, so I found no conflicting value. No finding.

## Item 3a: Level, placement, and the environment

None. The pipstub behavior is tested in-process in `main_test.go`, in the unit's own file. `serve` is a small new helper, and the older tests build requests inline; reuse is optional. The kind jobs run the chart. The only gap in the chart's tests is the one in item 2.

## Item 4: Names by content, not by position

None. Test case names are by content (`a routed path keeps its own answer`). I found no ordinals in the new text.

## Item 5: The failure report

None. All three pipstub tests use `t.Errorf` with a message that prints the request and both operands. The table cases have names, and the numbered `got`/`want` order is kept.

## Item 6: What the writer says it verified

No commit message states a red run on the base commit or a mutation verdict. The pipstub tests would plausibly fail on the base, because `requestUri` and `defaultRoute` do not exist there. The empty-responses case is the only one tied to a real base-commit crash, and see item 2: it is missing a case. This is the writer's to state.

## Item 7: Siblings of the change

**Stale count.** `README.md:61` still says "CI builds both via `.github/docker-dev-config.json` and publishes them as `ghcr.io/netcracker/qubership-authz-agent` and `…policy-admin`". `docker-dev-config.json` now lists five images, and the lines below say so. Request: rewrite the sentence to name all five or say "the images". Substantive.

**Other member lists.** I searched for `docker-release.yaml`, `docker.cfg` and `docker-dev-config.json`. The three agree on the three added images. `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` still list the right Deployments. The `.PHONY` list includes `test-stand-files`.

**Stub callers.** `routes[...]` and `counters[...]` are used only in `handlePIP`, `handleConfigure`, `handleReset` and the tests. Nothing else reads `callRecord`. The tests in `test/integration/testify/*` read the call list as untyped JSON, and the new `requestUri` field is additive.

**Keycloak setting dropped.** The old manifest set `JAVA_OPTS_APPEND=-Dkeycloak.migration.strategy=OVERWRITE_EXISTING`, and the chart does not. With a dev-mode database on the container filesystem this is harmless today, and the commit's "imports at every start" claim holds because the database starts empty. I note it only so the writer can confirm it was intended.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Header says "per path" while the default route shares one sequence | Substantive | `test/integration/pipstub/main.go:19-21`, `:34-37` | 1 |
| `RequestURI` comment and "nobody configures with it" are over-compressed | Substantive | `main.go:73-75`, `:37` | 1 |
| Test missing for a routed path with no responses and no default (the `-1` crash); rule-beats-default and `configure` with `*` also untested | Substantive | `test/integration/pipstub/main_test.go:225-255` | 2 |
| Pod-security properties claimed but not asserted by any test | Substantive | `helm-templates/authz-test-stand`, `test/scripts/test-chart-render.sh` | 2 |
| Unclaimed hunks: Keycloak bump in SVT compose, and 8 added parity-realm users or clients | Substantive | `test/svt/common/compose/docker-compose.yml:3`, `test/k8s/parity/idp-seed/parity-realm.json` | 2 |
| Documented install-from-image and subset-run commands are not run anywhere | Substantive | `helm-templates/authz-test-stand/README.md`, `docs/local-integration-tests.md` | 2 |
| Existing kind namespace holds kubectl-applied objects the chart cannot adopt; no test or remedy | Substantive | `Makefile` (`e2e-harness`, `parity-harness`) | 3 |
| Stuck pod now fails after about 15 minutes instead of 3, with different output | Substantive | `Makefile` (`define run-suite`) | 3 |
| `activeDeadlineSeconds` raised past 900 is overridden by fixed `helm test --timeout 15m` | Substantive | `helm-templates/authz-test-stand/values.yaml` (`suite.activeDeadlineSeconds`), `Makefile` | 3 |
| "CI builds both" is stale after three images were added | Substantive | `README.md:61` | 7 |

I did not run the kind jobs, `docker build`, `helm test` or any Kubernetes-dependent step. The inherited-state and stuck-pod findings are therefore read from the manifests, the Makefile and Helm's documented behavior, not from a run.
