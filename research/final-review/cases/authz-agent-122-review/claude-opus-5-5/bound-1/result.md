# Final review: `58316ca..HEAD` (three commits)

There was no separate task statement, so the claimed cases come from the three commit messages alone. The drift script printed nothing: it only parses Java, Kotlin, Groovy and Scala, and this change is Go, Helm, YAML, Make and Markdown. I did item 1 by hand. There is no previous report.

What I ran: `go test` in `test/integration/pipstub` (passes). I copied the chart to the scratchpad, filled in `files/` the way the Dockerfile does, and ran `helm lint` and `helm template` with both values files (both clean). All objects carry `helm.sh/chart`, and the security contexts render as the commit says. I ran the `profile.jq` merge with no user files and with a sample user file (it works). I ran `make -n` on `e2e-suite` and `parity-harness`, and checked the `helm test` flags on Helm 4.3.0.

Test stack (test-authoring §0): `AGENTS.md` has no stack line. I propose adding one sentence: `Tests (Go): the standard testing package as engine and assertions; no testify in test/integration/pipstub.` I edited no file.

## Item 1: comments consistent with the code and with each other

- **`docs/local-integration-tests.md:104`** says `e2e-harness` installs "…and the suite Job; waits until they are Ready". The Job is a `helm test` hook, so `helm upgrade --install --wait` neither creates it nor waits for it. `test/k8s/README.md` says so correctly ("installing the stand does not start it"). The two pages state the same fact differently.
- **`docs/local-integration-tests.md:190`**: the troubleshooting row still names `rollout status deploy/keycloak`. That command no longer runs. The timeout now comes from `helm … --wait --timeout 10m`, so a reader searching for the old message finds a row that doesn't match what they see.
- **`README.md:59`**: "CI builds both via `.github/docker-dev-config.json`". That file now lists five images.
- **`helm-templates/authz-test-stand/values.yaml:9-11`**: the list of images that use `TAG` names pip-stub, authz-parity-suite and tenant-manager. It leaves out `authz-runtime-suite`, which the e2e values run under the same `TAG`.
- **`test/integration/pipstub/main.go:37-38`**: "…as it did before the default route existed" describes the change rather than the behavior, in a package comment (taste).
- Checked and consistent: the comments in `_helpers.tpl`, `idp.yaml`, `suite.yaml` and `tenant-manager.yaml`; the claims in `idp-seed/README.md` (realm `parity-mt-b`, users `mt-a`/`mt-a-admin` and their roles, and the `tenant-id` claim of `parity-m2m-tenant-b`, all checked with jq); `helpers.go` and the testify `Dockerfile`; and `REALM-DESCRIPTION.md`.

## Item 2: claimed cases covered

| Claimed case | Test or run |
| --- | --- |
| `/pip-stub/configure` accepts `*` as the default route | **None.** The tests write `routes[defaultRoute]` directly, and nothing goes through `handleConfigure`. |
| An unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A stub with no `*` route still answers 404 | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses falls through (it used to index −1) | `…/a_routed_path_with_no_responses_gets_the_default_answer`, `…/an_unrouted_path_with_an_empty_default_route_is_404` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| The stand starts under the restricted Pod Security Standard | **None.** No render assertion, and no namespace is labeled `pod-security.kubernetes.io/enforce=restricted` in the kind harness. |
| `app.kubernetes.io` labels and `helm.sh/chart` on every object | **None** in `test/scripts/test-chart-render.sh`, which asserts exactly these things for the other two charts. I checked it by hand only. |
| `profile.jq` fills in profile fields; the build fails on a duplicate user | **None.** There are no user files yet, so nothing runs it. My manual run gave `R29LevelM2M` as claimed. |
| The release publishes three more images | **None.** No dry run of Docker Images Release is stated. `build_context` appears in `.qubership/docker.cfg:17-29` for the first time, and nothing shows the `config-resolver`/`docker-action` v2.8.2 pair reads it. |

Commands the change documents:

| Command | What runs the same form |
| --- | --- |
| `make test-stand-files` | The CI job "Chart lint and render" |
| `make e2e-harness`, `parity-harness`, `e2e-suite`, `parity-suite` | The kind jobs in `integration-tests.yaml` |
| `docker build … build/authz-agent-transfer/Dockerfile .` | The generic Go build's image matrix (docker-dev-config) |
| `docker create … true; docker cp …; docker rm` (chart README) | none |
| `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml` | none. The result depends on the release's tag format and on the published images existing. |
| `helm test authz-test-stand --timeout 15m --logs` | none. The Makefile runs it without `--logs`. The flag exists in Helm 4.3.0. |
| The subset `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false` | none. I rendered the `--set` part and the Job env comes out right; `--reuse-values` against a release was not run. |

