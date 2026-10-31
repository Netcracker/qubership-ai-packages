# Final review: `58316ca..HEAD` (four commits)

There was no separate task statement, so item 2 takes its claimed cases from the four commit messages and from the comments above the new tests. The drift script ran without error and printed nothing, because it parses only Java, Kotlin, Groovy and Scala files. I checked the changed Go members by hand (the package comment, `callRecord.RequestURI`, `defaultRoute`, `handlePIP`, `LoadConfig`), along with the comments in the Makefile, the chart, and the docs. Other checks I ran: `go test` in `test/integration/pipstub` passes; with the generated files rebuilt in my scratchpad, `helm lint` and `helm template` pass on both values files; with default values the chart renders nothing; and `profile.jq` turns `parity-r29-level-m2m` into `R29LevelM2M`, as its comment says.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-35` and `:122-123`.** Both say the default route answers "every request whose path has no route of its own". The new `handlePIP` also sends a path to the default route when that path's own route has no responses (`len(route.Responses) == 0`). A reader who configures a route with `[]` will expect a 404 for it, not the default answer. **Request:** in both comments, add "or whose route has no responses".
- **`Makefile:99-100`.** This comment says `helm test` "prints the log only at the end". The Makefile does not pass `--logs`, so `helm test` prints no log at all. The chart README (`helm-templates/authz-test-stand/README.md:61-62`) also says that for a Job, Helm 4 prints nothing and Helm 3 fails. **Request:** say that `helm test` prints no log for a Job, which is why the target streams it.
- **`docs/local-integration-tests.md:104`.** The `e2e-harness` row says the target installs "... and the suite Job; waits until they are Ready". The Job is a `helm test` hook, so installing the stand does not create it, as `test/k8s/README.md` says. A reader will expect the suite to run at harness time. **Request:** take the suite Job out of this row, as the `test/k8s/README.md` table does.
- **Taste: `main.go:37-38`.** "as it did before the default route existed" describes the change rather than the code. I would end the sentence at "404".

## Item 2: claimed cases covered

Each claimed case and what covers it:

| Claimed case | What covers it |
| --- | --- |
| An unrouted path gets the default route's answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `.../a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `.../a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses and no default route answers 404 | **No test.** See item 3. |
| No `*` route, or an empty one, answers 404 | `.../an_unrouted_path_without_a_default_route_is_404` and `.../an_unrouted_path_with_an_empty_default_route_is_404` |
| The default route serves its responses in order | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the request target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` accepts the path `*` | The tests write `routes[defaultRoute]` directly. `handleConfigure` is unchanged and stores any path. **Taste:** add one case through `handleConfigure`. |
| Each chart part is off by default | No test in the repository. I checked it: `helm template` with default values renders nothing. |
| Restricted Pod Security Standard (pod and container security context) | No test, and no run. See item 3a. |
| `app.kubernetes.io/*` and `helm.sh/chart` labels; selectors keep `app:` | No render assertion. Both kind CI jobs deploy the chart, so a broken selector would fail there. |
| Keycloak restarts when a realm file changes (`checksum/realms`) | No test. |
| `make test-stand-files`; extra user files merged into the parity realm with profile fields filled in; the build fails on a duplicate user | CI runs `make test-stand-files`, but no user file exists, so the merge, `profile`, and the duplicate check never run on any input. The commit message says "none so far". **Substantive:** add one user file as a fixture, or a CI step that runs the stage on a sample file and on a duplicate. |
| The kind harnesses run on the chart | The CI jobs `Kind end-to-end` and `Parity on kind`. |
| Three new published images | `.qubership/docker.cfg` and `.github/docker-dev-config.json`, consistent with each other. |
| `make e2e-suite` and `make parity-suite` honor `*_SUITE_TIMEOUT` | Nothing runs a value other than the default. See item 3. |

Commands the change tells a reader to run:

