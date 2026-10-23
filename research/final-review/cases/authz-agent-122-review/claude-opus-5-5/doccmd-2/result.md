I have what I need for every item. I didn't change or commit any file; the only scratch files are rendered manifests under the scratchpad.

# Final review: `58316ca..HEAD` (three commits)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages and the test comments alone. The drift script ran and printed nothing: it parses only Java, Kotlin, Groovy and Scala, and this change is Go, Helm, Make, Dockerfile and Markdown. I did item 1 by hand. There is no previous report.

Loaded skills: `test-authoring` (engine and assertions file: `go/testing.md`) and `english-developer-style`. Go has no doc-comment skill in the provided set.

Per test-authoring §0, AGENTS.md has no stack line. I propose adding one: `Tests: Go testing engine and assertions; testify in test/integration/testify`. I edited no file.

## Item 1: comments consistent with the code and with each other

**Go, `test/integration/pipstub/main.go`, checked by hand.**
- **Package comment (changed).**
  - `:35` says the default route answers "in sequence like any other route". `:20` says responses are "served sequentially per path". Read together, a reader expects each unrouted path to get its own sequence. In fact `*` keeps one counter shared by every unrouted path; `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` shows `/a, /b, /a` → `503, 200, 200`. The test's comment states this; the package comment does not.
  - `:37–38` narrates the change: "as it did before the default route existed".
  - The precedence sentence at `:29–31` matches the code: rules, then the path route, then `*`, then 404. A route with an empty `Responses` falls through, which agrees with the commit message.
- **`callRecord.RequestURI` (comment added):** true; `r.RequestURI` is the raw target.
- **`defaultRoute` (comment added):** true; `handleConfigure` stores any path, `*` included.
- **`handlePIP` (code changed, no doc comment):** the inline step comment `:232` is updated and true.

**Make, YAML and Markdown.**
- **`Makefile`, `run-suite` comment:** "`helm test` … prints the log only at the end" is false for the command it describes. `$(2) test authz-test-stand --timeout 15m` has no `--logs`, and Helm 4.3's help says logs are dumped only with `--logs`.
- **`helm-templates/authz-test-stand/values.yaml:7–9`:** lists the images that take `TAG` as "pip-stub, authz-parity-suite, and tenant-manager". The runtime suite image (`local/authz-runtime-suite` in `test/k8s/test-stand-values.yaml`) also takes `TAG`, and the list omits it.
- **`docs/local-integration-tests.md`, `e2e-harness` row:** says it installs "… and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` and is not created at install. `test/k8s/README.md`'s row for the same target correctly leaves the Job out, so the two pages disagree.
- **Checked and consistent:**
  - the `_helpers.tpl` comments against the rendered output;
  - `idp.yaml` probe arithmetic (60 × 5 s);
  - `run-suite` polling (90 × 2 s = 3 min);
  - `.qubership/docker.cfg` against `.github/docker-dev-config.json` (same three additions);
  - the transfer Dockerfile header against its stages;
  - `REALM-DESCRIPTION.md` issuer `/auth` against `KC_HOSTNAME`;
  - `testify/helpers.go` and `testify/Dockerfile` pointers.
- `git grep` finds no remaining reference to the deleted manifests outside `docs/handovers`.

## Item 2: claimed cases covered

| Claimed case | Test |
| --- | --- |
| An unrouted path is answered by `*` | `DefaultRouteAnswersUnroutedPaths/"an unrouted path gets the default answer"` |
| A routed path keeps its own answer (control) | `…/"a routed path keeps its own answer"` |
| No `*` configured → 404 as before | `…/"an unrouted path without a default route is 404"` |
| A route with no responses falls through to the default route | `…/"a routed path with no responses gets the default answer"` |
| A route with no responses, **and no default → 404** | **none.** This is exactly the input that indexed at −1 on the base commit. The only empty-route 404 case uses an unrouted path with an empty `*`. |
| `/pip-stub/configure` takes `*` | Not through the endpoint: tests write `routes[defaultRoute]` directly. `handleConfigure` is unchanged and stores any key, so this is low risk. |
| `requestUri` keeps the target as sent | `RecordsTheRequestTargetAsSent` |
| Every Pod non-root + RuntimeDefault; every container drops ALL, no escalation | No test in the repo. I rendered both values files: every Deployment and Job has all four fields. |
| Read-only root everywhere except Keycloak; `/tmp` emptyDir for the suite | Rendered and confirmed. Runtime behaviour is covered only by the kind CI jobs (see items 3a and 6). |
| Stand starts under **enforced** restricted PSS | **none.** No harness or CI namespace is labelled `pod-security.kubernetes.io/enforce=restricted`. |
| app.kubernetes.io labels + `helm.sh/chart` on every object; selectors keep `app:` | No test. I confirmed it in the render. |
| Keycloak restarts when a realm file changes | **No test.** I confirmed by render: the checksum changes when a realm file is added and is stable across renders. |
| Failure texts `no realm files under files/realms/<realms>/`, `no file files/pip-stub/<file>`, `tenantManager.tenants is required` | **No test.** All three fire with the documented text when rendered. |
| `chart-files` merges users from `testdata/realm/`, fills firstName/lastName/email, fails on a duplicate | **none.** The directory holds no JSON ("none so far"), so CI's `make test-stand-files` exercises only the empty partition of `profile.jq` and the two `jq -e` uniqueness checks. |
| Second tenant realm `parity-mt-b` | Only imported at Keycloak start in `kind-parity`; no case uses it yet. The commit says the cases come later. |
| Release publishes pip-stub, parity-suite, transfer | Config entries are present in both lists; no run (release only). |

