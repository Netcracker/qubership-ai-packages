# Final review of `58316ca..HEAD`: `8b85515` (test-stand chart), `9d25da7` (pip-stub default route), `17b17fc` (restricted Pod Security Standard)

There was no task statement, so the claimed cases in item 2 come only from the three commit messages and the test comments. No earlier report of this form exists. I loaded `test-authoring` (with `references/go/testing.md` and `testify.md`) and `english-developer-style`. No Go doc-comment skill was among the three allowed, so I judged the Go comments against `test-authoring` and the style skill only.

The drift script printed nothing and exited 0. It parses only Java, Kotlin, Groovy and Scala, and this change is Go, YAML, Helm templates, Makefile and Markdown. I read every changed comment by hand.

**Proposed stack line for §0:** `AGENTS.md` has no test-stack line. One that would fit: `Tests: Go testing as engine and assertions in test/integration/pipstub; testify in test/integration/testify`. I only propose it here; I did not edit anything.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-38` and `:122-123`.** Both comments say the default route answers "every request whose path has no route of its own". The code at `:234` also sends a path whose route has an empty `Responses` list to the default route. A reader would expect such a path to get 404, or the old index of −1. The commit message and the test comment do state this case; these two comments leave it out.
- **`Makefile:95-96`.** The comment says "`helm test` … prints the log only at the end, so the log is streamed while it runs." `helm test` without `--logs` prints no log at all, and with `--logs` it fails on a Job hook (see item 2). A reader would think the kubectl streaming duplicates output that helm already prints.
- **`docs/local-integration-tests.md:104`.** It says `e2e-harness` installs "… and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` and is not created at install, which `test/k8s/README.md:122-124` states correctly. The two pages now contradict each other.
- **`docs/local-integration-tests.md:127`.** It says re-running `e2e-harness` replaces the Keycloak Pod only "after a change to a realm file". In fact any change to the Keycloak Pod template replaces it, and a dev-mode Keycloak then mints new realm keys:
  - This branch's own `17b17fc` changes that template (new labels, securityContext). The first `make e2e-harness` on a stand built from `8b85515` therefore restarts Keycloak, and an agent that is not restarted fails at `setup.wait_for_agent`.
  - `helm.sh/chart` is now on the Pod template too, so every chart version bump also restarts Keycloak.
- **Other changed comments: no finding.** I checked the `idp.yaml` probe and path comments, `suite.yaml:12-13`, `:60-61`, `tenant-manager.yaml:9-11`, and the `testify/helpers.go` and `testify/Dockerfile` pointers. No comment narrates the change ("now", "no longer").

## Item 2: claimed cases covered

**Commit `9d25da7` (pip-stub):**

| Claimed case | Test |
| --- | --- |
| An unrouted path gets the default route's answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| No default route → 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| Empty default route → 404 | `…/an_unrouted_path_with_an_empty_default_route_is_404` |
| Route with no responses → default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| Route with no responses → **or to 404** | **none** (item 3) |
| The default route answers in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| "`/pip-stub/configure` now takes the path `*`" | **Not through the interface.** Every test writes `routes[defaultRoute]` directly; none sends `PUT /pip-stub/configure` with `"path":"*"` to `handleConfigure`. |

**Commit `8b85515` (chart):**

| Claimed case | Covered by |
| --- | --- |
| Every part off by default | No test. I rendered it: 0 objects. |
| Keycloak imports `files/realms/<realms>/` and restarts when a realm file changes | No test. I rendered it: the checksum changes when one realm file's content changes. |
| pip-stub instances, tenant-manager, M2M Secret, suite Job as a `helm test` hook | CI jobs `chart` (both `helm lint` calls) and `kind-e2e`/`kind-parity` (I did not see those runs) |
| `make test-stand-files` runs the `chart-files` stage | CI job `chart` |
| User files merged, profile fields filled in, build fails on a duplicate user | No test. Only the empty input ever runs (item 3). |
| The transfer image carries the three charts | No run (see the commands table) |
| The parity realm gains `parity-mt-b` | Imported by `kind-parity`; no case uses it in this change |
| The release publishes three more images | No run |
| Error texts `no realm files under files/realms/<realms>/` and `no file files/pip-stub/<file>` | No test. I rendered both without `files/` and the texts match. |

**Commit `17b17fc` (restricted Pod Security Standard):**

