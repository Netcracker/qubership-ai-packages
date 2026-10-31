# Final review: `58316ca..HEAD` (3 commits)

**Inputs.**
- **Task statement:** none was handed over. The claimed cases come from the three commit messages only (`17b17fc` restricted PSS, `9d25da7` pip-stub default route, `8b85515` test-stand chart).
- **Skills loaded:** `test-authoring` and `english-developer-style` from the given directory.
- **Drift script:** it printed nothing for this range, although `pipstub/main.go` and `helpers.go` changed. I read the Go hunks by hand instead.
- **Local runs:**
  - `go test` in `test/integration/pipstub` passes.
  - `helm lint` and `helm template` render both values files, on a scratch copy of the chart with the generated files copied in by hand.
  - The rendered output has `runAsNonRoot`, `allowPrivilegeEscalation: false` and `drop: ALL` on every Deployment and Job. `readOnlyRootFilesystem` is `false` only on Keycloak.
  - `checksum/realms` changes when a realm file changes.
- **Not done:** no cluster, so `helm test` and the Makefile recipes were not run. I did not build the Docker images.

## Item 1: comments consistent with the code and each other

1. `docs/local-integration-tests.md:190` still says `make e2e-harness` times out at `rollout status deploy/keycloak`. The target now runs `helm upgrade --install --wait` and has no `rollout status` step. A reader looking for that text will not find it. Request: name the `--wait` timeout and the Pod to check, `kubectl -n authz-e2e get pods`.
2. `README.md` (near line 60) still reads "CI builds both via `.github/docker-dev-config.json`", but that file now lists five images. The sentences before and after were updated. Request: drop "both".
3. `_helpers.tpl`, the `containerSecurityContext` comment: "Takes the value of readOnlyRootFilesystem: true for every container except Keycloak" reads as if the helper takes `true`. The argument is the value of `readOnlyRootFilesystem`, and Keycloak passes `false`. Taste: rewrite as "Takes the value of readOnlyRootFilesystem, which is true for every container except Keycloak's."
4. `values.yaml`, the `TAG` comment, lists "pip-stub, authz-parity-suite, and tenant-manager". The e2e values also use `TAG` for `local/authz-runtime-suite`. Taste: change to "the images of this repository".
5. `pipstub/main.go`: the package comment, `defaultRoute`, `callRecord.RequestURI` and the `handlePIP` step 2 comment agree with the code. The claim "No request path is *" holds because `ServeMux` answers `OPTIONS *` before the handler. None found there.

## Item 2: claimed cases covered

