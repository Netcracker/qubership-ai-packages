# Final review: `58316ca..HEAD` (4 commits)

There was no task statement, so the claimed cases under item 2 come from the four commit messages, the test comments, and the changed READMEs. There is no earlier report of this form. The drift script printed nothing because it parses only JVM sources (`EXT = (".java", ".kt", …)`). I checked every Go, YAML, template, Dockerfile and Markdown comment by hand. Skills loaded: final-review, test-authoring (§3, §4, §5, §7, §11, references/go/testing.md) and english-developer-style.

## Item 1: comments consistent with the code and with each other

- **Go comments.** The package doc (`test/integration/pipstub/main.go:34-38`) and the `defaultRoute` comment (`main.go:122-123`) say the default route answers "every request whose path has no route of its own". The code at `main.go:236` also sends a path to the default route when its own route has no responses. The commit message and the test comment (`main_test.go:221-222`) say this; neither production comment does. A reader of the code comments would expect a configured route with an empty `responses` list to answer 404. The `callRecord.RequestURI` comment and the step-2 comment are accurate. "No request path is `*`" holds, because `net/http` answers `OPTIONS *` before any handler runs.
- **`docs/local-integration-tests.md:104`.** The `e2e-harness` row says the target installs "…the client-credentials Secret, and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` object, so `helm upgrade --install` never creates it. `test/k8s/README.md:25-26` and `:57` say the opposite ("installing the stand does not start it"). Two pages contradict each other about one fact.
- **`test/parity/README.md:70-73`.** It says the parity realm "also holds the users of `suite/testdata/realm/`, so the cases that need those users run on the kind harness", and that "their files declare none" (no first name, last name or email). That directory holds only `README.md`, and the commit message says "none so far". The page describes users and cases that do not exist. `build/authz-agent-transfer/Dockerfile:32-37` does the same in a milder form: it says "if any", but then speaks of "the values these users have", with `parity-r29-level-m2m` as the example, a user that exists nowhere in the repository.
- **Chart comments** (`_helpers.tpl`, `suite.yaml`, `idp.yaml`, `values.yaml`). They match the rendered output: `runAsNonRoot` and `RuntimeDefault` on every Pod, `drop: ALL`, no privilege escalation, a read-only root everywhere but Keycloak, and an emptyDir at `/tmp` sized from `ephemeral-storage`. I rendered both values files from a scratch copy with stub `files/`.
- **`suite.yaml:12-13`.** The comment matches `before-hook-creation`.
- **`profile.jq`.** The comment matches what the code does: I ran it on `parity-r29-level-m2m` and got `Parity` / `R29LevelM2M` / `parity-r29-level-m2m@example.test`.
- **The idp-seed README.** Its realm, user, role, client and `tenant-id` claims match the JSON, checked with jq.
- No comment narrates the change with "now" or "no longer".

## Item 2: claimed cases covered

**pipstub (9d25da7)**