**Command lines in the changed files:**

| Command | Promised outcome | What runs the same form |
| --- | --- | --- |
| `make test-stand-files` | `files/` generated | CI `chart` job |
| `helm lint` of test-stand with each values file | lint passes | CI `chart` job. I also ran it locally on Helm 4.3.0 with stand-in files: 0 failed. |
| `make e2e-harness` / `e2e-suite` / `parity-harness` / `parity-suite` | stand up, suite exit status | CI `kind-e2e`, `kind-parity`, on a **fresh** cluster only |
| `docs/local-integration-tests.md`: `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false`, then `make e2e-suite` | runs a subset, no coverage-check failure | **none** |
| `authz-test-stand/README.md`: `docker create/cp/rm` of the transfer image; `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml`; `helm test authz-test-stand --timeout 15m --logs` | charts copied; stand installed from published images; suite log printed, non-zero exit on failure | **none** |
| `build/authz-agent-transfer/Dockerfile` header `docker build … .` | transfer image | image build from `docker-dev-config.json` |

For the two `none` rows:
- **Subset recipe.** It depends on Helm's `--reuse-values`, which Helm 4.3's help confirms, and on Kubernetes expanding `$(RUNTIME_SUITE_RUN)` in `args`, which the render shows. Whether the subset run then passes is not verified.
- **Transfer-image recipe.** It depends on the published tags existing under one version, which is not verifiable offline. `docker create` on a `FROM scratch` image with `true` as the command works because create does not resolve the binary. `helm test --logs` exists in Helm 4.3; Helm 3 is not checked here. The values edits the README lists are not verified on any non-kind stand.

## Item 3: boundaries, partitions, and the negative control