- **The stand starts in a namespace that enforces `restricted`: no test.** No namespace is labeled `pod-security.kubernetes.io/enforce=restricted`, and `test/scripts/test-chart-render.sh` checks only the two product charts.
- **The security fields, read-only root except Keycloak, no `runAsUser`, and the `app.kubernetes.io/*` and `helm.sh/chart` labels: no test.** I rendered both value files. All 5 and 4 Pods carry the four restricted fields, and all 12 and 10 objects carry the labels. Every image names a numeric non-root user (`USER 10001:10001`).

**Commands the change tells someone to run:**

| Command | Run by | Notes |
| --- | --- | --- |
| `make test-stand-files` | CI job `chart` | |
| `make e2e-harness`, `make e2e-suite`, `make parity-harness`, `make parity-suite` | `kind-e2e`, `kind-parity` | Run on kubectl from the runner or kind-action. `kubectl wait --for=create` (`Makefile:103`) needs kubectl 1.31 or later. The prerequisites table (`docs/local-integration-tests.md:37`) names no version. On an older kubectl the `&&` skips the poll, the log is not streamed, and the exit code is still helm's. |
| `helm test authz-test-stand --timeout 15m --logs` (`helm-templates/authz-test-stand/README.md:64`) | **none** | The property that matters: the test hook is a **Job**, not a Pod. In Helm v3.15.2, `pkg/action/release_testing.go:127` calls `Pods(ns).GetLogs(h.Name)`, so it looks for a Pod named `parity-suite`. That Pod does not exist, `cmd/helm/release_testing.go:82` returns the error, and the command exits non-zero even when the suite passed. Helm 4.3 (the CI version) I could not read. |
| `docker create …transfer:<version> true` / `docker cp` (`README.md:42-44`) and `docker build … build/authz-agent-transfer/Dockerfile .` (`Dockerfile:20`) | **none** | Only the `chart-files` stage runs in CI. The final `FROM scratch` stage and the copy-out are first exercised by a release. `docker create` with an explicit command does not execute it, so `true` missing from scratch should not matter, but nothing has run it. |
| `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` (`docs/local-integration-tests.md:71-72`) | **none** | Depends on `--reuse-values` keeping the harness's `--set suite.env.BASE_URL`. That is Helm's documented behavior; I see no risk specific to this configuration. |

**Hunks no sentence of the commit messages claims:**
- `test/svt/common/compose/docker-compose.yml`: Keycloak `26.0` → `26.3.5@sha256…`.
- `.github/docker-dev-config.json`: three new dev-build entries. The message claims only `.qubership/docker.cfg`.
- `test/k8s/parity/idp-seed/parity-realm.json`: besides `parity-mt-b`, it gains 8 users (`parity-r29-scope`, `parity-r30-scope`, `mt-a`, `mt-a-admin`, four tenant service accounts), 5 clients (`parity-m2m-tenant-{a,b,unknown,empty}`, `parity-end-user-tenant-a`) and 2 roles.
- `test/k8s/authn/REALM-DESCRIPTION.md`: the issuer is corrected to `/auth/realms/…`.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub, missing partitions.**
  - A routed path with no responses **and no default route** has no test. That input is the defect the commit names: on the base commit it indexed `Responses[-1]`.
  - The precedence control is missing. With rules loaded (`PIP_STUB_CONFIG`), a request that matches a rule must get the rule's answer and not the default route's. The package comment (`main.go:29-31`) claims this order; `pip-mock` runs with rules.
- **Realm merge (`build/authz-agent-transfer/Dockerfile:39-45`, `profile.jq`).** `test/parity/suite/testdata/realm/` holds no user file, so only the empty partition ever runs. The non-empty partition, a user that already has a `firstName`, and the duplicate-user failure never run anywhere. I ran it by hand on jq 1.8.2 with sample files:
  - The merge produced `R29LevelM2M`.
  - A declared `firstName` was kept.
  - A duplicate `mt-a` made `jq -e` exit 1.

  It works, but nothing in the repository records that.
