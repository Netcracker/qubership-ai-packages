# Final review: `58316ca..HEAD` (4 commits)

There was no task statement, so I took the claimed cases from the four commit messages and the test comments. There was no previous report. The drift script exited 0 and printed nothing, not even for `test/integration/pipstub/main.go`. I did Item 1 by hand over the Go file, the templates, the Makefile and the docs.

Most of the change is Helm, Make and docs, so I loaded `test-authoring` and `english-developer-style`. The only Go is `pipstub`; for the rest I used the §2a analogues and say so under each item.

## Item 1: comments consistent with the code and with each other

- **`docs/local-integration-tests.md:104`** says `e2e-harness` installs "the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` hook (`templates/suite.yaml:21`). Helm does not create it at install and does not wait for it. `test/k8s/README.md` gets this right ("installing the stand does not start it"), so the two pages contradict each other. A reader would expect the harness step to run the suite.
- **The limit comments** (`Makefile:49-51`, `Makefile:104`, chart `README.md:69`) say the suite's limit is `E2E_SUITE_TIMEOUT` together with `suite.activeDeadlineSeconds`. Both suites also pass `-test.timeout 600s` in `suite.args`, and that limit is reached first. Details under Item 3.
- **`README.md:59`**: "CI builds both via `.github/docker-dev-config.json`". That file now lists five images.
- **`test/parity/README.md:70-73`** says the `parity` realm "also holds the users of `suite/testdata/realm/`, so the cases that need those users run", and "their files declare none". That directory holds only `README.md`, so there are no such users and no such files. The commit itself says "none so far".
- **`test/integration/pipstub/main.go:37-38`**: "as it did before the default route existed" describes the change rather than the code (taste).
- I checked the other new comments in `main.go` (`defaultRoute`, the precedence paragraph, `RequestURI`), the comments in `_helpers.tpl`, `idp.yaml`, `suite.yaml` and `values.yaml`, and the `REALM-DESCRIPTION.md` rewrite against the code. They hold.

## Item 2: claimed cases covered

**pip-stub (9d25da7)**

| Claimed case | Test |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| A routed path keeps its answer | `…/a routed path keeps its own answer` |
| A route with no responses falls through to the default | `…/a routed path with no responses gets the default answer` |
| A route with no responses and no default answers 404 (the old index −1 crash) | **none**: the 404 cases use an unrouted path |
| No `*` means 404 as before | `…/an unrouted path without a default route is 404` |
| Sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` is kept as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` accepts `*` | Not through `handleConfigure`. Its neighbours also seed `routes` directly, and `handleConfigure` stores any path unchanged, so this is acceptable |

**Test-stand chart (8b85515, 17b17fc)**

| Claimed case | Coverage |
| --- | --- |
| Each part off by default; the two harness values files | `helm lint` in CI. I linted and rendered both files on Helm 4.3.0 against hand-generated `files/`: both clean |
| Keycloak restarts on a realm change | No repo test. I checked it by rendering: changing one realm file changes `checksum/realms` |
| Users of `testdata/realm/` merged; `profile.jq` fills names and email; the build fails on a duplicate username or id | **none**: the directory has no user files, so `profile` and both `jq -e` checks never run on any input |
| `parity-mt-b` realm | Imported; no test uses it yet |
| Release publishes three more images | No dry-run evidence stated |
| Stand starts under the restricted Pod Security Standard | **none**: no namespace in the Makefile or CI enforces `restricted`, and no render assertion checks the security contexts |
| `app.kubernetes.io/*` labels on every object; selectors keep `app:` | None beyond lint |
| OpenShift restricted SCC | Not run, and not runnable here |

**Commands the change tells someone to run**

| Command | Where it runs |
| --- | --- |
| `make test-stand-files`, `make e2e-*`, `make parity-*` | CI jobs, Helm v4.3.1 |
| Chart README step 3: `helm test … --timeout 15m` then `kubectl logs job/parity-suite` | The same form runs via `run-suite` in CI on Helm 4 only |
| Same step on Helm 3 | **none**. The README names Helm 3 behaviour; Helm 3 waits on a Job test hook, but this form was not run there |
| Chart README steps 1–2: `docker create/cp` from the transfer image; `helm upgrade --install … --set TAG=<version>` with published images | **none**. The outcome depends on the published `qubership-authz-*` images and on the transfer image's `files/`, and nothing builds or pulls those in CI |
| `docs/local-integration-tests.md:135` subset: `helm … upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` | **none** |
| `make e2e-down` as the ownership-error remedy | **none** (see Item 3) |