| Claim | Test or runner |
| --- | --- |
| Unrouted path gets the default answer | `DefaultRouteAnswersUnroutedPaths`, case "an unrouted path gets the default answer" |
| Routed path keeps its own answer | same test, case "a routed path keeps its own answer" |
| Route with no responses falls through to the default route | same test, case "a routed path with no responses gets the default answer" |
| An unconfigured stub answers 404, as before | same test, case "an unrouted path without a default route is 404" |
| Empty default route answers 404 | same test, case "an unrouted path with an empty default route is 404" |
| Sequence is shared across paths | `DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `RecordsTheRequestTargetAsSent` |
| Non-root, seccomp, drop ALL, read-only root, `emptyDir` at `/tmp`, labels | **none** (finding 6) |
| Realm change restarts Keycloak | none (checksum annotation; I rendered it by hand, see Inputs) |
| `make e2e-harness`, `parity-harness`, `e2e-suite`, `parity-suite` | `.github/workflows/integration-tests.yaml` runs the Makefile targets on kind (not run here) |
| `make test-stand-files` | the `helm lint` step in CI |

Commands the change tells someone to run:

- `helm test authz-test-stand --timeout 15m --logs` (chart README step 3).
  - **Runner:** `none`. The Makefile runs `helm test` without `--logs`.
  - **What the outcome depends on:** the suite is a Job hook, not a Pod hook.
  - **What I could not settle:** I did not find in Helm's help text what `--logs` acts on for a Job hook. The Makefile comment says helm prints the log only at the end, which is the opposite of what the README promises.
- The `helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` subset recipe in `docs/local-integration-tests.md`. **Runner:** `none`.
- The chart README's `docker create` / `docker cp` / `helm upgrade --install … -f my-test-stand-values.yaml` steps. **Runner:** `none`.

Findings:

6. **Substantive.** Neither the `restricted` Pod Security claim of `17b17fc` nor the labels have an assertion. `test/scripts/test-chart-render.sh` renders only the agent charts, and CI only runs `helm lint` on the test stand. `lint` does not check security contexts. A template edit that drops `seccompProfile` from one Deployment stays green. Request: add a render assertion over both values files for the following:
   - every Pod has `runAsNonRoot` and `RuntimeDefault` seccomp;
   - every container has `allowPrivilegeEscalation: false` and `drop: [ALL]`;
   - `readOnlyRootFilesystem` is true on all but Keycloak;
   - the Job mounts the `/tmp` `emptyDir`.
7. **Substantive.** Neither `--logs` nor the subset recipe has a runner. Request: run both forms on the kind stand, or replace the README form with the Makefile's `helm test` plus `kubectl logs -f`.
8. **Substantive, unclaimed hunk.** `test/svt/common/compose/docker-compose.yml` moves Keycloak from `26.0` to `26.3.5@sha256:…`. No sentence of `8b85515` claims it, and it changes a stack the commit does not touch. Request: claim it with a run of the svt compose stack, or move it to its own change.
9. **Substantive.** `9d25da7` claims "a route with no responses falls through to the default route, or to 404". The 404 half has no case with an empty-response route and no default route, which is the old index `-1` path. The "empty default route" case routes a non-empty `/routed`, so it does not cover it. Request: add a case with `/routed` having `[]pipResponse{}` and `defaultResponses` nil, expecting 404.

## Item 3: boundaries, partitions, negative control

Pip-stub: the boundaries are covered (no default, empty default, routed and empty-routed, sequence clamp). The controls hold on the base commit ("routed path keeps its own answer", "without a default route is 404"). Findings 10–12 below are all about the chart and Makefile.

10. **Substantive, pre-existing state.** Every run of the new chart starts from a fresh namespace. A kind cluster and namespace that `make e2e-harness` created with the old code are reused, because `e2e-cluster` skips creation when the cluster exists. They hold objects applied by `kubectl apply -f` with no Helm ownership metadata: Deployments `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, `pip-mock` and `idp`, the ConfigMap `keycloak-realms`, and the Secret `authz-agent-client-credentials`. `helm upgrade --install` refuses to adopt them ("invalid ownership metadata"). The parity ConfigMaps `parity-realms` and `pip-mock-config` are orphaned. No file states a remedy, and `make e2e-down` is the only teardown. Request: run `make e2e-harness` over a stand from the previous commit, then either document the remedy (delete the namespace) or add a cleanup step.
11. **Substantive, replaced mechanism (`run-suite`).** The old recipe waited `kubectl wait --for=condition=Ready pod` for 3 minutes, so a Pod that never started (`ErrImageNeverPull`, which `docs/local-integration-tests.md:187` lists as the usual fault) failed after 3 minutes with the wait error. The new recipe does the following:
    - It waits up to 2 minutes for the Job to exist, then polls `logs` for up to 3 minutes. A pull failure outlasts the poll.
    - `logs -f` then errors at once.
    - `wait $$helm_pid` blocks until `helm test --timeout 15m`, or the Job's `activeDeadlineSeconds: 900`, expires.
    - So the failure arrives at about 17 minutes and prints only one `kubectl logs` error.

    Nothing in the change accepts this. Request: run that fault on the new recipe, and bound the whole wait at the old 3 minutes. For example, kill `helm test` when the poll loop runs out without a log. Print the Pod state.
