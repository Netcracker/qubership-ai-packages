# Final review of `58316ca..HEAD` (4 commits)

There was no task statement, so I took the claimed cases from the four commit messages. I loaded `test-authoring` and `english-developer-style`; no doc-comment skill was given for Go, so item 1 uses the code alone. The drift script ran and printed nothing, because it only parses Java, Kotlin, Groovy, and Scala. I checked the Go members and the chart and Makefile comments by hand. `AGENTS.md` has no test stack line; I propose `Tests: Go testing (engine and assertions)` (test-authoring §0).

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:122` and `:34-35` miss a case.** The `defaultRoute` comment and the package comment both say the default route answers "every request whose path has no route of its own". The code at `:241-244` also sends it a path whose route has an empty `Responses` list, and the commit message and the subtest "a routed path with no responses gets the default answer" both claim that case.
- **`main.go:37-38` narrates the change.** "A stub nobody configures with it answers an unrouted request 404, as it did before the default route existed." The rewrapped "behaviour is exactly as before" at `:31-32` has the same shape. Item 1 allows this only in a regression test's comment.
- **`Makefile:100` contradicts the chart README.** It says "`helm test` … prints the log only at the end". `helm test` as the Makefile calls it, with no `--logs`, prints no log at all. The chart README (`:61-62`) says that even with `--logs` Helm 4 prints nothing for a Job. Helm 3.15.2's `GetPodLogs` (`pkg/action/release_testing.go:127-130`) does ask for a Pod named after the hook, so the README is right and the Makefile comment is wrong.
- **`docs/local-integration-tests.md:104` lists the suite Job among what `e2e-harness` installs and waits for.** The Job is a `helm test` hook and is not created at install. `test/k8s/README.md` says so: "installing the stand does not start it".
- **`Makefile:49-50` and chart `README.md:69-70` give an incomplete recipe for a longer suite.** Both say to raise the helm wait together with `suite.activeDeadlineSeconds`. Neither mentions `-test.timeout 600s` in `suite.args`. See item 3.
- **Taste:** `values.yaml:9-11` lists the images `TAG` applies to as "pip-stub, authz-parity-suite, and tenant-manager". The e2e stand's `authz-runtime-suite` takes `TAG` too, through `suite.imageRepository`.

## Item 2: claimed cases covered

| Claimed case (commit) | Test or run |
| --- | --- |
| `*` default route answers an unrouted path (9d25da7) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| Routed path keeps its own answer | `…/a routed path keeps its own answer` |
| No `*` configured → 404 as before | `…/an unrouted path without a default route is 404` |
| Route with no responses falls through to the default route | `…/a routed path with no responses gets the default answer` |
| Route with no responses falls through **to 404** when there is no default route (the old index -1 crash) | **none** |
| "`/pip-stub/configure` now takes the path `*`" | **none**. The tests write `routes[defaultRoute]` directly; `handleConfigure` is never called. |
| Default route serves its responses in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| Chart parts off by default; Keycloak restarts when a realm file changes | `helm lint` in CI. I rendered both values files and confirmed `checksum/realms` changes when a realm file changes; no repository test checks either. |
| `profile.jq` fills in first name, last name, and email; the build fails when a user is declared twice (8b85515) | **none**. `testdata/realm/` holds only `README.md`, so no build ever runs `profile` or the duplicate checks. I ran `profile.jq` by hand with jq 1.8: `parity-r29-level-m2m` becomes `R29LevelM2M`, as the comment says. |
| The stand starts under the `restricted` Pod Security Standard (17b17fc) | **none**. The kind namespaces come from `--create-namespace` with no `pod-security.kubernetes.io/enforce` label. All four repository images use a numeric `USER 10001`, so `runAsNonRoot` can be checked. |
| app.kubernetes.io and `helm.sh/chart` labels; selectors keep `app` | Render only; no assertion. |
| A suite can outlast 15 minutes (5dcb6be) | **none**, and it cannot as configured (item 3). |

Commands the change tells someone to run:

| Command | Runs elsewhere? |
| --- | --- |
| `make test-stand-files` | CI `integration-tests.yaml:77`. |
| Chart README step 1: `docker create … transfer:<version> true`, `docker cp`, `docker rm` | **none**. No job pulls or inspects the transfer image. |
| Chart README step 2: `helm upgrade --install authz-test-stand ./charts/authz-test-stand --set TAG=<version> -f my-test-stand-values.yaml` | **none**. I rendered it offline with the parity values minus the kind keys, and it pulls `ghcr.io/…:<version>` with `IfNotPresent`. The outcome depends on those images existing under that version, which only a release run shows. |
| Chart README step 3: `helm test … --timeout 15m` then `kubectl logs job/parity-suite` | Close to `run-suite`, which differs by `-f`. The chart sets no `ttlSecondsAfterFinished`, and `before-hook-creation` keeps the Job, so the log stays readable after the run. I accept it. |
| `docs/local-integration-tests.md:139-140`: `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false` | **none**. Its outcome depends on `--reuse-values` keeping the `suite.env.BASE_URL` that `make e2e-harness` set; I did not run it against a release. |
| `make e2e-down` as the remedy for the "invalid ownership metadata" error | `e2e-down` runs `kind delete cluster`, so the remedy works for both namespaces. |

Hunks no commit sentence claims:
- `test/svt/common/compose/docker-compose.yml`: Keycloak goes from `26.0` to `26.3.5@sha256…` in the SVT compose stack, which the change does not otherwise touch.
- `test/k8s/parity/idp-seed/parity-realm.json`, +318 lines. It adds `ROLE_MT_*`, the clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`, and the users `mt-a`, `mt-a-admin`, `parity-r29-scope`, and `parity-r30-scope`. The commit claims only "a second tenant realm, parity-mt-b", and `git grep` finds no case under `test/` that uses any of these names.
- `.github/docker-dev-config.json`: the three new dev builds. The commit claims only the release, through `.qubership/docker.cfg`.
- `REALM-DESCRIPTION.md`: the issuer corrected to `/auth/realms/...`. The old manifest already used `/auth`, so this fixes a stale doc rather than reflecting a code change.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub.** The sequence clamp and the empty default route are covered. Two cases are missing:
  - A routed path with an empty `Responses` list and no `*` route. This is the input that crashed on the base commit.
  - The control for precedence: a request that matches a rule while `*` is configured should get the rule's answer. `TestHandlePIP_RuleThenLegacyFallback` (`main_test.go:135`) has no default route.
