**Final review: `58316ca..HEAD` (3 commits, 48 files)**

**Scope and inputs**
- No task statement was handed over. Claimed cases come from the three commit messages and the test class comments. Commit 9d25da7 is the only one with Go tests.
- Skills loaded: `test-authoring` and `english-developer-style`, from the provided skills directory. The Go doc-comment skill (`godoc-authoring`) is not among the provided copies, so I did not load it. Item 1 for Go comments used the form's own questions.
- No previous report exists, so §4 has no table.
- `comment-drift.py` ran from the repository root and printed nothing. It parses only `.java`, `.kt`, `.kts`, `.groovy` and `.scala`, so Go, Helm, Makefile and Markdown were read by hand.
- Evidence I ran, without changing any file:
  - `go test ./...` in `test/integration/pipstub`: ok.
  - `helm lint` of the test-stand chart with both kind value files: passes. I used a scratch copy with the generated `files/` staged, and my staging skipped the parity user merge, so that render is not the Dockerfile output.
  - `helm template` of both value sets: every container has the restricted security fields, and every object has the `app.kubernetes.io` labels and `helm.sh/chart`.
  - `make -n` of the suite and harness targets.
  - A small Go program to check the request path for `OPTIONS *`.

**Item 1: comments consistent with code and each other**
Findings 4–8 below. The rest holds: the `callRecord.RequestURI` comment, the `defaultRoute` comment, the test comments in `main_test.go`, the `_helpers.tpl` and `suite.yaml` comments, and the `testify` Dockerfile and `helpers.go` references to `suite.args` and `suite.env` (both exist). No comment in the three commits narrates the change with "now" or "no longer". The drift script covers none of these files, so this item rests on the hand reading.

**Item 2: claimed cases covered**
- 9d25da7, default route: `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` covers an unrouted path, a routed path, a routed path with no responses, no default route, and an empty default route. `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` covers the shared sequence and the clamp. `TestHandlePIP_RecordsTheRequestTargetAsSent` covers `requestUri`.
- 9d25da7, configure: "`/pip-stub/configure` now takes the path `*`" has no test through `handleConfigure`. The tests write `routes[defaultRoute]` directly (`main_test.go:225`). Finding 3.
- 17b17fc, restricted Pod Security Standard, labels and selectors: no test. The only check is `helm lint` in CI, which asserts none of these fields. `test/scripts/test-chart-render.sh` renders only the agent and policy-admin charts. Finding 2.
- 8b85515, the chart parts, `make test-stand-files`, and the `parity-mt-b` realm contents: checked by reading and rendering. Not covered by any test. The `parity-mt-b` contents (users, clients, `tenant-id` claim) match the JSON.

**Item 3: boundaries, partitions, negative control**
- The pipstub control arms exist. The no-default 404 and the routed-path-keeps-its-answer cases are green on base; the sequence test is red on base.
- Pre-existing state: the change replaces objects an earlier version created with `kubectl`, and no test or documented remedy covers that state. Finding 1.
- Limits: `suite.activeDeadlineSeconds` is 900 (`values.yaml:99`), and the `helm test --timeout 15m` in the `run-suite` macro is also 900 (`Makefile:102`). The inner deadline does not fire strictly before the outer timeout. Finding 9. The `-test.timeout 600s` fires first, which is correct. The `emptyDir` `sizeLimit` is derived from the `ephemeral-storage` limit, which is correct.

**Item 3a: level, placement, environment**
- The pipstub tests are in-process through `httptest`, which is the smallest level. They sit at the end of `main_test.go`, use `resetState`, and add no skip.
- The chart has no test at the smallest level (see finding 2).
- Whether CI runs `go test` for the pipstub package was not checked.

**Item 4: names by content**
none. Test names and case ids state content. The chart comments use counts that check out: "the two tenant realms" and "the two stubs" are correct, and the startup-probe "allows five" is minutes and correct.

**Item 5: failure report**
none. The pipstub failures print got and want, `reflect.DeepEqual` failures print both values, and the compound `if` in the RequestURI test is a comparison with the operands printed.

**Item 6: what the writer says it verified**
None stated. The commit messages carry only `Assisted-by`; there is no red run and no mutation verdict. The RequestURI test cannot compile on the base commit, because the field is missing. A red run there would show a compile error, not the symptom, so it would not be the evidence test-authoring §1 asks for.