**Hunks no commit sentence claims**

- `test/svt/common/compose/docker-compose.yml`: Keycloak `26.0` → `26.3.5@sha256:…`.
- `.github/docker-dev-config.json`: three more dev builds. The commit names only `.qubership/docker.cfg`.
- `test/k8s/parity/idp-seed/parity-realm.json` (+318 lines): users `mt-a`, `mt-a-admin`, `parity-r29-scope`, `parity-r30-scope` and four `service-account-parity-m2m-tenant-*` clients. The commit claims only the separate `parity-mt-b` realm, and nothing outside the realm files and READMEs uses these users.

## Item 3: boundaries, partitions, and the negative control

**Limits on the suite's run time.** Four limits bound the same run:
- `-test.timeout 600s` in `suite.args` (`values.yaml:95-96`, `test-stand-values.yaml:55-56`);
- `suite.activeDeadlineSeconds: 900`;
- `helm test --timeout` from `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT` = 15m;
- the `run-suite` log wait.

At the defaults, `go test` stops the run at 10 minutes. The commit's case is "a suite given a longer deadline in its values", and following `Makefile:49-50` (raise the timeout together with `activeDeadlineSeconds`) still ends at 600 s, because `-test.timeout` caps both settings. Separately, Helm's clock starts when it creates the Job, which is no later than the Job's `startTime`. With the two values equal, Helm's timeout can fire before the Job's own deadline, so the Job's `DeadlineExceeded` report can be hidden. "No shorter than" (`Makefile:104`, chart README) allows exactly that tie.

**Inherited state.** The `invalid ownership metadata` remedy is documented but not shown run on a cluster an older `make e2e` or `make parity` set up. The row at `docs/local-integration-tests.md:190` names `parity-harness` in its symptom, but its action reruns only `make e2e`. `test/parity/README.md` carries no remedy.

**`E2E_HELM_ARGS` now reaches the test-stand chart.** The keys it shares with the agent and policy-admin charts are `TAG` and `IMAGE_PULL_POLICY`:
- `IMAGE_PULL_POLICY` (the documented example) is harmless.
- `--set TAG=x`, which a user passes to test agent images tagged `x`, now also asks for `local/pip-stub:x`, `local/tenant-manager:x` and `local/authz-runtime-suite:x`. `e2e-images` never builds those.

**Pip-stub partitions:**
- Missing: a routed path with empty `Responses` and no `*` route. This is the old crash path and should answer 404.
- Missing control for the rules mode (`PIP_STUB_CONFIG`, as `pip-mock` uses it): a request that a rule matches while `*` is set should get the rule's answer. `TestHandlePIP_RuleThenLegacyFallback` has no `*` route.
- Present: boundaries for an empty default route and for an unconfigured stub.

**Chart invalid partitions.** None of these is tested:
- `tenantManager.tenants` empty;
- an instance with no `port`;
- a missing realm or rule file (the `fail` messages);
- a missing `clientCredentials.username`.

## Item 3a: level, placement, and the environment

- Pip-stub tests are small (`httptest`, in process). They sit beside the existing `TestHandlePIP_*` tests and share `resetState`. `go test ./...` in `test/integration/pipstub` passes.
- The smallest level for the chart is `helm template`, and the repository already has `test/scripts/test-chart-render.sh` for it. That script has no line for `authz-test-stand`. The security contexts, the labels and selectors, the `/tmp` emptyDir and the `fail` paths are observable there, but only lint covers them. Finding.
- The PSS claim is a cross-boundary behaviour (admission). The CI kind job could check it by creating the namespace with `pod-security.kubernetes.io/enforce=restricted`, and does not. Finding.

## Item 4: names by content, not by position

None. I checked the subtest names, the test names, the README and doc headings, and the Makefile comments. The `$(1)…$(4)` parameter list in `run-suite` names Make's own positional arguments, which have no other names.

## Item 5: the failure report

None. Every new assertion in the three new tests uses `t.Errorf`/`t.Fatalf` with got and want printed in Go order (got first). The table cases carry descriptive names, not indexes, and no message repeats a test name.

## Item 6: what the writer says it verified

No red run on the base commit and no mutation verdict is stated for the pip-stub tests. The commit messages quote the error strings for Helm 3.22.1/4.3.1 `--logs` and for the ownership error, which suggests those were observed. No run of the stand under an enforcing namespace, and no run of the remedy, is stated.