Hunks no commit sentence claims:

- **`test/svt/common/compose/docker-compose.yml:3`**: Keycloak goes from `26.0` to `26.3.5@sha256:…` for the SVT stack, with no SVT run.
- **`parity-realm.json`**: about 318 added lines. The commit claims only "a second tenant realm, parity-mt-b". The additions also include the clients `parity-m2m-tenant-a/b/unknown/empty` and `parity-end-user-tenant-a`, the users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`, and the roles `ROLE_MT_*`. Nothing in the repository refers to them yet.
- **`REALM-DESCRIPTION.md`**: the issuer correction to `/auth`. It's a correct fix but unclaimed (minor).

## Item 3: boundaries, partitions, and the negative control

- **pip-stub.** The clamp, an empty route, an empty default and a missing default are each covered, and each 404 row is the control for the 200 rows. Missing: the case where a rule matches while a `*` route exists. The rule should win, as the package comment says, and nothing asserts it.
- **State left behind by the old harness.** A namespace set up by the old `e2e-harness` or `parity-harness` holds objects created with `kubectl apply`: Deployment `keycloak`/`idp`, ConfigMap `keycloak-realms` (the same name the chart renders), Secret `authz-agent-client-credentials` and ServiceAccount `runtime-suite`. `helm upgrade --install authz-test-stand` refuses to adopt objects that lack Helm ownership metadata. Every run in this change starts from a fresh kind cluster, and the docs give no remedy: `make e2e-down` is listed only for "Cluster left behind".
- **Values users already pass.** `E2E_HELM_ARGS` (Makefile:48) now also reaches the test-stand chart. That chart reads two keys the agent charts read too, `TAG` and `IMAGE_PULL_POLICY`. The documented `--set IMAGE_PULL_POLICY=Never` is harmless. But `--set TAG=<x>`, meant for the agent images, now makes the stand ask for `local/pip-stub:<x>`, `local/tenant-manager:<x>` and the suite images, which `e2e-images` never builds. `--wait` then runs into its 10-minute timeout.
- **The replaced suite wait (Makefile:100, `run-suite`).**
  - Fault: the Job Pod never starts (`ErrImageNeverPull`, which the troubleshooting table lists).
    - Old: `wait --for=condition=Ready pod … --timeout=3m` fails at 3 minutes with kubectl's timeout message.
    - New: the log loop polls for about 3 minutes, then `logs -f` fails at once, then `wait $helm_pid` blocks until the Job's `activeDeadlineSeconds: 900` or `helm test --timeout 15m` fires. That's about 15 minutes, and the output is only Helm's Job error, with nothing about the Pod's waiting reason.
    - No sentence in the change accepts this. The same happens when restricted PSS rejects the Pod, since the Job then has no Pod at all.
  - Second issue: `kubectl wait --for=create` needs kubectl 1.31 or later. With an older client the `&&` skips the loop and the log is never streamed. The prerequisites table (`docs/local-integration-tests.md:37`) gives no minimum version.
- **Limits.** The run-time limits on one suite run:

  | Limit | Where it is set |
  | --- | --- |
  | `-test.timeout 600s` | `suite.args` |
  | `activeDeadlineSeconds: 900` | `values.yaml:99`, a documented value |
  | `helm test --timeout 15m` | Fixed in the Makefile and in the chart README:64 |
  | `timeout-minutes: 30` for the whole job | `integration-tests.yaml` |

  At the defaults the inner limit fires first, which is correct. But raising `suite.activeDeadlineSeconds` past 900 has no effect, because `helm test --timeout 15m` fires first. One of these limits should be derived from the other.

## Item 3a: level, placement, and the environment

- The pip-stub tests are small tests that call `handlePIP` directly. They sit in `main_test.go` beside the existing ones and use `resetState`. The new `serve` helper doesn't duplicate any existing helper.
- The chart's security contexts and labels can be checked at render level, in-process with `helm template`. The repository's own harness for that, `test/scripts/test-chart-render.sh` (section "Platform conventions shared by both charts", line 783), does not cover the new chart. That is a finding.

## Item 4: names by content, not by position

- `values.yaml:11`: "own image and pull policy below" could name `idp.image` and `idp.imagePullPolicy` instead (taste).
- The test case names are content-based. Otherwise none.

## Item 5: the failure report

None. Each `t.Errorf` prints got and want together with the request (`GET %s = %d %s, want %d %s`). The `requestUri` check prints all four values, the subtests are named by condition, and the sequence test prints both slices.

## Item 6: what the writer says it verified

None stated. No commit claims a red run on the base commit for the pip-stub tests. On the base they would fail: 404 for the default-route rows and an index panic for the empty-route row. No commit mentions a kind run of the chart under read-only root filesystems either. That matters because `qubership-core-base:2.4.2` (pip-stub, parity suite) differs from the `alpine-2.5.8` base the agent uses with a read-only root, and the agent sets it only on Kubernetes.

## Item 7: siblings of the change

- **Stale lists and counts** (all under item 1): README "both" (README:59), the troubleshooting row (docs:190), and the docs `e2e-harness` row (docs:104).
- **`test-chart-render.sh`** loops over two charts (line 439 and line 792), and the new chart isn't one of them (see item 3a).
- **Other paths with the same symptom:** `parity-suite` uses the same `run-suite`, so the 15-minute fault and the `TAG` leak through `E2E_HELM_ARGS` apply to the parity harness too.
- **Stale references:** a `git grep` for every deleted manifest name, `E2E_AUTHN`, `PARITY_SEED`, `parity-realms` and `pip-mock-config` finds no leftovers.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | `run-suite` fails about 12 minutes later than the old wait when the Pod never starts, and prints less | Substantive | `Makefile:100` | Run that fault and give both durations; bound the wait at 3 minutes (e.g. wait for the Pod to be Ready, then stop `helm test`), or accept the delay in the description |
| 2 | Namespaces set up by the old `kubectl apply` harness make `helm upgrade --install` fail on ownership | Substantive | `Makefile:85`, `:149`; docs §6 and §8 | Add a documented remedy (`make e2e-down` or deleting the namespace) and run it on such a namespace |
| 3 | `E2E_HELM_ARGS` now carries `TAG` and `IMAGE_PULL_POLICY` into the test stand | Substantive | `Makefile:48`, `:86`, `:150` | Give the stand its own args variable, or run with `--set TAG=<other>` and document the result |
| 4 | Raising `suite.activeDeadlineSeconds` past 900 has no effect under the fixed `helm test --timeout 15m` | Substantive | `values.yaml:99`; Makefile `run-suite`; chart `README.md:64` | Derive one limit from the other |
| 5 | Restricted PSS and label claims have no render assertion and no enforced-namespace run | Substantive | `test/scripts/test-chart-render.sh:783`; Makefile harness | Add render assertions for the test-stand chart, and label the kind namespace `enforce=restricted` |
| 6 | Configuring `*` through `/pip-stub/configure` is untested; rule-over-default precedence is untested | Substantive | `test/integration/pipstub/main_test.go:225` | Add a test that sends a `PUT` to `handleConfigure`, and a rule-plus-`*` case |
| 7 | Unclaimed hunks: SVT Keycloak bump, parity-realm additions beyond `parity-mt-b`, the issuer doc fix | Substantive | `docker-compose.yml:3`, `parity-realm.json`, `REALM-DESCRIPTION.md` | Add a sentence claiming each (with an SVT run for the bump), or move them to their own change |
| 8 | Stale docs: the `rollout status deploy/keycloak` row, "CI builds both", and the harness row claiming it installs the suite Job | Substantive | `docs/local-integration-tests.md:190`, `:104`; `README.md:59` | Reword to the Helm wait message, the five images, and no suite Job |
| 9 | `profile.jq` and the duplicate check run on no input | Substantive | `build/authz-agent-transfer/Dockerfile:39-46` | Add a fixture user file, or a CI step that runs the stage on one |
| 10 | Release of three new images not dry-run; `build_context` unproven with the workflow-hub actions | Substantive | `.qubership/docker.cfg:17` | Do a dry run of Docker Images Release |
| 11 | Transfer-image install commands not run in any form | Substantive | chart `README.md` steps 1–3 | Run them once against a dry-run release, or mark them unverified |
| 12 | `wait --for=create` needs kubectl 1.31+, and the prerequisites don't say so | Substantive | `docs/local-integration-tests.md:37` | State the minimum version |
| 13 | The `TAG` image list omits `authz-runtime-suite` | Substantive | `values.yaml:9` | Add it |
| 14 | A package comment describes the change ("as it did before…") | Taste | `test/integration/pipstub/main.go:37` | State the 404 behavior without the history |
| 15 | "below" refers by position | Taste | `values.yaml:11` | Name `idp.image` and `idp.imagePullPolicy` |

Not checked: I didn't run any kind or Kubernetes install, `helm test`, the Docker builds, the release workflow, or the parity and runtime suites. I didn't inspect the `qubership-core-base` image entrypoints. There was no review pass over the prose for style alone.