**Item 7: siblings**
- `callRecord` consumers: `pip_admin_test.go:128` decodes into maps, and `entitlements_test.go:244` checks only the status. The new field is additive, so none.
- Container security context: `podSecurityContext` and `containerSecurityContext` are applied to all four containers (keycloak, pip-stub, tenant-manager, suite), checked in the render. none.
- Stale references: grep over Markdown, YAML, shell and Makefile found no reference to the deleted manifests. none.
- Observation, not a finding: no caller in this change configures `*`. The commit says the stub comes with the cases that use it, and no such case exists yet, so the default route is unused in the stack.

**Findings**

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | Helm's `upgrade --install` runs over the objects the old `kubectl apply` flow created (Keycloak Deployment and Service, the stubs, the Secret, the ConfigMap, the `runtime-suite` ServiceAccount). Helm refuses to adopt resources without its ownership metadata. `e2e-cluster` creates the cluster only if absent, so the old state survives. No remedy is documented, and this state was never run. The Helm behavior is from its documented ownership check, not run here. | Substantive | `Makefile:86`, `Makefile:150`; `docs/local-integration-tests.md` | Document the remedy (`make e2e-down` before the first upgrade, or delete the old objects), or run the harness once from an old-state cluster and say so. |
| 2 | 17b17fc's claims (restricted fields on every Pod and container, `app.kubernetes.io` labels on every object, selectors keep `app:`) have no test. `test-chart-render.sh` does not render the test stand. | Substantive | `helm-templates/authz-test-stand/templates/*.yaml`; `test/scripts/test-chart-render.sh` | Add render assertions for the test-stand chart to the render script, or a helm unit test, covering those fields. |
| 3 | 9d25da7's "`/pip-stub/configure` now takes the path `*`" has no test through `handleConfigure`. The tests set `routes[defaultRoute]` directly. | Substantive | `test/integration/pipstub/main_test.go:225` | Add a test that PUTs `[{"path":"*",...}]` to `handleConfigure`, then GETs an unrouted path. |
| 4 | "No request path is `*`" is false: `OPTIONS *` gives `URL.Path == "*"`, which I confirmed with `net/url` and `httptest`. The answer is unchanged, so the consequence is nil, but the sentence is wrong. | Substantive | `test/integration/pipstub/main.go:36` | Reword, for example: "A request for `*` (`OPTIONS *`) gets the same answer, so it never shadows a real route." |
| 5 | "answers every request whose path has no route of its own" omits the case the code and the tests cover: a route with no responses also falls through. | Substantive | `test/integration/pipstub/main.go:35` | Say "no route with responses of its own". |
| 6 | "the M2M client-credentials Secret the chart expects the platform to provision". On kind the stand chart creates the Secret (`clientCredentials.enabled: true`). | Substantive | `Makefile:83` | Say the stand chart creates it from its values. |
| 7 | "It prints the log only at the end". `helm test` without `--logs` prints no log, and this invocation has no `--logs`. | Substantive (low) | `Makefile:96` | Say that `helm test` prints no log here, so the log is streamed with `kubectl logs` while it runs. |
| 8 | "runs Keycloak with `authz-test-realm.json` and `cloud-common-realm.json`". The e2e stand imports the whole `authn/` directory, four realms. | Substantive (low) | `test/k8s/authn/REALM-DESCRIPTION.md:82` | Name all four, or say "the realms of `test/k8s/authn/`". |
| 9 | Limit order: `activeDeadlineSeconds` (900) equals `helm test --timeout 15m` (900s). The Job's own deadline does not fire first. | Substantive (low) | `helm-templates/authz-test-stand/values.yaml:99`; `Makefile:102` | Set the deadline below the timeout, or derive one from the other, and document the pair. |
| 10 | The new "default route" (`*`) shares its name with the existing `loadDefaultRoutes` "hardcoded defaults". | Taste | `main.go:122`, `main.go:162` | Prefer a distinct name for one of them. Expect this to be declined. |

**What the review did not check**
- No cluster exists, so none of the e2e or parity runs, Keycloak's behavior, the Helm adoption error in finding 1, or the Keycloak image's numeric `USER` were run.
- The `kubectl wait --for=create` in `run-suite` needs a newer kubectl, which I did not check.
- The transfer-image `RUN` (the `jq` merge and the `profile` filter) was not run.
- Only the pipstub package's tests were run. The other Go packages in the change (testify, the parity suite, the tenant-manager) were not.
- No wording pass over the prose was done beyond the sentences cited above.