- **Go.** The partitions of the route lookup are present apart from the one missing row in item 2: a routed path with empty responses and no default route. The control (an unrouted path with no `*` → 404, green on the base commit) is present. The sequence clamp is covered for `*`.
- **Pre-existing state: missing.** `e2e-cluster` reuses an existing `authz-e2e` cluster. Namespaces left by the previous Makefile hold objects created by `kubectl apply` under the same names the chart now owns:
  - **e2e:** Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`; Secret `authz-agent-client-credentials`; ServiceAccount and Job `runtime-suite`.
  - **parity:** `idp`, `pip-mock`, ConfigMap `pip-mock-config`.
  - **Effect:** Helm refuses to adopt objects without its ownership metadata, so a developer's first `make e2e-harness` or `parity-harness` after pulling this change should fail. This is inferred from Helm's adoption rule; I did not run it.
  - **Gap:** CI starts from fresh clusters, and no doc names the remedy (`make e2e-down`, or deleting the two namespaces).
- **Restricted PSS:** the enforcing namespace, the mode the commit is about, is never exercised (item 2).

## Item 3a: level, placement, and the environment

- **Go tests:** small, in-process, through `handlePIP`. They sit in the existing `main_test.go` beside the existing tests, reuse `resetState`, and run in `go-build.yaml`. I ran `go test` locally: pass.
- **Chart:** the repository has a render-assertion gate for the other charts (`test/scripts/test-chart-render.sh`). The new chart's checksum restart, failure messages, and security contexts are not asserted there or in a sibling script; CI only lints it.
- **Read-only root:** pip-stub and both suite images start through the `qubership-core-base:2.4.2` entrypoint script. `tenantmanager/Dockerfile` says that script "loads certificates"; the agent and tenant-manager images bypass it. Whether it writes to the root filesystem at start cannot be checked offline (image not cached). The kind CI jobs do run these Pods, so CI on this branch answers it; no run is stated.
- **Admission:** restricted admission exists only across the API-server boundary. The gap is that no CI job enforces it on the harness namespaces.

## Item 4: names by content, not by position

None. The subtest names are by condition ("a routed path with no responses gets the default answer"), and the count claims ("the three charts", "the two services") match what they count.

## Item 5: the failure report

None. The table test prints `GET %s = %d %s, want %d %s` with all four values, the sequence test prints both slices, and the request-target test prints both fields with both wants.

## Item 6: what the writer says it verified

Not stated:
- No red run on the base commit for the new pip-stub cases. "A routed path with no responses gets the default answer" should panic at index −1 on the base commit, but that is not stated.
- No mutation verdict.
- No kind or CI run of the stand under the new security contexts.
- No run against a restricted namespace.

## Item 7: siblings of the change

- **`matchRule`'s `respondSequence` index:** guarded by `len > 0`; the same defect does not apply.
- **Consumers of `/pip-stub/calls`:** `testify/entitlements_test.go`, `testify/pip_admin_test.go`, `parity/suite/pip_control.go`. None decodes with `DisallowUnknownFields`, so the added `requestUri` is safe.
- **`writeRespond` echo:** does not carry `requestUri`. That is not the same defect: the echo body is compared against goldens, and the commit claims the call record only.
- **Every template:** uses the labels and security-context helpers, confirmed by render.
- **`E2E_LOCAL_DEPLOYMENTS` / `PARITY_LOCAL_DEPLOYMENTS`:** still match the instance names.
- **`test/svt/common/compose/docker-compose.yml`:** commit 1 bumps Keycloak from `26.0` to `26.3.5@sha256…`, and no commit message mentions it. That is a dependency bump with no named surface or run (test-authoring §3).

## Findings

| # | Finding | Label | File:line | Requested change |
| --- | --- | --- | --- | --- |
| 1 | `make e2e-harness` / `parity-harness` over a namespace the previous harness created should fail on Helm ownership; no run or doc covers it | Substantive | `Makefile` (`e2e-harness`, `parity-harness`); `test/k8s/README.md` | Run once on a cluster left by `58316ca`, and document the remedy (`make e2e-down` or delete the namespaces), or label/annotate the old objects for adoption |
| 2 | The restricted-PSS claim has no run under an enforcing namespace | Substantive | commit 17b17fc; `Makefile` harness targets | Label the harness namespaces `pod-security.kubernetes.io/enforce=restricted` in CI, or state the run that did |
| 3 | No test for a routed path with no responses and no default route → 404 (the base-commit −1 input) | Substantive | `test/integration/pipstub/main_test.go:233` | Add a row: `"/routed"`, `[]pipResponse{}`, no default → 404 |
| 4 | Package comment implies each unrouted path has its own sequence; it is shared | Substantive | `test/integration/pipstub/main.go:35` | Say the `*` sequence is one counter across all unrouted paths |
| 5 | `profile.jq` merge, profile fill and duplicate check run only on an empty user set | Substantive | `build/authz-agent-transfer/Dockerfile`, `profile.jq` | A fixture user file (or a jq test) that exercises fill-in and a duplicate that fails the build |
| 6 | Chart behaviours (checksum restart, three failure texts, security contexts) have no render assertion beside the existing gate | Substantive | `helm-templates/authz-test-stand/templates/*`; `test/scripts/test-chart-render.sh` | Add render assertions for the test-stand chart |
| 7 | Read-only root for pip-stub and the suites depends on the base-image entrypoint's writes; no run stated | Substantive | `templates/pip-stub.yaml:58`, `templates/suite.yaml:57` | State the green `kind-e2e` and `kind-parity` runs on this branch |
| 8 | `run-suite` comment says `helm test` prints the log at the end; it does not without `--logs` | Substantive | `Makefile` (`run-suite` comment) | Say it prints the log only with `--logs`, after the run |
| 9 | `TAG` comment's image list omits `authz-runtime-suite` | Substantive | `helm-templates/authz-test-stand/values.yaml:7` | Add it, or say "the images this repository builds" |
| 10 | `e2e-harness` row says the suite Job is installed and waited for; it is a test hook | Substantive | `docs/local-integration-tests.md` (`e2e-harness` row) | Drop the Job from the row, as `test/k8s/README.md` does |
| 11 | SVT compose Keycloak bump is unmentioned and unrun | Substantive | `test/svt/common/compose/docker-compose.yml:3` | Mention it in the commit message with the surface it affects, or move it to its own change |
| 12 | Subset and transfer-image recipes have no run of the documented form | Substantive | `docs/local-integration-tests.md`; `helm-templates/authz-test-stand/README.md:39–67` | Run each once as written and say so |
| 13 | Package comment narrates the change ("as it did before the default route existed") | Taste | `test/integration/pipstub/main.go:37` | "…answers an unrouted request 404." |

**Not checked:** I did not run the Go suite against the base commit or any kind or cluster flow (no cluster available), did not build `make test-stand-files` (I rendered with hand-copied stand-in files), did not inspect the `qubership-core-base` or `keycloak:26.3.5` images (Keycloak's numeric user `1000` comes from the cached 26.7 image), and did no prose-style pass.
