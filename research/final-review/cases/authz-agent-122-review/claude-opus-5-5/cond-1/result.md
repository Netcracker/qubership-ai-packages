I've reviewed the three commits (`58316ca..17b17fc`) and found 18 findings: 17 substantive and 1 taste. The most important:

1. **The README's `helm test --logs` command doesn't print the suite log on Helm 3.** Helm 3.15 reads logs from a Pod named after the hook, and here the hook is a Job, so it errors. Helm 4, which CI uses, isn't checked.
2. **Existing kind namespaces will break the new install.** The chart creates objects under the same names the old `kubectl apply` harness used, and nothing tells developers to delete the namespace first.
3. **The suite now fails about 12 minutes later.** When the suite image is missing, the old wait failed after about 3 minutes; the new one waits up to 15.
4. **The restricted Pod Security claim has no test or run**, and the OpenShift setting goes against the agent chart's own setting.

There is no task statement, so I took the claimed cases from the three commit messages. I changed no repository files. The drift script parses only JVM languages, so it reported nothing, and I checked the Go comments by hand. To check the chart I made a copy in the scratchpad and generated its `files/` there with the local `jq`, without running `make test-stand-files` in the checkout. On that copy I ran `helm lint` with both values files and `helm template` (helm v4.3.0), plus `go test` in `test/integration/pipstub`; all passed. With no values the chart renders nothing, as the commit says.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:37-38`** says a stub without `*` answers 404 "as it did before the default route existed". That describes the history of the change, not the code (`english-developer-style` §7, code comments). Request: end the sentence at "answers an unrouted request 404".
- **`main.go:34-35` and `:122-123`** say the default route answers every request "whose path has no route of its own". The change also sends a route with an empty `Responses` list to the default route (`main.go:243`). A reader would expect a 404 there. Request: add "or whose route has no responses" to both comments.
- **`Makefile:95-96`** says `helm test` "prints the log only at the end, so the log is streamed while it runs". The target runs `helm test` without `--logs`, so helm prints no log at all; only the `kubectl logs -f` loop does. Request: "`helm test` prints no log of a Job hook, so the log is streamed while it runs."
- **`helm-templates/authz-test-stand/values.yaml:9-11`** lists the images that use `TAG` as pip-stub, authz-parity-suite and tenant-manager. `suite.imageRepository` can also be the runtime suite (`test/k8s/test-stand-values.yaml:48`), which uses `TAG` too. Request: name the suite image in general instead of the parity suite.

## Item 2: claimed cases covered

No task statement was handed over, so the claimed cases come from the three commit messages alone.

| Claimed case | Covered by |
| --- | --- |
| An unrouted path gets the `*` answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| Without `*`, an unrouted path is 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses goes to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses, with no default route, is 404 | **none** |
| `/pip-stub/configure` takes the path `*` | **none**: the tests write to the `routes` map directly |
| The default route serves its responses in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| The request target is recorded in `requestUri` | `TestHandlePIP_RecordsTheRequestTargetAsSent` checks the struct field only; the JSON key `requestUri` that peers read is not asserted |
| Every chart part is off by default | none in CI; my `helm template` with no values renders nothing |
| Both kind harnesses install the chart and run the suite | CI jobs `kind-e2e` and `Parity on kind` |
| Keycloak restarts when a realm file changes (`checksum/realms`) | none |
| The stand starts under the restricted Pod Security Standard | **none**: no namespace in CI enforces it, and `test/scripts/test-chart-render.sh` doesn't render this chart |
| `app.kubernetes.io/*` and `helm.sh/chart` labels; selectors keep `app` | none |
| `profile.jq` fills first name, last name and email; a duplicate username or id fails the build | **none**: `testdata/realm/` has no user files, so the function and both checks never run in CI. I ran it on one input and it gives `R29LevelM2M`, as the comment says |
| The release publishes three more images | none can run offline |

Requests: add a `t.Run` case for the empty route with no default route, one that configures `*` through `handleConfigure`, and an assertion on the `requestUri` key in the `/pip-stub/calls` JSON. Add render assertions for the test stand to `test-chart-render.sh`, and a jq check over a fixture user file.

Commands the change tells someone to run:

| Command | Promised outcome | Run by |
| --- | --- | --- |
| `make test-stand-files`, `e2e-harness`, `e2e-suite`, `parity-harness`, `parity-suite`; `helm lint …` with each values file | Files generated, stand up, suite passes | CI `integration-tests.yaml` |
| `helm test authz-test-stand --timeout 15m --logs` (`helm-templates/authz-test-stand/README.md:64`) | "Run the suite and print its log" | **none** |
| `docker create … true` / `docker cp …` / `helm upgrade --install … --set TAG=<version>` (same README, steps 1–2) | Charts copied out and the stand installed | none. The outcome isn't in doubt: the image is `FROM scratch`, and `docker create` with an explicit command works on it |
| `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` (`docs/local-integration-tests.md`) | A subset runs on the next `make e2e-suite` | none. Outcome not in doubt |

For the `--logs` row, the outcome depends on the hook being a Job. In Helm 3.15.2, `GetPodLogs` (`pkg/action/release_testing.go:127`) asks for the logs of a Pod named after the hook, here `parity-suite`. The Job's Pod has a generated suffix, so the command fails with `unable to get pod logs for parity-suite: pods "parity-suite" not found`. I couldn't read Helm 4's source, and CI uses v4.3.1. Request: run that command on the stand with Helm 3 and Helm 4, or replace `--logs` with `kubectl logs job/<suite.name>`.

Hunks no commit message claims:
- **`test/svt/common/compose/docker-compose.yml:3`** moves the SVT Keycloak from `26.0` to `26.3.5@sha256:…`. That's a version bump in a stand the change otherwise doesn't touch. Request: a sentence that claims it, with the SVT run, or a separate commit.
- **`test/k8s/parity/idp-seed/parity-realm.json`** gains about 318 lines: the `ROLE_MT_*` roles, the `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a` clients, and the users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`. The commit claims only the second realm, `parity-mt-b`. Request: a sentence that claims these additions, or move them to the change with the cases that use them.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub:** the 404 control without `*` is there and passes on the base commit. The missing partition (empty route, no default route) is filed under item 2.
- **Existing state, substantive.** `make e2e-harness` and `make parity-harness` now run `helm upgrade --install` into namespaces the old harness filled with `kubectl apply`. The chart renders objects under the same names: `keycloak-realms`, `authz-agent-client-credentials`, the `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager` Deployments and Services, the ServiceAccount `runtime-suite`, and `pip-mock-config`, `idp` and `pip-mock` in parity. Helm refuses to adopt objects it doesn't own ("invalid ownership metadata"). CI always starts from a fresh kind cluster, and no doc gives the remedy. Request: a run on a namespace left by the base commit, or a documented remedy such as deleting the namespace or running `make e2e-down`, run on that state.
- **`E2E_HELM_ARGS` now reaches the test stand, substantive.** It shares two names with the agent and policy-admin charts:
  - `IMAGE_PULL_POLICY` (agent `values.yaml:88`, policy-admin `:50`, test stand `:13`) means the same in all three.
  - `TAG` (agent `:5`, policy-admin `:5`, test stand `:12`) means the agent image's tag in the old charts. In the test stand it becomes the tag of `local/pip-stub`, `local/tenant-manager` and `local/authz-runtime-suite`, which `e2e-images` builds only as `:ci`. With pull policy `Never`, the harness then fails after 10 minutes.
  - A `--timeout` meant for the 5-minute installs would also cut Keycloak's 10-minute wait.
  
  Request: a separate setting for the test stand (for example `TEST_STAND_HELM_ARGS`), or a run with `E2E_HELM_ARGS='--set TAG=…'`.
- **Replaced wait, substantive.** The most likely fault is a suite image missing from the kind node (`ErrImageNeverPull`).
  - The old target failed at 3 minutes on `kubectl wait --for=condition=Ready pod … --timeout=3m` with `timed out waiting for the condition`.
  - The new one prints the waiting reason through `kubectl logs -f` after about 3 minutes (90 tries with a 2 s sleep), then blocks on `wait $helm_pid` until the Job's `activeDeadlineSeconds: 900` or helm's `--timeout 15m`. That is about 15 minutes, against a 30-minute CI job limit.
  
  No sentence accepts the later failure. Request: a run of that fault with its duration and output, and a deadline on the whole wait at about 3 minutes until the Pod starts.
- **Limits.** `suite.activeDeadlineSeconds` (`values.yaml:99`, 900) sits inside `helm test --timeout 15m` (`Makefile:97`, README `:64`). Raised past 900, helm's fixed 15 minutes fires first, so the raised value has no effect through `make` or the README. A `-test.timeout` in `suite.args` raised past 900 is cut by the Job deadline, without Go's timeout report. At the defaults the inner limit (600 s) fires first. Request: derive helm's `--timeout` from `activeDeadlineSeconds` plus a margin, or tie the two together in the values comment.

## Item 3a: level, placement, and the environment

The pip-stub tests are small and sit beside the existing `TestHandlePIP_*` tests, sharing `resetState`. That part is fine.

The chart's labels, security contexts, the checksum annotation and "off by default" can all be seen with `helm template`. The repository runs exactly that kind of check (`test/scripts/test-chart-render.sh`, CI step "Render assertions"), but the change adds no assertion for this chart; CI only lints it. That's substantive; the request is filed under item 2.

The restricted Pod Security Standard only shows at admission. The CI kind namespaces are created by `--create-namespace` without a `pod-security.kubernetes.io/enforce: restricted` label, so CI never tests the claim. Request: label the e2e and parity namespaces `enforce=restricted` in the harness.

## Item 4: names by content, not by position

None. I checked the test case names, the test comments and the chart and Makefile comments. The `$(1)`/`$(2)`/`$(3)` in the `run-suite` macro are Make's own argument syntax, not ordinals.

## Item 5: the failure report

None. The new Go tests print got before want and name the input (`GET %s = %d %s, want %d %s`, `statuses of /a, /b, /a = …`). `t.Fatalf` is used only before indexing `calls[0]`, and the case names describe their conditions.

## Item 6: what the writer says it verified

Neither commit states a red run on the base commit or a mutation result. The empty-route case would panic on the base (index −1), but nobody says it was seen failing. No run under the restricted Pod Security Standard or on OpenShift is stated either.

## Item 7: siblings of the change

- **Substantive: OpenShift and read-only root filesystem.** The authz-agent chart (`deployment.yaml:266`) and the policy-admin chart (`:138`) leave the root filesystem writable on OpenShift, "as the platform's charts do". The test stand sets `readOnlyRootFilesystem: true` everywhere (`_helpers.tpl:36`). Its images use the same `qubership-core-base` family. At the same time, the commit says it leaves out `runAsUser` so that OpenShift's restricted SCC can assign a uid. Request: follow the sibling rule, or show a run of the stand on OpenShift with a uid assigned from the namespace range.
- **Substantive: stale count in `README.md:58`.** It still says "CI builds both via `.github/docker-dev-config.json`", which now lists five images. Request: "CI builds the images of `.github/docker-dev-config.json`".
- **Taste:** the Makefile's `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` hard-code the stub instance names that are now keys in `pipStub.instances`. A stand that adds an instance won't have it restarted. Reading the names from `-l app.kubernetes.io/part-of=authz-test-stand` would follow the values.
- I found no other references to the removed manifests (`git grep` for `runtime-suite-job`, `keycloak.yaml`, `tenant-manager.yaml` and the like). "both charts" in `test-chart-render.sh` still correctly means the agent and policy-admin charts.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Comment describes the history of the change ("as it did before the default route existed") | Substantive | `test/integration/pipstub/main.go:37` | 1 |
| Default-route comments leave out the empty-route case | Substantive | `test/integration/pipstub/main.go:34`, `:122` | 1 |
| Comment says `helm test` prints the log at the end; without `--logs` it prints none | Substantive | `Makefile:95` | 1 |
| List of images that use `TAG` leaves out the runtime suite | Substantive | `helm-templates/authz-test-stand/values.yaml:9` | 1 |
| Empty route with no default route (404) is untested | Substantive | `test/integration/pipstub/main_test.go:225` | 2 |
| `/pip-stub/configure` with `*` and the `requestUri` JSON key are untested | Substantive | `test/integration/pipstub/main_test.go:276` | 2 |
| Chart labels, security contexts, checksum restart and `profile.jq` have no test | Substantive | `test/scripts/test-chart-render.sh` | 2 |
| README's `helm test --logs` reads a Pod named after the Job; fails on Helm 3.15 | Substantive | `helm-templates/authz-test-stand/README.md:64` | 2 |
| SVT Keycloak bump is not claimed | Substantive | `test/svt/common/compose/docker-compose.yml:3` | 2 |
| Tenant-A clients and extra users in the parity realm are not claimed | Substantive | `test/k8s/parity/idp-seed/parity-realm.json` | 2 |
| Install over a namespace from the old `kubectl apply` harness is neither run nor documented | Substantive | `Makefile:86`, `:150` | 3 |
| `E2E_HELM_ARGS` `TAG`/`--timeout` now reach the test stand with another meaning | Substantive | `Makefile:86` | 3 |
| Missing suite image now fails at about 15 min instead of 3 | Substantive | `Makefile:100` | 3 |
| `suite.activeDeadlineSeconds` above 900 is overridden by `helm test --timeout 15m` | Substantive | `helm-templates/authz-test-stand/values.yaml:99` | 3 |
| Restricted Pod Security Standard is not enforced on any CI namespace | Substantive | `.github/workflows/integration-tests.yaml:145` | 3a |
| Read-only root filesystem on OpenShift goes against the agent chart's rule | Substantive | `helm-templates/authz-test-stand/templates/_helpers.tpl:36` | 7 |
| README still says CI builds "both" images | Substantive | `README.md:58` | 7 |
| Deployments to restart are hard-coded instead of read from the chart's labels | Taste | `Makefile` (`E2E_LOCAL_DEPLOYMENTS`) | 7 |

The drift script doesn't parse Go, Helm templates or the Makefile, so I checked comment drift by hand. I couldn't check Helm 4's `helm test --logs` behavior because its source wasn't available locally.
