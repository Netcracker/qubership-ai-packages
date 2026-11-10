# Final review: `58316ca..HEAD` (three commits)

There was no task statement, so the claimed cases come only from the three commit messages and the test comments. The drift script printed nothing: it parses only Java, Kotlin, Groovy, and Scala, and this change is Go, Helm, Makefile, and Markdown. I checked the Go members by hand. Only three skills were provided, so the doc-comment checklist (`godoc-authoring`) was not run.

What I ran: `go test` on `test/integration/pipstub` (passes). `helm lint` and `helm template` with both values files, on a scratch copy of the chart with the realm and rule files copied in by hand. `jq` with `profile.jq` on a sample user. The local `pip-stub` and `parity-suite` images under `docker run --read-only --cap-drop ALL` with no network. I also read Helm 3.15.2's `release_testing.go` from the Go module cache. No repository file was changed.

## Item 1: comments consistent with the code and with each other

- **The default-route comments leave out the case the change added.** `test/integration/pipstub/main.go:34-36` and `:122-123` say the default route answers "every request whose path has no route of its own". The code at `:236` also sends a request to it when its own route has no responses, and the commit message claims that case. A reader who configures an empty route to force a 404 on one path would get the default answer instead. Request: add "or whose route has no responses" to both comments.
- **Two sentences need a second read** (`english-developer-style` §4, *Unpack an over-compressed sentence*):
  - `main.go:74-76`: "so that a caller that encodes a value in the path differently from one that does not can be told apart". It is unclear what "one that does not" leaves out. Suggested: "so that a test can tell `/users/a%2Fb` from `/users/a/b`, which decode to the same `Path`."
  - `main_test.go:222-224` packs three outcomes into one sentence, and "or one with no responses" can refer to the stub or to the default route. Request: one sentence per outcome, naming "a default route with no responses".
- **`_helpers.tpl:2-4` gives the wrong reason for keeping the selector.** It says the selectors keep `app: <name>` "so the Makefile's deploy/<name> … address a part". `deploy/<name>` resolves by object name and does not depend on the selector. The real constraint is that a Deployment's selector is immutable, so changing it breaks `helm upgrade` of a release installed from `8b85515`. A reader who trusts the comment could change the selector. Request: state the immutability, and keep the `kubectl -l app=<name>` clause.
- **`docs/local-integration-tests.md:104` is false.** It says `e2e-harness` installs "the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` object, so install never creates it, as `test/k8s/README.md` correctly says. Request: drop "and the suite Job".
- **`test/k8s/parity/idp-seed/parity-realm.json:30` names a test that does not exist.** It refers to "TestTenantScopedDecisions and others", but no such test exists at HEAD (`git grep` finds no match outside this file). Request: drop the name, or add it together with the test (see the unclaimed-hunks finding under item 2).
- **Coined term "stand" / "test stand"** (`english-developer-style` §4a). It has no source at the base: `git grep -i '\bstands?\b'` finds nothing outside handovers. The code's word for these parts is "harness" (`e2e-harness`, "Kind end-to-end harness"). The change also uses "stand" in a second sense, the target environment: "a real stand", "your stand", "the stand the goldens were recorded on". Carriers include:
  - the chart name `authz-test-stand`, `TEST_STAND_CHART`, `test-stand-files`, `test-stand-values.yaml`;
  - `values.yaml:1-2` and `:79`;
  - chart `README.md:1,8-9,38-56`;
  - the transfer `Dockerfile:2`;
  - `test/k8s/README.md` and the commit messages.

  Request: use "harness" for the parts. Use "environment" (or "cluster") for the target. Or define "test stand" once in the chart README and use it in that one sense only.
- **Uncommented expression at `templates/suite.yaml:68`.** Neither the `dig "ephemeral-storage" "256Mi"` fallback nor the choice to tie `sizeLimit` to the container's limit is explained. The substance of this is filed under item 3 (limits).
- **Taste:** `main.go:37-38` narrates the change ("as it did before the default route existed"). "Answers an unrouted request 404" is enough on its own.

## Item 2: claimed cases covered

Claimed cases from the commit messages, with what covers each:

| Claimed case | Covered by |
| --- | --- |
| Unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| Routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| Route with no responses falls to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` (panics on the base: index -1) |
| Route with no responses falls "or to 404" | **none** (item 3) |
| Without `*`, an unrouted path is 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| Sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` kept as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` takes `*` | Tests write `routes` directly. Taste: a case through `handleConfigure` would pin the wire form. |
| Chart parts off by default | none in CI. Rendering with no values gave 0 objects. |
| Keycloak restarts when a realm file changes (checksum) | none |
| Stubs, emulator, Secret, suite as a `helm test` hook; `make e2e-*` and `parity-*` targets | CI `kind-e2e`, `kind-parity` |
| `make test-stand-files` | CI "Chart lint and render" |
| Merge of user files, profile fields, duplicate username or id fails the build | **none**: no user file exists, so CI never runs the merge (my `jq` run on a sample user gave `R29LevelM2M`) |
| Transfer image with three charts | built by the dev config; contents not checked |
| Commit 3: non-root, seccomp, drop ALL, no escalation, read-only except Keycloak, `/tmp` emptyDir, labels | **none** (my render confirms them, but nothing in CI asserts them) |
| "the stand starts in a namespace that enforces `restricted`" | **none**: no harness labels a namespace `pod-security.kubernetes.io/enforce` |

Requests for the gaps:

- **Restricted Pod Security Standard (commit 3).** Add `test/scripts/test-chart-render.sh` cases over both values files. Assert the four restricted fields on every Pod and container, `readOnlyRootFilesystem: true` everywhere except `keycloak`, and the label set. Also create the kind namespaces with `pod-security.kubernetes.io/enforce=restricted`, so CI proves the README claim.
- **Realm merge.** Add a fixture user file (or a build-only check) that exercises the profile defaults and the duplicate failure.

Commands the change tells someone to run:

| Command | Runs in | Finding |
| --- | --- | --- |
| `make test-stand-files`, `make e2e-*`, `make parity-*`, `helm lint …` | CI | none |
| Subset `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false` (local-integration-tests) | none | I rendered it and both env values came out as intended; no finding |
| `docker create/cp/rm` from the transfer image (chart README) | none | `docker create` with no start works on a `FROM scratch` image; no finding |
| `helm test authz-test-stand --timeout 15m --logs` (chart `README.md:64`) | none | **Substantive**, below |

- **`helm test --logs` fails on this chart.** `--logs` "dump[s] the logs from test pods". In Helm 3.15.2, `GetPodLogs` (`pkg/action/release_testing.go:127`) calls `Pods().GetLogs(h.Name)`, and `h.Name` here is the Job name, `parity-suite`. No Pod has that name, so the command returns "unable to get pod logs for parity-suite" and exits non-zero even after a passing suite. I could not check Helm 4.3. `Makefile:96` ("It prints the log only at the end") assumes the same flag works. Request: run the documented form on Helm 3 and Helm 4, or replace it with `kubectl logs job/<name>`.

Hunks no commit message claims:

- `test/svt/common/compose/docker-compose.yml:3` bumps Keycloak from `26.0` to `26.3.5@sha256:…` for the SVT stack.
- `parity-realm.json` adds far more than "a second tenant realm, parity-mt-b": roles `ROLE_MT_*`, clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`, a `level` mapper, and users `mt-a`, `mt-a-admin`, `parity-r29-scope`, `parity-r30-scope`, plus service accounts. Nothing at HEAD uses them.
- `.github/docker-dev-config.json:12-26` makes ordinary CI build and publish three more images. The message claims only the release.

Request: claim each hunk with the run that checks it, or move it to its own change. For the realm, that change could be the one with the cases that use it, as the pip-stub commit already does for its stub instance.

## Item 3: boundaries, partitions, and the negative control

**pip-stub.** A route with no responses and **no** default route, which the message claims answers 404, has no row. The rows with an empty route always set a default route. Rule-engine precedence over the default route is claimed at `main.go:29-31` but no test configures a rule together with `*`. The control rows (no default, empty default) do pass on the base. Request: add those two rows.