12. **Substantive, setting reaching a new consumer.** `E2E_HELM_ARGS` now reaches the test-stand install, and the documented example is `--set IMAGE_PULL_POLICY=Never`. The chart reads `TAG` and `IMAGE_PULL_POLICY`, the same names the agent charts read. `E2E_HELM_ARGS='--set TAG=x'` therefore changes the stand images too. Keycloak ignores both, since `idp.imagePullPolicy` is its own key. This is plausible and intended, but no run passes such a value. Request: one `helm template` run with `--set TAG=other --set IMAGE_PULL_POLICY=Always`, or a sentence saying the names are shared on purpose.

Limits on the same work: the suite `-test.timeout 600s`, the Job's `activeDeadlineSeconds: 900`, and `helm test --timeout 15m` (900 s) are consistent, but the two 900 values are independent literals. Taste: derive one from the other.

## Item 3a: level, placement, environment

Pip-stub: in-process tests beside the existing ones, in the same package and file, using the existing `resetState`. The new `serve` helper is only partly shared: the existing tests build requests inline, so it is not a copy of one. None found. Chart: no test at the lowest level that could observe it (finding 6).

## Item 4: names by content

None. The test names, case names and chart headings I read use content names. Checked the new test names, the Dockerfile stage names, and the docs section references.

## Item 5: failure report

None. The Go tests use `t.Errorf` with the operands and the case name in the subtest name. `RecordsTheRequestTargetAsSent` joins two comparisons with `||` but prints both values.

## Item 6: what the writer says it verified

None of the three commit messages states a red run on the base commit or a mutation verdict for the pip-stub tests or for the chart. Say so; the writer owes it.

## Item 7: siblings

- **Callers and readers:** the `callRecord` JSON gained `requestUri`; `git grep` finds the `/pip-stub/calls` readers only in the parity suite and testify, which decode into structs that tolerate an extra field. Consumers of `routes[...]` and `counters[...]`: `handlePIP` only. `handleReset` clears `counters`, so the default route's sequence resets too.
- **Set size:** findings 1 and 2 (docs and README still count the old set).
- **Old paths:** no remaining mention of the deleted manifests (`keycloak.yaml`, `runtime-suite-job.yaml`, `parity-suite-job.yaml` and the others) outside `docs/handovers`.
- **Twin path:** `e2e-restart` and `parity-restart` list Deployment names that match the values files. `docs/local-integration-tests.md` still tells the reader to restart Keycloak by hand; the new text covers this.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Troubleshooting row names a `rollout status deploy/keycloak` step the target no longer has | Substantive | `docs/local-integration-tests.md:190` | 1 |
| "CI builds both" while five images are built | Substantive | `README.md` (about line 60) | 1 |
| `containerSecurityContext` comment reads as taking `true` | Taste | `_helpers.tpl` (comment) | 1 |
| `TAG` comment omits the runtime suite image | Taste | `values.yaml` (`TAG` comment) | 1 |
| No assertion for the PSS settings, the `/tmp` mount or the labels | Substantive | `test/scripts/test-chart-render.sh`, `integration-tests.yaml` | 2 |
| `helm test … --logs` and the subset recipe have no runner | Substantive | `helm-templates/authz-test-stand/README.md`, `docs/local-integration-tests.md` | 2 |
| Keycloak `26.0` → `26.3.5@sha256` bump is not claimed | Substantive | `test/svt/common/compose/docker-compose.yml:3` | 2 |
| Empty-response route with no default route (the 404 half) has no case | Substantive | `pipstub/main_test.go:225` | 2 |
| Stand from the old commit blocks `helm upgrade --install`; no remedy | Substantive | `Makefile` (`e2e-harness`, `parity-harness`) | 3 |
| `run-suite` fails after about 17 minutes instead of 3 on an image fault | Substantive | `Makefile` (`run-suite`) | 3 |
| Shared names `TAG` / `IMAGE_PULL_POLICY` reach the stand via `E2E_HELM_ARGS` | Substantive | `Makefile` (`E2E_HELM_ARGS`) | 3 |
| The two 900 s limits are independent literals | Taste | `values.yaml`, `Makefile` | 3 |
| No red-run or mutation evidence stated | Substantive | the three commit messages | 6 |

The only check not done is the live behavior of `helm test --logs` on a Job hook and the kind runs, because there is no cluster here.
