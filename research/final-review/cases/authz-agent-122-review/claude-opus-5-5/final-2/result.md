# Final review: `58316ca..HEAD` (8b85515, 9d25da7, 17b17fc)

I found nine substantive findings and three taste findings across the three commits. The pipstub tests miss the exact case the fix was for. The restricted Pod Security Standard (PSS) claim has no check anywhere: no render assertion, and the kind jobs don't enforce it. A developer's existing kind cluster will refuse the new install, and nothing documents the fix. Several comments and docs state things that aren't true.

**How I ran it.** There was no task statement, so the claimed cases come from the three commit messages and the test comments only. There was no previous report. The drift script printed nothing: it parses only Java, Kotlin, Groovy and Scala, so I did item 1 by hand. I rendered the test-stand chart with both harness value files, using a copy in the scratchpad with the generated files rebuilt by hand. `helm lint` and `kubeconform -strict` passed: 12 and 10 objects. I also ran `go test` on pipstub, which passed.

**Test stack line.** `AGENTS.md` names no test stack. I propose adding one line: `Tests: Go testing (engine and assertions) for test/integration/pipstub; testify for test/integration/testify.`

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-35` and `:122`.** Both say the default route answers "every request whose path has no route of its own". The commit and the code also send a path whose route has *no responses* to the default route. A reader of either comment would expect such a route to answer 404 (or panic, as before).
- **`helm-templates/authz-test-stand/templates/_helpers.tpl:2-4`.** It says the selectors keep `app: <name>` "so the Makefile's deploy/<name> and a reader's kubectl -l app=<name> address a part by its Service name". `deploy/<name>` finds a Deployment by its name and works with any selector. The real reason goes unstated: a Deployment's selector is immutable, so changing it would break `helm upgrade` over a stand that is already installed.
- **`test/k8s/parity/idp-seed/parity-realm.json:30`.** The description of `ROLE_MT_READER` cites `TestTenantScopedDecisions`. No such test exists in the repository. None of the other additions to this realm appear anywhere outside `idp-seed/` either: `mt-a`, `mt-a-admin`, `parity-r29-scope`, `parity-r30-scope`, the four `parity-m2m-tenant-*` clients, and `parity-end-user-tenant-a`.
- **`docs/local-integration-tests.md:104`.** It says `e2e-harness` installs "… and the suite Job; waits until they are Ready". The Job is a `helm test` hook and is not created at install. `test/k8s/README.md` says the opposite: "installing the stand does not start it".
- **`test/parity/README.md:69-73`.** It talks about the users of `suite/testdata/realm/` as if they exist: "their files declare none", "so the cases that need those users run on the kind harness". The directory holds only a README; the commit message says "none so far".
- No comment narrates the change (`now`, `no longer`).
- The other new comments match the code: `callRecord.RequestURI`, the new test comments, the security-context helpers, `values.yaml`, the Makefile `run-suite` comment, the Dockerfile header and `profile.jq`. I checked `profile.jq`'s example by hand: `parity-r29-level-m2m` becomes `R29LevelM2M`.

## Item 2: claimed cases covered

| Claimed case | Test |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer (control) | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| **A route with no responses falls through "or to 404"** (the old index −1 panic) | **None.** Every row with an empty routed path also has a default route. |
| No `*` configured: unrouted path answers 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| The default route keeps one sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` takes `*` | Tests write `routes` directly; `handleConfigure` itself is unchanged (taste) |
| The stand starts under the restricted PSS | **None.** No render assertion, and the kind namespaces are created by `--create-namespace` with no `pod-security.kubernetes.io/enforce` label. |
| Read-only root filesystem everywhere except Keycloak; capabilities dropped; app.kubernetes.io labels on every object | **None.** I confirmed all three only by rendering by hand. |
| No `runAsUser`, so OpenShift can assign one (a design reason) | **None.** No test would fail if a `runAsUser` were pinned. |
| Chart replaces the loose manifests; `helm test` runs the suites | The kind e2e and parity CI jobs, through `make e2e-harness`/`e2e-suite` and the parity targets |
| Generated files; duplicate users fail the build | The CI lint job runs `make test-stand-files`. The duplicate check has no failing example: the user directory is empty. |
| Parity realm gains tenant realm `parity-mt-b` | No case uses it; see item 1 |

## Item 3: boundaries, partitions, and the negative control

- **pipstub.** The empty-responses partition is tested only together with a default route; the missing row is in item 2. The other partitions are present: unrouted vs routed, default route present, absent or empty. The control row ("a routed path keeps its own answer") is present.
- **Inherited state, 8b85515.** A developer's kind cluster from before this change holds objects that `kubectl apply` created: Deployments `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`, the ConfigMap `keycloak-realms`, and the Secret `authz-agent-client-credentials`. The parity namespace holds the same set. Without Helm ownership metadata, `helm upgrade --install authz-test-stand` should refuse them with "invalid ownership metadata". I reasoned this from Helm's behavior; I could not run a cluster. CI starts from a fresh cluster, so it never meets this state. No document names the remedy, such as `make e2e-down`.
- **Inherited state, 17b17fc.** Upgrading a stand installed by 8b85515 changes Keycloak's Pod template (labels and securityContext), so Keycloak restarts and mints new realm keys. `docs/local-integration-tests.md:127` ties "restart the agent afterwards" to realm-file changes only.
- **Limits on the suite run.** Three limits apply:
  - `-test.timeout 600s` in `suite.args`, a documented setting.
  - `suite.activeDeadlineSeconds: 900` (`values.yaml:99`), a documented setting.
  - `helm test --timeout 15m`, fixed in `Makefile:102` and `README.md:64`.

  Raising `activeDeadlineSeconds` past 900 has no effect under `make e2e-suite` or `make parity-suite`, because the fixed 15 minutes caps it. At the defaults the two tie, and Helm's clock starts first, so Helm's timeout hides the Job's `DeadlineExceeded`. The 600 s test timeout fires first, which is correct.