**State left on an existing cluster.** A kind cluster set up by the base harness holds objects created with `kubectl apply`. Among them: `deploy/keycloak`, `cm/keycloak-realms`, `secret/authz-agent-client-credentials`, `sa/runtime-suite`, the stub Deployments and Services, and in parity `cm/pip-mock-config`, `deploy/idp`, `deploy/pip-mock`. They carry no Helm ownership metadata, so `helm upgrade --install authz-test-stand` stops with "invalid ownership metadata". Every CI run starts from a fresh cluster, and no document names a remedy. Request: run `e2e-harness` on a base-commit cluster, or document deleting the namespace or `make e2e-down`.

**Mechanisms replaced** (the old timings come from the base Makefile):
- **Suite run** (`run-suite`, `Makefile:96-106`).
  - Old: on the faults the troubleshooting table names (`ErrImageNeverPull`, or a Pod that never becomes Ready), `wait --for=condition=Ready pod … --timeout=3m` failed after about 3 minutes and named the Pod.
  - New, same fault: `wait --for=create` passes and the log loop runs out after about 3 minutes (90 × 2 s plus calls). `logs -f` then fails, and `wait $helm_pid` blocks until `helm test --timeout 15m` or the Job's `activeDeadlineSeconds: 900` ends it. That is about 15 minutes, and Helm's message gives no reason from the Pod's waiting state. A `CreateContainerConfigError` caused by the new `runAsNonRoot` (an image with a non-numeric `USER`) takes the same path.
- **Harness wait.** A missing stub image failed after 2 minutes under `rollout status deploy/pip-stub --timeout=2m`. It now fails after 10 minutes under `--wait --timeout 10m`.

No sentence in the change accepts either delay. Request: a run of each fault with its duration and output, and a deadline that kills `helm test` once the log loop runs out, printing `kubectl describe pod -l job-name=<job>`.

**Limits.**
- `helm test --timeout 15m` is fixed at `Makefile:102` and in the chart `README.md:64`. The Job's `activeDeadlineSeconds` is a documented setting (`values.yaml:99`, `900`). The CI job allows 30 minutes, which also covers harness and install. If `activeDeadlineSeconds` is raised past 900, Helm's 15 minutes fires first, so the raised value has no effect. Request: derive the Helm timeout from the value, or document that the two are coupled. At the defaults, `-test.timeout 600s` fires first, as it should.
- `emptyDir.sizeLimit` (`suite.yaml:68`) equals the container's `ephemeral-storage` limit, which in a one-container Pod is the Pod's limit. The Pod limit also counts logs, so the `sizeLimit` never fires first, and the `256Mi` fallback is used by neither values file. Request: drop `sizeLimit`, or set it below the container limit, with a comment saying which limit is meant to fire.

**A setting that now reaches a new consumer.** `E2E_HELM_ARGS` now goes to the stand too. The stand reads two of the same keys as the agent and policy-admin charts: `TAG` and `IMAGE_PULL_POLICY`.
- The documented example, `IMAGE_PULL_POLICY=Never`, is harmless: Keycloak has its own `idp.imagePullPolicy`.
- `--set TAG=<x>`, meant for the two product images, now makes the stand ask for `local/pip-stub:<x>`, `local/tenant-manager:<x>`, and `local/authz-runtime-suite:<x>`, which `e2e-images` never builds (it always tags `:ci`). The result is `ErrImageNeverPull` and a 10-minute wait.

Request: give the stand its own variable (for example `TEST_STAND_HELM_ARGS`), or run with `TAG` set.

## Item 3a: level, placement, and the environment

- The pip-stub tests are in-process (`httptest`), sit beside the existing tests and share `resetState`, and the `go-build` workflow runs them. No finding there.
- The chart's own claims (both commits) have no test at the smallest level that can observe them: `helm template` assertions in `test/scripts/test-chart-render.sh`, which CI already runs. The request is the one filed under item 2.
- **Taste:** `kubectl wait --for=create` needs kubectl 1.31 or later, and the prerequisites table in `docs/local-integration-tests.md` gives no version. On an older client the log is not streamed, but the exit code still comes from `helm test`.

## Item 4: names by content, not by position

None. I checked the subtest names, the Go test function names, the Makefile macro arguments (positional by nature), and the headings of the changed docs.

## Item 5: the failure report

None. Every new Go assertion prints got and want with its input (`GET %s = %d %s, want %d %s`, `statuses of /a, /b, /a = %v, want %v`, `recorded %d calls, want 1`). The subtests are named by condition.

