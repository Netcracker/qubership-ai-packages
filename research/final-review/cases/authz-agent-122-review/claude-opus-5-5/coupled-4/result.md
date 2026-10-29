# Final review: `58316ca..HEAD` (3 commits)

**Inputs.** No task statement was handed over, so item 2 takes its claimed cases from the three commit messages and the test comments alone. I loaded `test-authoring` (Go `testing.md`) and `english-developer-style`. The drift script ran and printed nothing, because it parses only Java, Kotlin, Groovy, and Scala. This change is Go, Helm, YAML, Makefile, and Markdown, so I did item 1 by hand over every changed comment. There is no previous report.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-38` (package doc) and `:122-124` (`defaultRoute`).** Both say the default route answers "every request whose path has no route of its own". The change also sends a path whose route has an empty `Responses` to the default route (`main.go:236`). A reader would conclude that a route configured with `[]` still answers its own path. The list leaves out the case the change added.
- **`main.go:35`: "in sequence like any other route".** Another route keeps one sequence per path. This one keeps a single counter for every unrouted path, keyed `*`, which `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` pins down. A reader would expect `/a` and `/b` to each start at the first response.
- **`main.go:37-38`: "…as it did before the default route existed".** This narrates the change history (taste).
- **`templates/_helpers.tpl:2-4`.** It says the selectors keep `app: <name>` "so the Makefile's deploy/<name> … address a part". `deploy/<name>` resolves by object name, not by label, so only the `kubectl -l` half of the sentence is true.
- **`docs/local-integration-tests.md`, `e2e-harness` row.** It says the target installs "…and the suite Job; waits until they are Ready". A `helm.sh/hook: test` Job is not created at install. `test/k8s/README.md` says the opposite: "installing the stand does not start it".
- **`values.yaml:9-11`.** It lists the images that `TAG` applies to as pip-stub, authz-parity-suite, and tenant-manager. The e2e stand also runs `authz-runtime-suite` through `suite.imageRepository` (taste).
- **Checked and consistent:**
  - `suite.yaml:12-13`: hook delete policy.
  - `idp.yaml`: the probe comment (5 s × 60 = 5 min) and the `/auth` comment.
  - `podSecurityContext`/`containerSecurityContext` comments against the rendered output.
  - `callRecord.RequestURI` comment.
  - `LoadConfig` and testify `Dockerfile` pointers. Both now point at `suite.env`/`suite.args`, which exist.
  - `REALM-DESCRIPTION.md`: the `/auth` issuer now matches the old and new `KC_HOSTNAME`.
  - `profile.jq` example: I ran it, and `parity-r29-level-m2m` gives `R29LevelM2M`.
  - `git grep` finds no remaining reference to the deleted manifests.

## Item 2: claimed cases covered

| Claimed case | Test |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| No `*` configured → 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses → default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses → **404** (the `-1` index defect) | **No case.** A routed `[]` with no default route is never served. See item 3. |
| `/pip-stub/configure` takes `*` | Indirect only: the tests write `routes[defaultRoute]` directly. `handleConfigure` is unchanged, so this is taste. |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| The default route serves a sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| Stand starts under the **restricted** Pod Security Standard | **No test or run.** Neither kind namespace is labelled `pod-security.kubernetes.io/enforce=restricted`, because `--create-namespace` creates it with no labels. `test-chart-render.sh` asserts security contexts for the agent chart (`:828-834`) but not for this chart. |
| Read-only root everywhere except Keycloak; `/tmp` emptyDir | Only functional, through the CI kind jobs. No render assertion. |
| `app.kubernetes.io/*` and `helm.sh/chart` labels; selectors stay `app:` | `helm lint` only. No assertion. |
| Every part off by default | No test. By hand: `helm template` with the defaults renders 1 byte. |
| Keycloak restarts when a realm file changes | No test. By hand, editing one realm file changed `checksum/realms`. |
| `profile.jq` fills first name, last name, and email; the build fails on a duplicate username or id | **No test.** `testdata/realm/` holds only a README, so CI never runs the jq merge with a user or the duplicate checks. |
| `make e2e-*`/`parity-*` install and run the chart | The CI jobs `kind-e2e` and `kind-parity` |
| Agent and policy-admin resource profiles unchanged | Confirmed by the diff: those install lines change only in how helm is invoked. |

## Item 3: boundaries, partitions, and the negative control

- **pip-stub partitions.** The table covers the default route present, absent, and empty, and a routed path with and without responses. One combination is missing: a routed path with empty responses and **no** default route. That is the configuration that indexed at `-1` on the base commit, and it is the regression the commit message names. The control is present: a stub with no `*` still answers 404.
- **Pre-existing state: substantive.** `make e2e-harness` and `make parity-harness` on a cluster the old harness set up will fail, and nothing documents the fix. The old harness used `kubectl apply` to create objects with exactly the names the chart now owns:
  - e2e: Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, and `tenant-manager`; ConfigMap `keycloak-realms`; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`.
  - parity: `idp`, `pip-mock`, and others.

  `helm upgrade --install` refuses them with "invalid ownership metadata". Every run in the change starts from a fresh kind cluster, and no doc names the fix (`make e2e-down` first, or `--take-ownership`).
- **Limits on the suite run.** There are three:
  - `-test.timeout 600s` in `suite.args`;
  - `suite.activeDeadlineSeconds: 900`;
  - `helm test --timeout 15m` = 900 s, fixed in the Makefile `run-suite` and in the chart README.

  At the defaults the innermost limit fires first. But `activeDeadlineSeconds` equals helm's timeout, and helm's clock starts earlier. A value past 900, or a `-test.timeout` past 900 s, therefore has no effect, and at 900 the helm timeout can report before the Job's `DeadlineExceeded` does. The Keycloak startup probe (300 s) is inside `--wait --timeout 10m`, which is fine.

## Item 3a: level, placement, and the environment

- **pip-stub.** These are small, in-process tests beside the existing `TestHandlePIP_*` tests, sharing `resetState`. That is correct.
- **Chart.** The security-context and label claims can be observed at render level with no cluster, and the repository already has a render-assertion script for its sibling charts. The test-stand chart has none. The cross-boundary claim, that the stand starts under the restricted PSS, needs the kind namespaces created with the `enforce=restricted` label, so that the CI jobs actually exercise it.

## Item 4: names by content, not by position

None. The subtest names, test function names, the "parity-mt-b" and "three charts" references, and the doc cross-references all name things by content.

## Item 5: the failure report

None. Every check prints its operands in got-then-want form, for example `GET %s = %d %s, want %d %s` and `statuses of /a, /b, /a = %v, want %v`. There is no bare boolean check and no index-named case.

## Item 6: what the writer says it verified

Not stated. None of the three commits shows the red run on the base commit for the `-1` index fix or the default route, or a mutation verdict, or a green kind run. As a consistency check, `go test` and `go vet` in `test/integration/pipstub` pass, and `helm lint` and `helm template` pass with both values files. For that check I copied the chart to a scratch directory and filled `files/` by hand rather than through `make test-stand-files`.

## Item 7: siblings of the change

- **`readOnlyRootFilesystem`.** The authz-agent and authz-policy-admin charts set it only when `PAAS_PLATFORM` is `KUBERNETES` (`deployment.yaml:266` and `:138`). The test-stand chart hard-codes `true` while it claims OpenShift compatibility. No evidence that this breaks anything; taste: give the reason, or use the same switch.
- **`/pip-stub/calls` readers.** These are the parity `GetCalls` and three testify call sites. None of them uses `DisallowUnknownFields`, so the new `requestUri` field is safe.
- **`ResetPinnedRoutes`** (`pip_control.go:181`) and `/pip-stub/reset` do not unregister routes, so a `*` route would survive into the next test. No case configures `*` yet, so this does not apply now. It belongs with the cases the commit message defers.
- **`run-suite`.** Its two callers are `e2e-suite` and `parity-suite`, and both are covered by the limit finding above.

## Findings

| Finding | Label | Location | Request |
| --- | --- | --- | --- |
| An old harness namespace makes `helm upgrade --install` fail on objects it does not own; no documented fix | Substantive | `Makefile` `e2e-harness`/`parity-harness`; `docs/local-integration-tests.md` | A run over the old state, or a documented fix (`make e2e-down`, or `--take-ownership`) that has been run on that state |
| The restricted PSS claim has no test or run | Substantive | `helm-templates/authz-test-stand/README.md:8-10`; `Makefile` | Create the kind namespaces with `pod-security.kubernetes.io/enforce=restricted`, and add render assertions for this chart to `test/scripts/test-chart-render.sh` (security contexts, labels, realm checksum) |
| No case for a routed path with empty responses and no default route (the `-1` defect) | Substantive | `test/integration/pipstub/main_test.go:236` | Add `{"a routed path with no responses and no default route is 404", "/routed", []pipResponse{}, nil, 404, …}` |
| `profile.jq` and the duplicate checks never run with any input | Substantive | `build/authz-agent-transfer/Dockerfile:39-46` | A fixture user file, or a jq check in CI over a sample input |
| The doc comment leaves out the empty-responses fall-through | Substantive | `main.go:34-38`, `:122-124` | Name the case: "…has no route of its own, or a route with no responses" |
| "In sequence like any other route" implies one sequence per path | Substantive | `main.go:35` | Say that one sequence is shared across every unrouted path |
| The docs say `e2e-harness` installs the suite Job and waits for it | Substantive | `docs/local-integration-tests.md`, `e2e-harness` row | Drop the Job from that row, as `test/k8s/README.md` does |
| `deploy/<name>` is attributed to the selectors | Substantive | `templates/_helpers.tpl:2-4` | Credit the object name for `deploy/<name>` and the label only for `-l app=` |
| `suite.activeDeadlineSeconds` and `-test.timeout` past 900 s are capped by the `helm test --timeout 15m` fixed in the Makefile; at 900 the two outer limits tie | Substantive | `values.yaml:95-99`; `Makefile` `run-suite`; chart `README.md` | Derive the helm timeout from `activeDeadlineSeconds` plus a margin, or document the pair |
| The `*` route is tested by writing `routes` directly, not through `/pip-stub/configure` | Taste | `main_test.go:225-273` | One case through `handleConfigure` |
| History narration: "as it did before the default route existed" | Taste | `main.go:37-38` | State the current behavior only |
| The `TAG` comment omits the runtime-suite image | Taste | `values.yaml:9-11` | Say "the images this repository builds" without the list |
| Read-only root is hard-coded, while the sibling charts exempt OpenShift | Taste | `templates/_helpers.tpl:34-36` | State the reason, or follow `READONLY_CONTAINER_FILE_SYSTEM_ENABLED`/`PAAS_PLATFORM` |

Not checked: the kind suites, `make test-stand-files`, and the Docker builds were not run, since there is no cluster. Docker was used only for the jq check, through the local jq binary. Nothing was tried on OpenShift, and the prose was not given a style-only pass.