- **State left by an earlier version.** The harness objects that `kubectl apply` created are named, the quoted error shows the writer met them, and `make e2e-down` deletes them. No finding.
- **Values users already pass.** `E2E_HELM_ARGS` now reaches the test-stand install too (`Makefile:90`, `:155`). That chart shares two key names with the agent and policy-admin charts: `TAG` and `IMAGE_PULL_POLICY`.
  - `E2E_HELM_ARGS='--set TAG=1.2.3'`, meant to test published product images, now also asks for `local/pip-stub:1.2.3`, `local/tenant-manager:1.2.3`, and `local/authz-*-suite:1.2.3` with `IMAGE_PULL_POLICY: Never`. Nothing builds those images.
  - `--set IMAGE_PULL_POLICY=Always` makes the stand try to pull `local/...` from a registry.
  - The documented example, `IMAGE_PULL_POLICY=Never`, is harmless.
  - The request: give the stand its own variable, for example `TEST_STAND_HELM_ARGS`, or stop passing `E2E_HELM_ARGS` to it.
- **Limits on the suite run.** Four limits bound the same work:
  - `-test.timeout 600s` in `suite.args`, at `values.yaml:96` and `test/k8s/test-stand-values.yaml:56`.
  - `suite.activeDeadlineSeconds: 900`.
  - `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`, both `15m`.
  - The CI jobs' `timeout-minutes: 30` (`integration-tests.yaml:120`, `:168`). This one starts earlier: cluster creation, the image builds, a harness wait of up to 10 minutes, and two 5-minute installs all come out of the same budget.

  If you raise `activeDeadlineSeconds` to 1800 and the timeout variable to `30m`, as the Makefile comment says, the suite still dies at 10 minutes, so the commit's headline case cannot happen. In CI the job limit fires before any raised value too. At the defaults the innermost limit does fire first, but the helm wait (900 s) and the Job deadline (900 s) are equal, so which of those two fires first is a race. The request: derive `-test.timeout`, the Job deadline, and the helm wait from one value, each with a margin, and name the CI job limit in the comment.

## Item 3a: level, placement, and the environment

The Go tests are small, sit beside the existing `TestHandlePIP_*` tests, and reuse `resetState`. They pass (`go test ./...`, run as a consistency check). The chart behaviors can all be seen in one process with `helm template`: the security contexts, the labels, the `fail` messages for missing files, the checksum annotation, and the `emptyDir` `sizeLimit`. `test/scripts/test-chart-render.sh` already asserts this kind of thing for the other two charts, but it has no test-stand case. CI only runs `helm lint` on the new chart. The restricted Pod Security claim is a cross-boundary behavior, and it needs a namespace labeled `enforce=restricted` in the kind jobs.

## Item 4: names by content, not by position

No finding. The test names, subtest names, and messages all name content. One taste note: `values.yaml:11` says "below" where it could name `idp.image`.

## Item 5: the failure report

No finding. Every comparison uses `t.Errorf` or `t.Fatalf` and prints got and want with the input (`GET %s = %d %s, want %d %s`; `statuses of /a, /b, /a = %v, want %v`). Subtests are named by condition.

## Item 6: what the writer says it verified

The commits state no red run on the base commit and no mutation verdict for the pip-stub tests. The subtest "a routed path with no responses gets the default answer" would crash with index -1 on the base commit, but the commits don't say so. No kind run of the chart is stated. The Helm 4.3.1 and 3.22.1 observations in 5dcb6be are the only run evidence, and the Helm 3 half agrees with the 3.15.2 source.