## Item 6: what the writer says it verified

No commit states a red run on the base or a mutation result. The pip-stub message describes the base defect (index -1) but does not say the new row was seen failing. Neither Helm commit states a run on kind or under an enforcing namespace.

## Item 7: siblings of the change

- `README.md:59` still says "CI builds both via `.github/docker-dev-config.json`", which now lists five images.
- The troubleshooting row at `docs/local-integration-tests.md:190` says `make e2e-harness` "times out at `rollout status deploy/keycloak`". That target no longer runs `rollout status`; it runs `helm … --wait`.

Request: update both. Siblings I checked with no finding:
- `run-suite` has two call sites, both covered.
- The labels and security-context helpers reach every object and container in both renders.
- `e2e-logs` and `parity-logs` only read stdout through `kubectl exec`, which a read-only root still allows.
- The `echo` rule does not carry `requestUri`, and should not: its body is compared with goldens.
- The parity suite's sidecar write already failed silently on its root-owned `testdata/`, so the read-only root changes nothing there.
- The `qubership-core-base` entrypoint started read-only in my run, but the local images report base `alpine-2.5.10`, not the `2.4.2` the Dockerfiles pin.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Default-route comments leave out the empty-route case | Substantive | `test/integration/pipstub/main.go:34,122` | 1 |
| Dense sentences in the `RequestURI` comment and the test comment | Substantive | `main.go:74`, `main_test.go:222` | 1 |
| Selector comment gives the wrong reason; the real one is immutability | Substantive | `helm-templates/authz-test-stand/templates/_helpers.tpl:2` | 1 |
| Docs say the harness installs and waits for the suite Job | Substantive | `docs/local-integration-tests.md:104` | 1 |
| Realm role description names a test that does not exist | Substantive | `test/k8s/parity/idp-seed/parity-realm.json:30` | 1 |
| "stand" / "test stand" coined, used in two senses | Substantive | chart name, `values.yaml:1`, chart `README.md:1` | 1 |
| Package comment narrates the change | Taste | `main.go:37` | 1 |
| `helm test --logs` reads a Pod named after the Job hook and fails | Substantive | `helm-templates/authz-test-stand/README.md:64`, `Makefile:96` | 2 |
| Restricted-profile and chart claims have no render assertion or enforcing run | Substantive | `helm-templates/authz-test-stand/README.md:8` | 2 |
| Realm merge, profile defaults, and duplicate check never exercised | Substantive | `build/authz-agent-transfer/Dockerfile:31` | 2 |
| Unclaimed hunks: SVT Keycloak bump, extra parity realm content, dev-CI publishing | Substantive | `test/svt/common/compose/docker-compose.yml:3`, `parity-realm.json`, `.github/docker-dev-config.json:12` | 2 |
| No test configures `*` through `/pip-stub/configure` | Taste | `main_test.go:225` | 2 |
| Missing rows: empty route with no default; rule ahead of the default route | Substantive | `main_test.go:225` | 3 |
| Existing kind clusters hit a Helm ownership conflict; no remedy documented | Substantive | `Makefile:85,149` | 3 |
| Suite and harness faults fail after about 15 and 10 minutes instead of 3 and 2, and say less | Substantive | `Makefile:96-106` | 3 |
| Fixed 15-minute `helm test` timeout makes a raised `activeDeadlineSeconds` useless; `sizeLimit` never fires first | Substantive | `Makefile:102`, `templates/suite.yaml:68` | 3 |
| `E2E_HELM_ARGS` `TAG` now reaches the stand's local images | Substantive | `Makefile:48` | 3 |
| `kubectl wait --for=create` needs kubectl ≥ 1.31; no version stated | Taste | `Makefile:103` | 3a |
| README count "both" and troubleshooting row now stale | Substantive | `README.md:59`, `docs/local-integration-tests.md:190` | 7 |

Three checks could not be done. The drift script does not parse Go or YAML, so I reviewed the members by hand. `godoc-authoring` was not among the provided skills. Helm 4.3's `helm test --logs`, the base `2.4.2` entrypoint, and the restricted admission check all need a cluster or that image, which this review did not have.