- **Size limit on `/tmp` (taste).** The suite's `emptyDir.sizeLimit` is set equal to the container's `ephemeral-storage` limit (256Mi in both value files). The Pod-level check counts the emptyDir plus logs against that same 256Mi, so the `sizeLimit` can never fire first.

## Item 3a: level, placement, and the environment

- **pipstub.** The new tests are small and in-process. They sit in `main_test.go` beside the existing `handlePIP` tests and share `resetState`. The new `serve` helper copies no existing helper. No finding.
- **Chart.** `test/scripts/test-chart-render.sh` checks the sibling charts for seccomp, read-only root filesystem and labels (around lines 783-840). The test stand gets none of these checks, although CI already generates its files before linting. A render check is the cheapest level that would catch a dropped field. Whether a namespace *admits* the Pods can only be seen in a cluster. I rendered `authz-agent` and `authz-policy-admin` with the kind values, and both already meet the restricted fields. So the kind jobs could label their namespaces `enforce=restricted` and exercise the claim for real.

## Item 4: names by content, not by position

None. The case names state their condition. Comments name things by content ("tenant B's realm", "the request-args rule set"), not by ordinal.

## Item 5: the failure report

None. Every new assertion prints the function, the input, what came back and what was expected, for example `GET %s = %d %s, want %d %s` and `statuses of /a, /b, /a = %v, want %v`. The combined `requestUri`/`path` check prints all four values. Subtest names describe the case, not an index.

## Item 6: what the writer says it verified

None of the three commits states any evidence that the tests can fail: no red run on the base and no mutation verdict. On the base, the empty-routes row should panic at index −1, but that is not shown. None of the commits says whether the kind harnesses were run on 8b85515 or on 17b17fc.

## Item 7: siblings of the change

- **`handlePIP`** is the only reader of `routes` and `counters`.
- **`ResetPinnedRoutes`** (`test/parity/suite/pip_control.go:181`) would pin a 404 on `*` if a test had pinned `*`. That behaves like having no default route, so it is not a defect.
- **`PipStubCall`** (`pip_control.go:72`) does not mirror `requestUri`. The commit message defers that to the cases that will use it, so it is not a defect.
- **Security context.** The only other pod specs installed in the same namespaces come from the two product charts, and both already pass the restricted fields.
- **Render assertions.** `test-chart-render.sh` checks the two sibling charts and not this one (item 3a).

## Findings

| # | Finding | Label | File:line | Requested change |
| --- | --- | --- | --- | --- |
| 1 | A route with no responses and no default route answering 404 (the old panic) has no test | Substantive | `test/integration/pipstub/main_test.go:228` | Add the row "a routed path with no responses and no default route is 404" |
| 2 | Comments leave out that a route with no responses also falls to the default route | Substantive | `test/integration/pipstub/main.go:34-35`, `:122` | Add "or whose route has no responses" |
| 3 | Restricted PSS, labels, read-only root filesystem and no-`runAsUser` claims have no test | Substantive | `test/scripts/test-chart-render.sh`; `Makefile:85`, `:149` | Add render assertions for the test stand; label the kind namespaces `pod-security.kubernetes.io/enforce=restricted` |
| 4 | An existing kind cluster with the old `kubectl apply` objects will make the Helm install fail; no remedy is documented. The 17b17fc upgrade also restarts Keycloak | Substantive | `test/k8s/README.md`; `docs/local-integration-tests.md:127` | Document the remedy (`make e2e-down`, or delete the namespaces), run it on such a cluster, and widen the Keycloak-restart note |
| 5 | The fixed `helm test --timeout 15m` caps `suite.activeDeadlineSeconds` and hides its report at the defaults | Substantive | `Makefile:102`, `README.md:64`, `values.yaml:99` | Derive the Helm timeout from the value plus a margin, or document the pair |
| 6 | Wrong reason given for keeping the `app` selector | Substantive | `templates/_helpers.tpl:2-4` | Say the selector is immutable, so changing it would break `helm upgrade` |
| 7 | Role description cites a test that doesn't exist; the realm additions are unused and absent from the commit message | Substantive | `test/k8s/parity/idp-seed/parity-realm.json:30` | Drop the test name, or bring the additions with the cases that use them, as 9d25da7 does for its stub |
| 8 | Docs say `e2e-harness` installs and waits for the suite Job | Substantive | `docs/local-integration-tests.md:104` | Drop "and the suite Job" |
| 9 | README describes user files and cases that don't exist yet | Taste | `test/parity/README.md:69-73` | Phrase it conditionally, as `testdata/realm/README.md` does |
| 10 | `/tmp` `sizeLimit` equals the container limit, so it never fires first | Taste | `templates/suite.yaml:68` | Drop it, or set it below the limit |
| 11 | Tests bypass `/pip-stub/configure` | Taste | `main_test.go:244` | Configure one row through `handleConfigure` |

**Not checked.** I had no cluster, so PSS admission, Keycloak starting as non-root, Helm adoption and the timeouts are reasoned from configuration rather than run. I did not build the Docker `chart-files` stage. I did not run the kind suites, only the pipstub `go test`. I did not do a style pass over the prose.