## Item 7: siblings of the change

- **`run-suite`:** both callers were updated.
- **The new timeout variables:** `test/k8s/README.md:66-71` lists the overrides (`KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, `E2E_ARTIFACTS`, `E2E_HELM_ARGS`, `E2E_BASE_URL`, `PARITY_AC_BASE_URL`) but not `E2E_SUITE_TIMEOUT` or `PARITY_SUITE_TIMEOUT`.
- **Image count:** `README.md:59` still says "CI builds both via `.github/docker-dev-config.json`", which now lists five images.
- **Troubleshooting row:** `docs/local-integration-tests.md:190` names `make e2e-harness` or `make parity-harness` in its symptom, but its action says only "then `make e2e`". It has no step for the parity path (`make parity`).
- **kubectl version:** `run-suite` uses `kubectl wait --for=create` (`Makefile:108`), which kubectl 1.31 added. The prerequisites table states no minimum kubectl version. On an older kubectl, the `&&` skips the log polling, so the log is not streamed, though helm still sets the exit code.

## Findings

| Finding | Label | Location | Request |
| --- | --- | --- | --- |
| `-test.timeout 600s` caps the suite below the deadline and the helm wait; the CI 30-minute job limit encloses everything; the helm wait and the Job deadline are equal at the defaults | Substantive | `Makefile:49-52`, chart `values.yaml:96-99`, `test/k8s/test-stand-values.yaml:56`, `integration-tests.yaml:120,168`, chart `README.md:69` | Derive the three from one value with margins, and name the CI limit |
| `E2E_HELM_ARGS` now reaches the stand; `TAG` or `IMAGE_PULL_POLICY` meant for the product charts asks for images nothing builds | Substantive | `Makefile:90,155` | A setting of the stand's own, or a run with `--set TAG=<v>` |
| No test or run under an enforcing restricted namespace | Substantive | 17b17fc; `integration-tests.yaml` kind jobs | Label the kind namespaces `enforce=restricted`, or add render assertions plus a server dry-run |
| No render assertions for the new chart | Substantive | `test/scripts/test-chart-render.sh` | Cases for the security contexts, labels, `fail` messages, and checksum |
| `profile.jq` and the duplicate-user checks never run in any build | Substantive | `build/authz-agent-transfer/Dockerfile:338-352` | A fixture user file run through the stage, or a jq test |
| Unclaimed hunks: the SVT Keycloak bump, the parity-realm clients and users no case uses, the dev-config builds | Substantive | `test/svt/common/compose/docker-compose.yml:3`, `parity-realm.json`, `.github/docker-dev-config.json` | A sentence that claims each one, or move them to their own change |
| Routed path with empty responses and no `*` → 404 is untested | Substantive | `main_test.go:225` | Add the subtest |
| A rule wins over `*` is untested | Substantive | `main_test.go:135` | Add a control with `*` configured |
| `*` registered through `/pip-stub/configure` is untested | Substantive | `main_test.go:225-262` | Configure `*` through `handleConfigure` in one test |
| Default-route comments omit the routed-but-empty case | Substantive | `main.go:34-35,122` | Name it |
| Docs say `e2e-harness` installs and waits for the suite Job | Substantive | `docs/local-integration-tests.md:104` | Drop "and the suite Job", as `test/k8s/README.md` does |
| Makefile says `helm test` prints the log at the end | Substantive | `Makefile:100` | Say that `helm test` prints no log for a Job |
| The transfer-image install steps and the `--reuse-values` subset command were never run | Substantive | chart `README.md:39-59`, `docs/local-integration-tests.md:139-140` | One run of each documented form |
| The troubleshooting row's action covers only `make e2e` | Substantive | `docs/local-integration-tests.md:190` | "then `make e2e` or `make parity`" |
| Override list misses the two timeout variables | Substantive | `test/k8s/README.md:66-71` | Add them |
| "CI builds both" | Substantive | `README.md:59` | Restate the count |
| `kubectl wait --for=create` needs kubectl 1.31+, which the prerequisites don't state | Substantive | `Makefile:108`, `docs/local-integration-tests.md` prerequisites table | State the minimum version, or poll without `--for=create` |
| Package comment narrates the change ("as it did before…", "exactly as before") | Substantive | `main.go:31-32,37-38` | State the current behavior |
| `TAG` image list omits the runtime suite | Taste | chart `values.yaml:9-11` | Name the suite image generally |
| "below" where `idp.image` is meant | Taste | chart `values.yaml:11` | Name the key |

The review did not run anything on a Kubernetes cluster: not `make e2e` or `make parity`, not the transfer image, and not Helm 4's `--logs` behavior. It ran `make test-stand-files` only as a hand copy of the files into a scratch chart for `helm lint` and `helm template`. The drift script cannot parse Go, YAML, or Makefiles, and the prose was not reviewed for style alone.