| Claimed case | Test |
|---|---|
| Default route answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses falls through **to 404** when there is no default route (the original index −1 case) | **none.** The 404 rows use the unrouted path `/users/u-1`, never `/routed` with `[]` and no default route. |
| No default route → 404, as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| Empty default route → 404 | `…/an_unrouted_path_with_an_empty_default_route_is_404` |
| The default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` takes `*` | No test goes through `handleConfigure`; all tests write `routes[defaultRoute]` directly. The handler stores any path, so this is taste. |

**Chart and harness (8b85515)**

| Claimed case | What runs it |
|---|---|
| Each part is off by default | Not tested. I rendered the defaults by hand: 0 objects. |
| Keycloak imports the realm files at every start | Kind CI jobs |
| Keycloak restarts when a realm file changes (checksum annotation) | **none** |
| `tenantManager.tenants is required`; the "no realm files…" and "no file files/pip-stub/…" failures | **none** in CI. I reproduced the pip-stub message with `helm template`. |
| `make test-stand-files` | CI `chart` job |
| Merges user files and fills in the profile fields; fails on a duplicate username or id | **none.** The directory has no user file, so the jq merge, `profile` and both uniqueness checks never run on any input. |
| `parity-mt-b` realm | Present, but no parity case refers to it (`git grep parity-mt-b -- test/parity` finds only the README). |
| The release publishes three more images | `.qubership/docker.cfg`; cannot be run here |

**Security context and labels (17b17fc)**

| Claimed case | What runs it |
|---|---|
| The stand starts under the restricted Pod Security Standard | **none.** `e2e-harness` and `parity-harness` use `--create-namespace` with no `pod-security.kubernetes.io/enforce` label, so no run puts the chart through restricted admission. Kind does run the Pods as non-root with read-only roots, which shows they start. It would not catch a container that lost `drop: ALL`. |
| Every object carries the `app.kubernetes.io/*` and `helm.sh/chart` labels; selectors keep `app: <name>` | **none.** `test/scripts/test-chart-render.sh` asserts these for the agent chart (around lines 809-845) and has nothing for the test-stand chart. |

**Command lines in the changed files**

| Command (file) | Promised outcome | Run by |
|---|---|---|
| `make test-stand-files` | Generates `files/` | CI `chart` job ✓ |
| `docker build … -f build/authz-agent-transfer/Dockerfile .` (Dockerfile header) | The transfer image | Presumably the shared build through `.github/docker-dev-config.json`, which is outside the repository and not verified |
| `docker create/cp/rm …` (test-stand README, step 1) | Charts copied out | **none.** Depends on the transfer image's `/charts` layout. `docker create` on a `scratch` image does not run `true`, so it should work. |
| `helm upgrade --install authz-test-stand ./charts/authz-test-stand --set TAG=<version> -f …` (README, step 2) | Stand up on a non-kind cluster with the published images | **none.** Depends on the published images `ghcr.io/netcracker/qubership-authz-{pip-stub,parity-suite}:<version>` and on `files/` in the image. Nothing runs this path. |
| `helm test authz-test-stand --timeout 15m` (README, step 3) | Exits with the suite's outcome | `run-suite` in the Makefile, same flags ✓ (kind) |
| `kubectl logs job/parity-suite` (README, step 3) | The log | `run-suite` polls the same command ✓ |
| Claim that `helm test --logs` fails on Helm 3 | `unable to get pod logs for …` | Confirmed in source: Helm v3.15.2 `pkg/action/release_testing.go:127-130` calls `Pods().GetLogs(h.Name)` for every test hook. I could not check the Helm 4 claim offline. |
| `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false` (docs §6) | A subset run | **none.** Depends on `--reuse-values` keeping the earlier `--set suite.env.BASE_URL`. It is the same in Helm 3 and 4, so the risk is low. |
| `make e2e-down`, then `make e2e` (docs table, test/k8s README) | Clears the ownership-metadata failure | **none** on that state; see item 3. |
| `E2E_SUITE_TIMEOUT=…` / `PARITY_SUITE_TIMEOUT=…` override | A suite runs past 15 minutes | **none**, and it cannot pass as documented; see item 3. |

## Item 3: boundaries, partitions, and the negative control

- **pipstub.** The negative control is present: no default route answers 404, which stays green on the base commit. The partition "routed path with empty responses and no default route" is missing (item 2). A rule-engine match with a default route configured is not tested together. Precedence is structural, so this is taste.
- **Inherited state.** The change replaces objects that an older `kubectl apply` harness created. Every run starts from a fresh kind cluster. The writer chose a documented remedy (`make e2e-down`), which test-authoring §3 allows. The commit quotes the error text, so the failure was seen; nothing says the remedy was run on that state. Deleting the cluster removes everything, so the outcome is not in doubt. A second point: `docs/local-integration-tests.md:190` lists `make parity-harness` failing, but its remedy says "then `make e2e`", and `make parity` is the matching rerun. Taste.
- **Limits on one suite run**

  | Limit | Where it is set | Counted from | Default |
  |---|---|---|---|
  | `-test.timeout 600s` | `suite.args`: `values.yaml:94-96` and `test/k8s/test-stand-values.yaml:55-56` | Test process start | 10 m |
  | `activeDeadlineSeconds` | `values.yaml:99` | Job start, including scheduling and image pull | 900 s |
  | `helm test --timeout` | `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` (`Makefile:51-52`); fixed at 15m in the test-stand README | Before the Job exists | 15 m |
  | `timeout-minutes: 30` | `integration-tests.yaml:120,168` | Job start, not suite start | 30 m |

  The last row does not end the work "from the same start", so it is not one of the limits. I list it because it caps any raised suite timeout in CI.

  - **(a) A setting capped by a limit fixed elsewhere.** `Makefile:49-50` tells a longer suite to raise the helm timeout "together with suite.activeDeadlineSeconds". The commit title says the change lets "a suite outlast 15 minutes". The Go binary still panics after 10 minutes unless `suite.args` changes too, so raising the two named settings past 600 s has no effect. The Makefile comment, the `values.yaml` suite comment and the README sentence at `README.md:69-70` should all name `-test.timeout`, or the args should take it from the deadline.
  - **(b) Inner limit not firing first at the defaults.** The helm wait (15 m, counted from before the Job exists) and `activeDeadlineSeconds` (900 s, counted from Job start) are equal. "No shorter than" (`Makefile:103-104`) and "at least as long as" (`README.md:69`) allow that equality, and the README example uses it. Whenever the deadline is what would end the Job (a Pod stuck in Pending or pulling), the helm wait expires a moment earlier and its timeout replaces the Job's `DeadlineExceeded`. The fix is a strict margin, such as "longer than", with a 16 m default or a derived value.

## Item 3a: level, placement, and the environment

- pipstub: the tests are small, in-process `httptest` tests, beside the existing `TestHandlePIP_*` tests and on the shared `resetState()`. They run in CI through the `go-build.yaml` module list (`test/integration/pipstub`). This is the correct level and placement.
- Chart: the rendered properties (security contexts, labels, selectors, required-value failures) can be observed with `helm template` and need no cluster. The repository's render-assertion script covers the sibling charts and not this one. The request is assertions in `test/scripts/test-chart-render.sh`. Optionally, label the kind namespaces `pod-security.kubernetes.io/enforce=restricted` so the existing CI run enforces the claim; that needs a check that the agent and policy-admin charts also pass.
- The CI `chart` job lints both test-stand values files after `make test-stand-files`; this is correct.

## Item 4: names by content, not by position

None that matters. The test and subtest names describe the scenario. "Its own image and pull policy below" (`values.yaml`) and "the Makefile targets below" (`test/k8s/README.md`) point by position at nearby text; naming `idp.image` would be steadier. Taste.

## Item 5: the failure report

None.
- Every new assertion prints got and want in the Go order, `GET %s = %d %s, want %d %s`, and the input appears in the message.
- The subtests are named by condition, not by index.
- `t.Fatalf("recorded %d calls, want 1")` comes before the dereference that needs it, which is correct (go/testing.md, "Keep going, or stop").
- The `||` in `TestHandlePIP_RecordsTheRequestTargetAsSent` joins two fields, but the message prints both fields and both expected values, so the report is complete.

## Item 6: what the writer says it verified

- No red run on the base commit and no mutation verdict is stated for the pipstub tests.
  - The routed-empty row would panic on the base commit (`idx = -1`), but no message says so.
- No kind run, restricted-namespace run, or transfer-image install is stated for the chart commits.
- The only evidence stated is the Helm 4.3.1 and 3.22.1 behavior quoted in 5dcb6be; I confirmed the Helm 3 half in source.
- Not evidence of failure, only a check: `go test ./...` in `test/integration/pipstub` passes, and `helm lint` and `helm template` pass on both values files with stub `files/`.

## Item 7: siblings of the change

- `routes` and `counters` readers: `handleConfigure` stores `*` like any other path, `loadDefaultRoutes` never adds `*`, and `handleReset` clears the `*` counter. The other index into a response sequence, `matchRule`'s `respondSequence`, already checks `len(...) > 0`, so the −1 defect does not apply there.
- The `podSecurityContext`, `containerSecurityContext` and `labels` helpers are called from all five templates; I rendered every call site.
- `run-suite` has two callers, both updated.
- I found no remaining reference to the deleted manifests (`git grep` for `runtime-suite-job`, `keycloak.yaml`, `pip-mock.yaml` and the others) and no other `helm test --logs`.
- Siblings of the 15 m fix: the README example still hard-codes `15m`, and both CI kind jobs have `timeout-minutes: 30`. Neither is mentioned beside the new variables.

## Findings

| # | Finding | Label | File:line | Change requested |
|---|---|---|---|---|
| 1 | `-test.timeout 600s` in `suite.args` caps every suite at 10 m; raising the helm timeout and `activeDeadlineSeconds` as documented has no effect, despite the commit title | Substantive | `Makefile:49-50`, `values.yaml:94-99`, `test/k8s/test-stand-values.yaml:55-56`, `README.md:69-70` | Name the third limit beside the other two, or take `-test.timeout` from the deadline |
| 2 | The helm wait equals `activeDeadlineSeconds` and starts earlier, so it fires first and hides the Job's `DeadlineExceeded`; "no shorter than" allows the equality | Substantive | `Makefile:51-52,103-104`, `README.md:65,69` | Make the helm wait strictly longer (for example 16m), or derive one value from the other |
| 3 | The restricted Pod Security claim and the label/selector claim have no test; the kind namespaces do not enforce restricted, and the render script skips this chart | Substantive | `Makefile:90,155`; `test/scripts/test-chart-render.sh` | Add render assertions for the test-stand chart, or label the harness namespaces `enforce=restricted` |
| 4 | Routed path with no responses and no default route → 404 is claimed but not tested | Substantive | `test/integration/pipstub/main_test.go:236-240` | Add the row `"/routed", []pipResponse{}, nil, 404` |
| 5 | The production comments omit the routed-but-empty case of the default route | Substantive | `pipstub/main.go:34-35,122-123` | Add "or whose route has no responses" |
| 6 | Docs say `e2e-harness` installs the suite Job and waits for it; the test/k8s README says the opposite | Substantive | `docs/local-integration-tests.md:104` | Drop "and the suite Job" from the row |
| 7 | The parity README describes user files and cases that do not exist; the Dockerfile comment gives a nonexistent user as the example | Substantive | `test/parity/README.md:70-73`; `build/authz-agent-transfer/Dockerfile:32-37` | Say the directory is empty so far and what the stage will do with a file when one is added |
| 8 | The jq merge, `profile` and both duplicate checks never run on any input | Substantive | `build/authz-agent-transfer/Dockerfile:39-45` | A fixture user file run through the stage in CI, or keep the claim until the first real file lands |
| 9 | The transfer-image install flow (README steps 1-2) and the `--reuse-values` subset command are not run anywhere | Substantive | `helm-templates/authz-test-stand/README.md:38-58`; `docs/local-integration-tests.md` §6 | One run of each on the configuration they describe, or a note that they are unverified |
| 10 | The CI job's `timeout-minutes: 30` also caps a raised suite timeout in CI and is not mentioned | Taste | `.github/workflows/integration-tests.yaml:120,168` | Mention it beside `E2E_SUITE_TIMEOUT` |
| 11 | The ownership-metadata remedy for `parity-harness` says "then `make e2e`" | Taste | `docs/local-integration-tests.md:190` | "then `make e2e` or `make parity`" |
| 12 | `/pip-stub/configure` with `*` is never tested through the handler | Taste | `pipstub/main_test.go` | One test that posts `[{"path":"*",…}]` |
| 13 | "below" points at nearby values or sections by position | Taste | `values.yaml` (TAG comment), `test/k8s/README.md:4` | Name the key or the section |

Not checked: the full Go suites and the kind jobs were not run (there is no cluster), the Helm 4 `--logs` behavior and the shared org build workflow are outside the repository, and no pass was made over the prose for style alone.
