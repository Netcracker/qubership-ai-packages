# Final review: `58316ca..HEAD` (3 commits)

**Inputs.** There is no separate task statement, so the claimed cases come from the three commit messages and the test comments. I loaded `final-review` and `test-authoring` with its Go `testing` reference. The `english-developer-style` skill is not in the skills directory, so I cite no wording rules. The drift script exited 0 with no output because it parses only Java, Kotlin, Groovy and Scala. I checked comment drift by hand over the Go, Helm, Makefile and Markdown changes. No previous report exists.

What I ran, all read-only or in the scratchpad:
- `go test` in `test/integration/pipstub` passed.
- A scratch copy of the chart, with `files/` filled by plain copies of the realm and rule files, passes `helm lint` with both stand values files. It renders with `helm template` and validates under `kubeconform -strict`: 12 objects for e2e and 10 for parity. With default values it renders nothing.
- `profile.jq` on a sample user file turns `parity-r29-level-m2m` into `R29LevelM2M` and keeps a declared `firstName`.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-38` and `:122-124`.** Both comments say the default route answers "every request whose path has no route of its own". The code at `:235-237` also sends a path whose route has *no responses* to the default route, and the commit message claims that case. A reader would expect an empty route to answer 404 for its own path.
- **`main.go:37-38`.** "as it did before the default route existed" narrates the change in a package comment. "A stub nobody configures with it answers an unrouted request 404" already says it without history.
- **`docs/local-integration-tests.md`, `e2e-harness` row.** It says the target installs "… and the suite Job; waits until they are Ready". The Job is a `helm test` hook, so the install neither creates it nor waits for it. `test/k8s/README.md` says "installing the stand does not start it", and its own `e2e-harness` row leaves the Job out. The two docs contradict each other.
- **`test/parity/README.md`, Identity provider section.** It says "The `parity` realm … also holds the users of `suite/testdata/realm/`, so the cases that need those users run…", and "their files declare none". The directory holds only `README.md`, and the commit says "none so far". A reader would look for users and cases that do not exist.
- **`test/parity/suite/testdata/realm/README.md`.** It says the stage "fails when two files declare the same username or id". The `jq -e` checks run over the merged realm, so the stage also fails when one file repeats a user that `parity-realm.json` already declares. That case is missing from the list.
- **`helm-templates/authz-test-stand/templates/_helpers.tpl:2-5`.** It says the selectors keep `app: <name>` "so the Makefile's deploy/<name> … address a part". `deploy/<name>` resolves by object name, not by label, so the stated reason is false for the Makefile half. The `kubectl -l` half holds.
- Checked and consistent: `callRecord.RequestURI`, the step-2 comment in `handlePIP`, every comment in `values.yaml` and the templates, the testify `Dockerfile` and `helpers.go` pointers, the `docker-release.yaml` header, `REALM-DESCRIPTION.md`, and both stand values files.

## Item 2: claimed cases covered

**`test(pipstub)`**

| Claimed case | Test |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| Routed path keeps its own answer | `…/a routed path keeps its own answer` |
| Stub not configured with `*` answers 404 as before | `…/an unrouted path without a default route is 404` |
| Route with no responses falls through to the default route | `…/a routed path with no responses gets the default answer`. On the base commit this indexes at -1 and panics, so it is red there. |
| Route with no responses, with no default route → 404 | **None.** This is the exact input that panicked on the base. |
| `/pip-stub/configure` takes the path `*` | **None.** Every test writes `routes["*"]` directly and never goes through `handleConfigure`. |
| Default route serves its responses in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |

**`test(k8s)` chart commit**

None of these claims has a test in the repository. Most are exercised only by the CI jobs `kind-e2e` and `kind-parity`, which run the make targets end to end.
- Each part off by default: verified only by my render.
- Realm import at every start, and the restart when a realm file changes (the `checksum/realms` annotation): no test that the checksum moves.
- `tenantManager.tenants` required: no test.
- Merging the user files and filling in the profile fields: no input exists, so nothing in the repository exercises it.
- The duplicate-user build failure: no test.

The commit names `parity-mt-b` as the realm's only addition. `parity-realm.json` also gains 5 clients and 6 users: the four `parity-m2m-tenant-*` clients, `parity-end-user-tenant-a`, `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`. Nothing outside the realm files and their README uses them, and the message does not say they come ahead of their cases, as it does for the stub.

**`test(k8s)` restricted commit**

| Claimed case | Coverage |
| --- | --- |
| Stand starts in a namespace that enforces `restricted` | **No test or run.** `--create-namespace` creates an unlabelled namespace, so kind admits anything. |
| `app.kubernetes.io/*` and `helm.sh/chart` on every object | No test |
| No `runAsUser` pinned | No test |
| `/tmp` emptyDir on the suite Job | No test, and no suite test asks for a temp dir (by grep) |

The design reason, OpenShift SCC assigning the uid, is not testable offline. A render assertion that no `runAsUser` appears would fail if someone pinned one.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub partitions.**
  - Missing: an empty routed route with no default route.
  - Missing: a rule-engine match while a default route exists. That is the control showing rules still win.
  - Present: a sequence clamped to the last response, and an empty default route.
- **Pre-existing state.** Before this change, `make e2e-harness` and `make parity-harness` created these objects with `kubectl apply`:
  - e2e: `deploy/keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, ConfigMap `keycloak-realms`, Secret `authz-agent-client-credentials`, ServiceAccount `runtime-suite`.
  - parity: `deploy/idp`, `pip-mock`, `entitlements-mock`, the Secret.

  The chart now renders objects with the same names in the same namespaces. On a cluster set up before this change, `helm upgrade --install authz-test-stand` will refuse them for missing Helm ownership metadata. That is my reading of Helm's adoption rule; I did not run it, since there is no cluster. Every CI run starts from a fresh kind cluster, and no doc tells a developer to run `make e2e-down` (or delete the namespace) first. This is the inherited-state partition with no run and no documented remedy.

## Item 3a: level, placement, and the environment

- **pip-stub tests.** They are small and in-process, beside the existing tests in `main_test.go`, and share `resetState`. CI runs them through `go-build.yaml`. No finding.
- **Chart.** Its labels, security contexts and off-by-default parts can all be seen in a render, with no cluster. The repository already asserts the same security properties for the sibling charts in `test/scripts/test-chart-render.sh` (around `:788-834`). The test-stand chart has no assertion there; CI only runs `helm lint` on it.
- **Restricted admission.** It exists only across the API-server boundary, so the finding is the CI job. `kind-e2e` and `kind-parity` never label their namespaces `pod-security.kubernetes.io/enforce=restricted`. Both sibling charts already set `runAsNonRoot`, `RuntimeDefault`, drop `ALL` and disable escalation, so the label looks feasible. I did not check their Pod-level `seccompProfile`.

## Item 4: names by content, not by position

- The test and subtest names are all by content.
- `values.yaml`: "Keycloak has its own image and pull policy below" means `idp.image`. It could say "under `idp`".
- `test/k8s/README.md`: "The Makefile targets below" keeps the wording that was there before.

## Item 5: the failure report

None. Every new assertion is a `t.Errorf` or `t.Fatalf` that prints got and want in Go's order, with the input (`GET %s`, `statuses of /a, /b, /a`). Subtest ids are condition names, not indices. The one compound condition in `RecordsTheRequestTargetAsSent` prints both operands of both comparisons.

## Item 6: what the writer says it verified

None of the three commit messages states a red run on the base commit or a mutation verdict. For the pip-stub fix, the empty-route case would panic on the base, but the commits do not say so. For the chart commits, no run on kind is reported in the messages.

## Item 7: siblings of the change

- **`PipController.ResetPinnedRoutes`** (`test/parity/suite/pip_control.go:185-205`). It "resets" each pinned path by registering a 404 response for it. Under the new semantics, that leftover route shadows the default route for that path in every later test. If `*` itself was pinned, it also turns the default route into a 404 for all unrouted paths. Registering `responses: []` would now really fall through. This applies once the cases that use `*` arrive, so it needs a fix or a named follow-up.
- **`PipStubCall`** (same file, `:72`). It has no `RequestURI`. The struct comment says fields are added as the assertion code needs them, and the commit defers the cases, so this is consistent. No finding.
- **`writeRespond` echo.** It builds its own map, so `requestUri` does not leak into echoed bodies. Parity goldens are unaffected.
- **Stale references.** `git grep` finds none to the deleted manifests or the `m2m-credentials` files outside `docs/handovers` and `docs/plans`.
- **`E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS`.** They match the Deployment names the chart renders.
- **Image users.** Every image the chart runs has a numeric `USER`, which `runAsNonRoot` requires: `10001` for the local images, and `1000` for Keycloak from memory (not read here).

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | Re-running the harness on a stand created by the old `kubectl apply` manifests meets same-named objects without Helm ownership. No run starts from that state and no remedy is documented. | Substantive | `Makefile` (`e2e-harness`, `parity-harness`); `docs/local-integration-tests.md` | Document and verify the remedy (`make e2e-down`, or delete the namespace) on an old stand, or run once from that state. |
| 2 | The restricted Pod Security Standard claim has no run: the kind namespaces do not enforce it. | Substantive | `Makefile` `e2e-harness`/`parity-harness`; `.github/workflows/integration-tests.yaml` | Label both namespaces `pod-security.kubernetes.io/enforce=restricted` before the installs, so the CI jobs prove it. |
| 3 | The test-stand chart has no render assertions; its sibling charts do. | Substantive | `test/scripts/test-chart-render.sh` | Assert the Pod and container security contexts, the absence of `runAsUser`, the labels, and an empty default render. |
| 4 | No test for an empty routed route with no default route, the input that panicked on the base commit. | Substantive | `test/integration/pipstub/main_test.go:233` | Add a row: `/routed` with `[]`, no default, expecting 404. |
| 5 | No test registers `*` through `/pip-stub/configure`, the interface the commit names. | Substantive | `main_test.go` | Register `*` through `handleConfigure` in one case, then hit an unrouted path. |
| 6 | No control showing a matching rule still beats the default route. | Substantive | `main_test.go` | Add a case with a rule and `*` both present, expecting the rule's answer. |
| 7 | The default-route comments leave out that it also answers a routed path with no responses. | Substantive | `main.go:34-36`, `:122-123` | Add that case to both comments. |
| 8 | The `e2e-harness` row says the target installs the suite Job and waits for it. | Substantive | `docs/local-integration-tests.md` (`e2e-harness` row) | Drop the Job, as `test/k8s/README.md` does. |
| 9 | The parity README states that the realm holds users from `testdata/realm/` and that cases need them; none exist. | Substantive | `test/parity/README.md`, Identity provider section | Say the directory takes user files and holds none yet. |
| 10 | The duplicate-user check is described as between two files; it also fails on a repeat of a user the realm already has. | Substantive | `test/parity/suite/testdata/realm/README.md` | Say the stage fails when a username or id appears twice in the merged realm. |
| 11 | The helper comment gives the selector label as the reason `deploy/<name>` works; that resolves by name. | Substantive | `helm-templates/authz-test-stand/templates/_helpers.tpl:2-5` | Drop the `deploy/<name>` half, or state the real reason. |
| 12 | `parity-realm.json` gains 5 clients and 6 users that the commit message does not mention and nothing uses. | Substantive | `test/k8s/parity/idp-seed/parity-realm.json`; commit `8b85515` | Name them in the message, with the cases they are for. |
| 13 | `ResetPinnedRoutes` leaves a 404 route that shadows the default route, and resets a pinned `*` to 404. | Substantive | `test/parity/suite/pip_control.go:185-205` | Fix it (re-register with `responses: []`), or name it as follow-up for the cases that use `*`. |
| 14 | The profile fill-in and the duplicate check have no input in the repository. | Substantive | `build/authz-agent-transfer/Dockerfile`, `profile.jq` | A fixture user file in a build check, or state that it lands with the first user file. |
| 15 | No red run or mutation verdict is stated for any of the three commits. | Substantive | commit messages | State the red run of `a routed path with no responses gets the default answer` on the base, and the kind runs. |
| 16 | The package comment narrates history ("before the default route existed"). | Taste | `main.go:37-38` | End at "answers an unrouted request 404". |
| 17 | "pull policy below" refers by position. | Taste | `helm-templates/authz-test-stand/values.yaml` (`TAG` comment) | "under `idp`". |

**Not checked:** I did not run the kind suites (no cluster), `make test-stand-files` or any Docker build, Helm's ownership refusal on a real stand, or Keycloak's own `USER`. The drift script does not parse Go, YAML, Makefile or Markdown, so that pass was manual. I did not do a style-only read of the prose.