- **`make test-stand-files`, `make e2e-harness`, `make e2e-suite`, `make parity-harness`, `make parity-suite`.** Run by CI, with the same flags.
  - `run-suite` (`Makefile:108`) uses `kubectl wait --for=create`, which kubectl added in 1.31. With an older kubectl, the `&&` chain is skipped and no log is streamed, but the target still exits with the suite's result.
  - The prerequisites table (`docs/local-integration-tests.md:37`) names no minimum kubectl version.
  - **Substantive. Request:** state kubectl ≥ 1.31 in that table.
- **`helm test authz-test-stand --timeout 15m` followed by `kubectl logs job/parity-suite`** (`helm-templates/authz-test-stand/README.md:64-67`).
  - The Makefile runs the `helm test` form. The form that reads the log afterwards runs nowhere.
  - Whether it works depends on how the Job ended. A failed test leaves a Failed Pod, so its log can be read. When `activeDeadlineSeconds` expires, the Job controller deletes the Pods still running, so `kubectl logs job/...` then finds no Pod and prints nothing.
  - **Substantive. Request:** run this form on a suite that times out, or document streaming the log (`kubectl logs -f` beside `helm test`, as the Makefile does).
- **Copying the charts out of the transfer image (`docker create` / `docker cp`) and `helm upgrade --install ... --set TAG=<version>`.** These run nowhere. The Dockerfile shows the `/charts/...` layout they rely on, so I see no doubt in the outcome.
- **The subset recipe (`helm upgrade ... --reuse-values --set suite.env.RUNTIME_SUITE_RUN=...`, `docs/local-integration-tests.md`).** This runs nowhere. `--reuse-values` works the same in Helm 3 and Helm 4, so I see no doubt.
- **`make e2e-down` as the remedy for clusters set up by an older `make e2e`.** See item 3.

Hunks that no commit message claims:

- **`test/svt/common/compose/docker-compose.yml:3`.** The SVT Keycloak moves from `26.0` to `26.3.5@sha256:...`. That is a version bump in a harness the change otherwise does not touch. **Substantive. Request:** a sentence in the commit message that claims it, with the SVT run that checks it, or move the hunk to its own change.
- **`test/k8s/parity/idp-seed/parity-realm.json` (+318 lines).** The commit message claims only the new `parity-mt-b` realm. This file also gains the roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`; the clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`; and the users `parity-r29-scope`, `parity-r30-scope`, `mt-a`, and `mt-a-admin`. No suite case in this change uses them; `git grep` outside the JSON finds only READMEs. **Substantive. Request:** claim these additions and name the cases that use them, or move them to the change that adds those cases.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub: the missing partition.** No test covers "a routed path with no responses, and no default route". It answers 404. On the base commit, the same request indexed `Responses[-1]` and panicked, which is the defect the commit message names. The empty-default case at `main_test.go:241` routes a path that has no route at all, so it does not reach this code. **Substantive. Request:** add the row `"a routed path with no responses and no default route is 404"`, with `/routed`, `[]pipResponse{}`, `nil`, and `404`.
- **State an earlier version left behind.** CI starts every run on a fresh kind cluster. For a cluster built by the old `kubectl apply` harness, the documented remedy is `make e2e-down`. Nothing says it was run on such a cluster; the error text is quoted, but no run of the remedy is. **Request:** state that run.
- **A setting that now reaches another consumer.** `E2E_HELM_ARGS` now also reaches the test-stand install (`Makefile:90`, `:155`).
  - The test-stand chart reads two of the same top-level keys as the agent charts: `TAG` (`values.yaml:12`) and `IMAGE_PULL_POLICY`. It also reads Helm's own `--timeout` flag.
  - `IMAGE_PULL_POLICY=Never`, the documented example, means the same thing to both.
  - `--set TAG=<x>`, meant to choose an agent build, makes the stand ask for `local/pip-stub:<x>`, `local/authz-runtime-suite:<x>` and `local/tenant-manager:<x>` with pull policy `Never`. Nothing builds those, so the result is `ErrImageNeverPull`.
  - `--timeout 8m`, meant to give the agent installs longer than 5 minutes, shortens the stand's own wait from 10 minutes to 8, because the later flag wins.
  - **Substantive. Request:** give the stand its own variable (for example `E2E_STAND_HELM_ARGS`), or run the harness with these values.