- **State left by the earlier harness.** A kind namespace set up before `8b85515` holds objects created by `kubectl apply`: `deploy/keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, Secret `authz-agent-client-credentials`, ServiceAccount `runtime-suite`, and in `authz-parity` `deploy/idp`, `pip-mock`, and others. The objects the chart now renders have the same names. `helm upgrade --install authz-test-stand` refuses them with "exists and cannot be imported into the current release: invalid ownership metadata" (`pkg/action/validate.go:59` in v3.15.2). No document gives the remedy (`make e2e-down`, or deleting the namespace) for this upgrade, and no run starts from that state.
- **Limits on the same suite run.**

  | Limit | Set where | Value |
  | --- | --- | --- |
  | `-test.timeout` | `suite.args` (values) | 600s |
  | `activeDeadlineSeconds` | documented setting `suite.activeDeadlineSeconds`, `values.yaml:99` | 900 |
  | `helm test --timeout` | fixed in `Makefile:102` and `README.md:64` | 15m, counted per hook Job |

  - At the defaults the innermost limit (600s) fires first, which is correct.
  - Raising `suite.activeDeadlineSeconds` past 900 has no effect, because the fixed 15m helm timeout ends the run first.
  - At the defaults, 900s equals 15m, and helm's clock starts slightly earlier. A run stuck after the Go timeout window therefore reports helm's "timed out waiting for the condition" instead of the Job's `DeadlineExceeded`.
- **Values users already pass: none.** `E2E_HELM_ARGS` now reaches the test-stand chart. Its documented example `--set IMAGE_PULL_POLICY=Never` maps to the chart's key for its own images, and Keycloak has its own `idp.imagePullPolicy`, so the example does no harm. `E2E_BASE_URL`/`PARITY_AC_BASE_URL` now apply at harness time, and `test/k8s/README.md:63-66` says so.
- **Empty value.** `suite.resources: null` fails rendering with a nil pointer at `suite.yaml:68`; `{}` renders.

## Item 3a: level, placement, and the environment

- **pip-stub tests: none.** They are small, in-process (`httptest`), and sit in `main_test.go` beside the existing `TestHandlePIP_*` tests, sharing `resetState`. `.github/workflows/go-build.yaml:63` runs this module.
- **Chart: finding.** The smallest level that can observe the restricted-PSS fields and labels is a `helm template` assertion, and `test/scripts/test-chart-render.sh` (run by CI job `chart`) has none for this chart. The only larger check, a namespace with `enforce=restricted`, is not configured either.
- No test depends on an optional prerequisite.

## Item 4: names by content, not by position

None. The subtest names state condition and outcome. `$(1) $(2) $(3)` in `run-suite` are Make's positional `call` arguments, which the Makefile's own comment names. "The Makefile targets below" in `test/k8s/README.md` was already there before this change.

## Item 5: the failure report

None. Every new check is `if got != want { t.Errorf("GET %s = %d %s, want %d %s", …) }` or a `reflect.DeepEqual` guarded the same way. Each prints input, got and want in Go's order. `t.Fatalf` is used only before dereferencing `calls[0]`. Table ids are content, not indexes.

## Item 6: what the writer says it verified

Neither commit states a red run on the base commit or a mutation verdict. The empty-route case would have hit the old `Responses[-1]` on the base commit, but that is my inference, not the writer's evidence. I ran `go test ./...` in `test/integration/pipstub` as a consistency check, and it passed.

## Item 7: siblings of the change

- **`PipController.ResetPinnedRoutes` (`test/parity/suite/pip_control.go:181`): does not apply.** If a case pins `*`, a reset turns the default route into 404 `{"error":"reset"}`, which matches "no default route".
- **`matchRule`'s `RespondSequence` (`main.go:276`): does not apply.** It already guards the empty case.
- **Count sentences for the image set (finding).** `docker-dev-config.json` now lists five images, but two sentences still count two:
  - `README.md:59`: "CI builds both via `.github/docker-dev-config.json`".
  - `.github/docs-for-publication-task.md:77`: "The two-entry array".
- **Other lists of the changed sets: none.** `E2E_HELM_ARGS` is updated in `Makefile:45-46` and `test/k8s/README.md:63`. `test-stand-files` is in `.PHONY` and in both target tables. The Keycloak pin `26.3.5` agrees with `test/BASELINE.md:24`.
- **Render script.** `test-chart-render.sh:783` loops over "both charts". The test stand is a fixture, so the platform conventions don't apply, but its security claims have no home there (item 3a).

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | Upgrading a stand made by the earlier kubectl harness fails on Helm's ownership check; no remedy documented, no run from that state | Substantive | `Makefile:86`, `:150`; `docs/local-integration-tests.md` | Document the remedy (`make e2e-down` or delete the namespace) for the upgrade and run it, or run `e2e-harness` on a namespace from `58316ca` |
| 2 | `helm test --logs` reads a Pod named after the hook; this hook is a Job, so it errors and exits non-zero even on a pass (v3.15.2 source); nothing runs it | Substantive | `helm-templates/authz-test-stand/README.md:64` | Run that form on kind with Helm 4.3 and 3.x, or document the `kubectl logs -f job/<suite.name>` form the Makefile uses |
| 3 | `suite.activeDeadlineSeconds` is capped by the fixed `--timeout 15m`; at the defaults the two are equal and helm's timeout hides the Job's report | Substantive | `values.yaml:99`, `Makefile:102`, `README.md:64` | Derive helm's `--timeout` from the value (with a margin), or document the pair and set the default below 15m |
| 4 | Restricted-PSS claim, security fields and new labels have no test | Substantive | `templates/_helpers.tpl:23-40`; `test/scripts/test-chart-render.sh` | Render assertions for the test-stand chart, and/or `pod-security.kubernetes.io/enforce=restricted` on the kind namespaces |
| 5 | Missing case: routed path with no responses and no default route → 404 (the original defect) | Substantive | `test/integration/pipstub/main_test.go:226` | Add the row |
| 6 | Missing control: a rule-matched request is answered by the rule, not the default route | Substantive | `test/integration/pipstub/main_test.go` | Add a test with `rules` set and `*` configured |
| 7 | "`/pip-stub/configure` takes `*`" is tested by writing `routes` directly | Substantive | `test/integration/pipstub/main_test.go:243`, `:257` | Configure `*` through `handleConfigure` in at least one test |
| 8 | Default-route comments leave out routes with no responses | Substantive | `test/integration/pipstub/main.go:35`, `:123` | Name both cases |
| 9 | Comment says `helm test` prints the log at the end; without `--logs` it prints none | Substantive | `Makefile:96` | Say `helm test` prints no Pod log for a Job hook |
| 10 | Docs say `e2e-harness` installs the suite Job and waits for it | Substantive | `docs/local-integration-tests.md:104` | Drop the Job from that row, as `test/k8s/README.md` does |
| 11 | Keycloak restart condition stated too narrowly; this branch's own Pod-template change restarts it | Substantive | `docs/local-integration-tests.md:127` | "after a change to a realm file or to Keycloak's Pod template"; optionally keep `helm.sh/chart` off the Pod template |
| 12 | Realm-merge, profile and duplicate checks never run on a non-empty input | Substantive | `build/authz-agent-transfer/Dockerfile:39-45`, `profile.jq` | A fixture user file and a CI step (or script) that runs the stage and checks the merged realm and the duplicate failure |
| 13 | Transfer image's final stage and copy-out instructions never run | Substantive | `build/authz-agent-transfer/Dockerfile:52-56`; `README.md:41-45` | A release dry-run, or a local build and `docker create`/`cp`, stated in the description |
| 14 | Unclaimed hunks: svt Keycloak bump, `docker-dev-config.json` entries, parity-realm users/clients/roles beyond `parity-mt-b`, issuer fix in `REALM-DESCRIPTION.md` | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `.github/docker-dev-config.json:12-27`; `parity-realm.json`; `REALM-DESCRIPTION.md:202` | A sentence for each with the run that checks it, or move them to their own change |
| 15 | Stale counts after the dev-config grew to five images | Substantive | `README.md:59`; `.github/docs-for-publication-task.md:77` | Update both |
| 16 | `kubectl wait --for=create` needs kubectl 1.31 or later; the prerequisites table states no version | Substantive | `docs/local-integration-tests.md:37`; `Makefile:103` | State the minimum version |
| 17 | The helper comment ties the `app` selector to "the Makefile's deploy/<name>", which addresses objects by name, not by label | Taste | `templates/_helpers.tpl:3-4` | Keep only the `kubectl -l app=<name>` reason |
| 18 | `TAG` comment lists pip-stub, authz-parity-suite and tenant-manager but not the runtime suite image the e2e values run | Taste | `values.yaml:9-11` | Say "the suite image" |
| 19 | `suite.resources: null` gives a nil pointer at render | Taste | `templates/suite.yaml:68` | `(.Values.suite.resources | default dict).limits` |

**Not checked:** I did not run the kind jobs, the release workflow, any Docker build, or Helm 4's `helm test --logs`. The chart findings rest on `helm template` and `helm lint` (v4.3.0) of a copy with hand-generated `files/`, and the Helm behavior I cite comes from the v3.15.2 source. I did no style pass over the prose.