## Item 7: siblings of the change

- Members added to sets:
  - **Images.** `.qubership/docker.cfg` and `docker-dev-config.json` both gained the three images, and `README.md` names them for the release. But `README.md:59` still counts the dev builds as "both".
  - **`E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT`.** No doc lists them: the override sentence in `test/k8s/README.md` still names `KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, `E2E_ARTIFACTS`, `E2E_HELM_ARGS`, `E2E_BASE_URL` and `PARITY_AC_BASE_URL` without them. Finding.
- I grepped every deleted manifest name (`runtime-suite-job`, `keycloak.yaml`, `pip-mock.yaml`, `m2m-credentials`, `keycloak-realms`, `parity-realms`, and others) outside `docs/handovers`. No stale reference is left.
- Two paths show the ownership-error symptom (e2e and parity). The remedy row covers only one (see Item 3).

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| `-test.timeout 600s` in `suite.args` caps both documented limits, so raising `E2E_SUITE_TIMEOUT` and `activeDeadlineSeconds` has no effect past 10 min; Helm timeout equal to the Job deadline is a tie that can hide `DeadlineExceeded` | Substantive | `Makefile:49-51,104`; `values.yaml:92-99`; `test/k8s/test-stand-values.yaml:55-56`; chart `README.md:69` | Derive the limits from one setting (for example `-test.timeout` from `activeDeadlineSeconds` minus a margin, with Helm's timeout plus a margin), or document all three and make "no shorter than" strictly longer |
| Restricted Pod Security Standard claim never exercised | Substantive | `Makefile:89-90,154-155`; `templates/_helpers.tpl` | Create the harness namespaces with `pod-security.kubernetes.io/enforce=restricted` in CI, or add a server-side dry-run against such a namespace |
| No render assertions for `authz-test-stand` | Substantive | `test/scripts/test-chart-render.sh` | Assert, at least: security contexts on every Pod and container, selectors `app:` only, and the `fail` paths (missing realm or rule file, empty tenants, missing port) |
| Doc says `e2e-harness` installs and waits for the suite Job | Substantive | `docs/local-integration-tests.md:104` | Drop "and the suite Job" and match `test/k8s/README.md` |
| `E2E_HELM_ARGS --set TAG=…` now retags the stand's local images, which nothing builds | Substantive | `Makefile:46-48,90,155` | Give the stand its own args variable, or document that `TAG` reaches it and run with such a value |
| Unclaimed hunks: SVT compose Keycloak pin, dev-config builds, extra parity realm users and clients with no consumer | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `.github/docker-dev-config.json`; `test/k8s/parity/idp-seed/parity-realm.json` | Add a commit sentence for each with the run that checks it, or move each hunk to its own change, the realm users to the change with the cases that use them |
| "CI builds both" is now five | Substantive | `README.md:59` | Restate the count or name the images |
| `profile.jq` fill-in and duplicate checks never run on any input; parity README describes users and files that do not exist | Substantive | `build/authz-agent-transfer/Dockerfile:32-46`; `test/parity/README.md:70-73` | Add a fixture user file (or a `jq` test) that exercises `profile` and a duplicate; reword the README to match the empty directory |
| Pip-stub: no case for an empty routed path with no default (404), and no rule-versus-default control | Substantive | `test/integration/pipstub/main_test.go:231-241` | Add the row `/routed`, `[]pipResponse{}`, `nil` → 404, and a test with a rule plus `*` asserting the rule answers |
| Ownership-error remedy names only `make e2e`, is missing from the parity README, and was not shown run on the old state | Substantive | `docs/local-integration-tests.md:190`; `test/parity/README.md` | Name `make parity` too, add the row to the parity README, and state the run of `make e2e-down` on a cluster an older `make e2e` built |
| `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT` missing from the overrides list | Substantive | `test/k8s/README.md` (overrides paragraph) | Add both, with the pairing to `activeDeadlineSeconds` |
| Outside-kind recipe, Helm 3 form, and `--reuse-values` subset command never run | Substantive | chart `README.md:39-67`; `docs/local-integration-tests.md:135-141` | One run of each documented form on the configuration it targets, or note it as unverified |
| Comment narrates the change ("before the default route existed") | Taste | `test/integration/pipstub/main.go:37-38` | State the current behaviour only |

Not checked: no kind cluster, Docker build (`make test-stand-files`, so the chart was linted against hand-generated `files/`), Helm 3, OpenShift, or release run was done. The drift script parsed no members. There was no prose pass for style alone.