- **Replaced mechanisms.** No sentence in the change accepts these slower failures.
  - **`e2e-harness`** (the old waits were `rollout status` with 2 minutes per stub and 10 for Keycloak; the new one is a single `helm --wait --timeout 10m`).
    - The troubleshooting table lists a stub image missing from the node (`ErrImageNeverPull`) as a common fault. The old target failed on it after 2 minutes and named the Deployment.
    - The new target fails after 10 minutes, with Helm's wait message.
  - **`e2e-suite` and `parity-suite`.**
    - With the suite image missing, the old target failed after 3 minutes, at `wait --for=condition=Ready pod`.
    - The new target takes up to 3 minutes in its log-poll loop. Then `logs -f` fails, and `wait $helm_pid` blocks until `helm test --timeout 15m` gives up, close to the Job's 900 s deadline. That is about 15 minutes.
  - **Substantive. Request:** run each fault on the new target and record both durations and both outputs. Add a deadline that fails by the old time: for example, end the log loop by checking the Pod's waiting reason and stopping `helm test`. Alternatively, add a sentence that accepts the later failure.
- **Limits on the suite run.** `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` sit inside or beside these other limits:

  | Limit | Set where | Value |
  | --- | --- | --- |
  | `-test.timeout` | `suite.args` in `values.yaml:95-96` and `test/k8s/test-stand-values.yaml:55-56` | 600 s |
  | `activeDeadlineSeconds` | chart default | 900 s |
  | `helm test --timeout` | the new Makefile variables | 15m |
  | `kubectl wait --for=create` | `run-suite` (covers only the Job's start) | 2m |
  | CI `timeout-minutes` | `integration-tests.yaml:120,168` | 30, which also covers the image builds, the harness (up to 10m) and the installs (up to 2×5m) |

  - With the defaults, `-test.timeout` fires first, which is right.
  - Follow the documented recipe (`Makefile:49-50`, chart README `:69-70`): raise `E2E_SUITE_TIMEOUT` to 30m and `activeDeadlineSeconds` to 1800. The suite still dies at 10 minutes on `-test.timeout`, so the raise has no effect. That is the failure the commit message says it fixes.
  - In CI, any suite timeout above about 30 minutes, minus the setup time, is cut off by the job timeout.
  - **Substantive. Request:** name `-test.timeout` in both recipes, or derive it from `activeDeadlineSeconds`. Say that CI is bounded by `timeout-minutes`.

## Item 3a: level, placement, and the environment

- The pip-stub tests are small, in-process tests. They sit beside the existing `handlePIP` tests in `main_test.go` and reuse `resetState`. Good.
- **The restricted Pod Security Standard.** This is the claim of commit 17b17fc, and nothing checks it:
  - no render assertion in `test/scripts/test-chart-render.sh`, which covers only the agent and policy-admin charts;
  - no kind namespace labelled `pod-security.kubernetes.io/enforce=restricted` (`git grep` finds no such label).

  The smallest level is `helm template` with render assertions on the security context, the labels, and "off by default". The larger level is labelling the kind namespaces so that admission enforces the standard in CI. **Substantive. Request:** add both, or at least the render assertions.

## Item 4: names by content, not by position

None. The subtest names and comments refer to cases by their content. The positional `$(1)`…`$(4)` in `run-suite` are how Make passes macro arguments, and each one is named in the comment.

## Item 5: the failure report

None. Each Go assertion prints the call or input, the value it got, and the value it wanted (`GET %s = %d %s, want %d %s`, `statuses of /a, /b, /a = %v, want %v`). The one `t.Fatalf` guards an index into `calls`. No case is named by its index.

## Item 6: what the writer says it verified

- **pip-stub tests:** no red run on the base commit and no mutation verdict is stated. The new tests do not compile on the base commit, so a red run would need a version adapted to the old code.
- **Helm behavior:** the commit message quotes behavior seen with Helm 4.3.1 and 3.22.1, which is evidence for the README's log note.
- **Restricted standard:** no run in a namespace that enforces it is stated.
- **`e2e-down` remedy:** no run on an old cluster is stated.

## Item 7: siblings of the change

- **`README.md:59`.** It still says "CI builds both via `.github/docker-dev-config.json`", but that file now lists five images. **Substantive. Request:** reword it, for example "builds the images `.github/docker-dev-config.json` lists".
- **`test/k8s/README.md:66-71`.** This paragraph lists the variables that override the Makefile defaults. It does not list the new `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`, which `git grep` finds only in the Makefile. **Substantive. Request:** add them there, together with the `-test.timeout` note from item 3.
- **`docs/local-integration-tests.md:190`.** The troubleshooting symptom names both `make e2e-harness` and `make parity-harness`, but the action ends with "then `make e2e`" only. **Substantive. Request:** add "or `make parity`".
- **The -1 index defect.** The rule engine's `respondSequence` in `matchRule` already checks `len > 0`, so it does not have the defect. `git grep` finds no other `len(...)-1` index into a sequence.
- **References to the deleted manifests.** `git grep` finds none left (`runtime-suite-job`, `keycloak.yaml`, `pip-mock.yaml`, `m2m-credentials`, and the others).

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The default-route comments leave out the route that has no responses | Substantive | `test/integration/pipstub/main.go:34`, `:122` | 1 |
| The comment says `helm test` prints the log at the end; it prints none for a Job | Substantive | `Makefile:100` | 1 |
| The `e2e-harness` row says the harness installs and waits for the suite Job | Substantive | `docs/local-integration-tests.md:104` | 1 |
| The pip-stub package comment describes the change ("as it did before") | Taste | `test/integration/pipstub/main.go:37` | 1 |
| The realm-user merge, `profile`, and the duplicate check run on no input | Substantive | `build/authz-agent-transfer/Dockerfile:46` | 2 |
| `--for=create` needs kubectl ≥ 1.31; the prerequisites table names no version | Substantive | `Makefile:108` | 2 |
| `kubectl logs job/...` after `helm test` finds no Pod once the deadline has expired | Substantive | `helm-templates/authz-test-stand/README.md:66` | 2 |
| Unclaimed SVT Keycloak version bump | Substantive | `test/svt/common/compose/docker-compose.yml:3` | 2 |
| Unclaimed clients, roles, and users added to the parity realm | Substantive | `test/k8s/parity/idp-seed/parity-realm.json` | 2 |
| The `*` default route is tested through the map, not through `/pip-stub/configure` | Taste | `test/integration/pipstub/main_test.go:249` | 2 |
| No case for a route with no responses and no default route, the old panic | Substantive | `test/integration/pipstub/main_test.go:241` | 3 |
| The `e2e-down` remedy is not shown run on a cluster from the old harness | Substantive | `docs/local-integration-tests.md:190` | 3 |
| `E2E_HELM_ARGS` passes `TAG` and `--timeout` to the stand, where they mean something else | Substantive | `Makefile:90`, `:155` | 3 |
| Harness and suite targets now fail after 10 and 15 minutes, not 2 and 3 | Substantive | `Makefile:90`, `:105` | 3 |
| Raising the suite timeout has no effect while `-test.timeout 600s` stays | Substantive | `Makefile:50` | 3 |
| No render assertion or enforcing namespace for the restricted standard | Substantive | `helm-templates/authz-test-stand/templates/_helpers.tpl:23` | 3a |
| "CI builds both" is now five images | Substantive | `README.md:59` | 7 |
| The new timeout variables are missing from the list of overrides | Substantive | `test/k8s/README.md:66` | 7 |
| The troubleshooting row names two targets, and its action covers one | Substantive | `docs/local-integration-tests.md:190` | 7 |

No cluster was available, so I could not run the documented commands or the fault scenarios. The suite-wait finding is worked out from the Makefile, and the post-deadline log finding from how the Job controller handles a Job past its deadline. The drift script does not parse Go, so I checked those comments by hand.
