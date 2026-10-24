I found 16 substantive findings and 1 matter of taste in the three commits `58316ca..HEAD`. There was no task statement, so the claimed cases come from the three commit messages and the test comments. I changed nothing in the repository; temporary output is in the scratchpad only.

The drift script printed nothing. It parses only `.java`, `.kt`, `.kts`, `.groovy` and `.scala` files, and this change is Go, YAML, Helm templates, a Makefile, a Dockerfile and Markdown. Item 1 was therefore done by reading the diff.

What I ran:
- `helm lint` on the chart with both values files: passes.
- `helm template` with both values files: renders.
- The `chart-files` Docker stage, built into the scratchpad: the parity realm matches the source realm, because there are no user files to merge.
- The transfer image, built locally, then the chart README's `docker create` / `docker cp` steps: they work, and the copied chart renders.
- `go test` in `test/integration/pipstub`: passes.

## Item 1: comments consistent with the code and with each other

- **`Makefile:95-96`**: "`helm test` … prints the log only at the end, so the log is streamed while it runs." The recipe does not pass `--logs`, so `helm test` prints no suite log at all. The sentence also leads a reader to expect a log at the end that never comes.
- **`docs/local-integration-tests.md:104`**: the `e2e-harness` row says the chart installs "… and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` (`templates/suite.yaml:21`), so an install never creates it. `test/k8s/README.md` says the opposite: "installing the stand does not start it".
- **`helm-templates/authz-test-stand/values.yaml:9-11`**: the comment lists the images `TAG` applies to as "pip-stub, authz-parity-suite, and tenant-manager". The e2e stand also runs `local/authz-runtime-suite` under `TAG`.
- **`test/integration/pipstub/main.go:31-38`**: two problems with "before".
  - "behaviour is exactly as before" now sits beside a second "before" in "as it did before the default route existed", and the two mean different things. The first refers to the time before the rule engine; a reader can take it as the time before the default route.
  - The second sentence describes the change's history, which the item rules out.
- Checked and consistent: the other new comments in the Makefile, `idp.yaml`, `suite.yaml`, `_helpers.tpl` and the Dockerfile, the `callRecord.RequestURI` comment, and the `LoadConfig` comment in `helpers.go`.

## Item 2: claimed cases covered

Source of the claims: the three commit messages and the comments above the pipstub tests.

| Claimed case | Covered by |
| --- | --- |
| An unrouted path is answered by the default route | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses falls through "or to 404" | **none.** A routed path with empty responses and no default route is the exact input that indexed at -1 on the base commit, and no case uses it. |
| `/pip-stub/configure` takes the path `*` | **none.** Every test writes `routes[defaultRoute]` directly; none goes through `handleConfigure`. |
| A stub nobody configured with `*` still answers 404 | `…/an_unrouted_path_without_a_default_route_is_404` |
| The default route serves its responses in sequence across paths, clamped to the last | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the request target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| Configured rules win over the default route (header comment) | none (taste: the rule step itself is unchanged) |
| User files are merged into the parity realm, their profile fields are filled in, and the build fails on a user declared twice | **none.** `testdata/realm/` holds no user files, so `profile.jq`, the merge and both duplicate checks have never run. |
| The stand starts under the restricted Pod Security Standard | **none.** No harness or CI namespace sets `pod-security.kubernetes.io/enforce=restricted`. |
| The labels are added and the selectors keep `app: <name>` | rendered output (checked in this review) |
| The resource profiles of the agent and authz-policy-admin installs stay as they were | the diff of `e2e-install` / `parity-install` |

Command lines in the changed files:

| Command | Runs in | Outcome |
| --- | --- | --- |
| `make test-stand-files`, `make e2e-harness`, `make e2e-suite`, `make parity-harness`, `make parity-suite` | `integration-tests.yaml`: lint job, `kind-e2e`, `kind-parity` | covered |
| `helm lint helm-templates/authz-test-stand -f …` | `integration-tests.yaml` lint job | covered |
| `docker build … -f build/authz-agent-transfer/Dockerfile .` | release workflow and dev CI | covered |
| Chart README `docker create` / `docker cp` / `docker rm` | none | I ran it locally: it works, and the copied chart renders. |
| Chart README `helm upgrade --install … --set TAG=<version>` | none | Depends on the image tag the external `docker-action` derives from the git ref `v<version>`. Nothing in the repository settles whether that tag is `1.0.0` or `v1.0.0`. |
| **Chart README:64 `helm test authz-test-stand --timeout 15m --logs`** | none (the Makefile runs it without `--logs`) | See below. |
| Docs "A subset" `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` | none | From reading it, the outcome holds: the chart is unchanged and `--reuse-values` keeps `suite.env.BASE_URL`. |

On `--logs`: the suite hook is a Job. In Helm v3.15.2, `ReleaseTesting.GetPodLogs` (`pkg/action/release_testing.go:127`) reads the logs of a Pod named after the hook, `parity-suite`. A Job's Pod has a generated suffix, so that call fails with "unable to get pod logs for parity-suite" and `helm test` exits non-zero even when the suite passed. That contradicts README:67, "exits non-zero when the suite fails". CI uses Helm v4.3.1, whose behaviour here I did not check, and the README names no Helm version.

Hunks no commit sentence claims:
- **`test/svt/common/compose/docker-compose.yml`**: Keycloak bumped from `26.0` to a pinned `26.3.5`.
- **`.github/docker-dev-config.json`**: three more images built and published by dev CI. The message says only that the *release* publishes them, "from `.qubership/docker.cfg`".
- **`test/k8s/parity/idp-seed/parity-realm.json`**: 318 added lines. They add clients `parity-m2m-tenant-a`, `-b`, `-unknown`, `-empty` and `parity-end-user-tenant-a`, users `parity-r29-scope`, `parity-r30-scope`, `mt-a`, `mt-a-admin`, and roles `ROLE_MT_*`. The message claims only `parity-mt-b`, and no suite code refers to any of them.
- The old e2e Keycloak passed `-Dkeycloak.migration.strategy=OVERWRITE_EXISTING`; the chart drops it. This is harmless, since each Pod starts with an empty database.

## Item 3: boundaries, partitions, and the negative control

- **pipstub:** the controls are present (a routed path keeps its own answer; 404 without a default route; 404 with an empty default route). The missing partition is a routed path with empty responses and no default route (Item 2).
- **State an earlier version left behind:** the old `e2e-harness` and `parity-harness` created these objects with `kubectl apply`:
  - Deployments `keycloak`/`idp`, `pip-stub`, `pip-mock`, `entitlements-mock`, `tenant-manager`;
  - the Services of the same names;
  - the Secret `authz-agent-client-credentials`;
  - the ConfigMaps `keycloak-realms`, `parity-realms`, `pip-mock-config`;
  - the ServiceAccount `runtime-suite`.

  `helm upgrade --install authz-test-stand` on a kind cluster that still has them meets objects with no Helm ownership metadata, and Helm refuses to adopt them. No run starts from that state, and neither the docs nor the READMEs give the remedy (`make e2e-down`, or deleting the namespace).
- **Values users already pass (`E2E_HELM_ARGS` now reaches the test-stand chart):** the names both kinds of chart read are `TAG` and `IMAGE_PULL_POLICY`. The documented `--set IMAGE_PULL_POLICY=Never` is harmless, because Keycloak has its own `idp.imagePullPolicy`. But `--set TAG=<x>`, passed to install the agent at another tag, makes the stand ask for `local/pip-stub:<x>`, `local/tenant-manager:<x>` and `local/authz-runtime-suite:<x>`. `make e2e-images` builds only `:ci`, so with `Never` the harness waits out its 10 minutes.
- **Replaced mechanisms, by fault:**

  | Fault | Old | New |
  | --- | --- | --- |
  | Suite image not loaded into kind (`ErrImageNeverPull`) | `kubectl wait --for=condition=Ready pod … --timeout=3m` fails after 3 min with "timed out waiting for the condition on pods/…" | `wait --for=create` succeeds at once. The log loop polls silently for ~3–4.5 min (90 × (call + 2 s)). `logs -f` then prints the `ErrImageNeverPull` line and exits, but `wait $helm_pid` blocks until the Job's `activeDeadlineSeconds: 900` or Helm's `--timeout 15m`: about 15 min. |
  | Stub image missing in the harness | `rollout status deploy/pip-stub --timeout=2m` fails after 2 min and names the Deployment | `helm --wait --timeout 10m`: 10 min. What Helm 4's waiter prints was not checked. |

  No sentence in the change accepts either slowdown.
- **Limits on the suite run:**
  - `helm test --timeout 15m`, fixed in `Makefile:102` and in chart README:64;
  - `suite.activeDeadlineSeconds: 900`, a documented value in `values.yaml:99`;
  - `-test.timeout 600s` in `suite.args`;
  - the CI job's `timeout-minutes: 30`.

  Raising `suite.activeDeadlineSeconds` above 900 has no effect, because Helm's fixed 15 minutes fires first. At the defaults the Job deadline and Helm's timeout are equal, so neither the Job deadline nor Helm's timeout reliably fires first. Before this change the outer wait was the Job's own deadline.

## Item 3a: level, placement, and the environment

- **pipstub:** small tests sit in the existing `main_test.go`, use its `resetState`, and follow the shape of their neighbours. No finding.
- **Restricted Pod Security Standard:** this is only observable through namespace admission, so no in-process test is owed. But the CI jobs that do exist (`kind-e2e`, `kind-parity`) create the namespace with `--create-namespace` and no `pod-security.kubernetes.io/enforce: restricted` label, so the claim is never exercised.
- **Chart:** CI lints it after `make test-stand-files`, which is placed correctly.
- **`kubectl wait --for=create`:** needs kubectl 1.31 or newer. The prerequisites table (`docs/local-integration-tests.md:37`) names no version. With an older kubectl, the `&&` chain skips the log poll.

## Item 4: names by content, not by position

None. I checked the test-case names, the values comments and the Makefile comments. `$(1)`, `$(2)`, `$(3)` in `run-suite` are positional because make requires it, and they are named in the comment above.

## Item 5: the failure report

None. Each new pipstub assertion prints got and want with the method and target (`GET %s = %d %s, want %d %s`). Every table case is named by its condition. The two-field comparisons print both fields.

## Item 6: what the writer says it verified

None of the three commit messages states a red run on the base commit or a mutation verdict. That includes the regression case "a routed path with no responses", which panicked on the base commit. No CI run of the kind jobs is cited either.

## Item 7: siblings of the change

- **Set of published images (two → five):**
  - `README.md:59` still says "CI builds both via `.github/docker-dev-config.json`", and that file now lists five images.
  - `.github/docs-for-publication-task.md:77` still says "The two-entry array".
  - `helm-templates/authz-agent/values.yaml:8`: its "both" means the two config files, so it is correct.
  - `test/scripts/test-chart-render.sh:439` checks the default image repository of the two product charts. The test-stand chart reads its image repositories from different keys, so this sibling does not apply.
- **Security context:** matches the `authz-agent` and `authz-policy-admin` charts (no `runAsUser`, with the same OpenShift reason).
- **`callRecord`:** `test/parity/suite/pip_control.go:57,77` mirrors the record without `requestUri`. That is consistent with "the stub instance comes with the cases that use it", and its decoder does not reject unknown fields.
- **The docs' own fix list:** the pre-existing-state row from Item 3 is missing from the troubleshooting text.

## Findings

| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| `helm test --logs` reads a Pod named after a Job hook; in Helm 3 it errors and exits non-zero even when the suite passes; not run anywhere | Substantive | `helm-templates/authz-test-stand/README.md:64,67` | Run that form on Helm 3 and Helm 4, or replace it with the Makefile's streaming form and name the supported Helm version |
| Makefile comment says `helm test` prints the log at the end; without `--logs` it prints none | Substantive | `Makefile:95-96` | State what `helm test` prints here |
| Docs say the install creates the suite Job and waits for it; it is a test hook | Substantive | `docs/local-integration-tests.md:104` | Drop "and the suite Job" from the install row |
| `TAG` comment omits `authz-runtime-suite` | Substantive | `helm-templates/authz-test-stand/values.yaml:9-11` | Add it, or say "the images this repository builds" |
| "exactly as before" is ambiguous next to "before the default route existed", which describes the change's history | Substantive | `test/integration/pipstub/main.go:31-38` | State the behaviour: no rules, path routes only; no `*` route means 404 |
| No test of a routed path with empty responses and no default route (the "or to 404" claim, the base-commit panic input) | Substantive | `test/integration/pipstub/main_test.go:503-518` | Add the case |
| No test configures `*` through `/pip-stub/configure` | Substantive | `test/integration/pipstub/main_test.go` | PUT `[{"path":"*",…}]` through `handleConfigure`, then GET an unrouted path |
| The merge, `profile.jq` and the duplicate checks are claimed but never exercised | Substantive | `build/authz-agent-transfer/Dockerfile:333-347`, `profile.jq` | A fixture user file, plus a duplicate pair, run through the `chart-files` stage in CI |
| The restricted Pod Security Standard claim is not run anywhere | Substantive | `Makefile:86,150`, `integration-tests.yaml` | Pre-create the kind namespaces labelled `pod-security.kubernetes.io/enforce=restricted` |
| Installing over objects left by `kubectl apply` fails on Helm ownership; no run and no remedy | Substantive | `Makefile:85-86,149-150`, docs §6 | Document `make e2e-down` (or deleting the namespace) for existing clusters, or show a run over the old state |
| `E2E_HELM_ARGS` now reaches the stand; `--set TAG=<x>` meant for the agent breaks the stand | Substantive | `Makefile:46-48` | A stand-specific variable, or a documented warning |
| A missing suite image now fails after ~15 min instead of 3; a missing stub image after 10 min instead of 2 | Substantive | `Makefile:100-107`, `:86` | Bound the wait (stop `helm test` when `logs -f` fails before the container ran), or accept it in a sentence, with a run of the fault |
| `suite.activeDeadlineSeconds` is capped by the fixed `helm test --timeout 15m`, and the two race at the defaults | Substantive | `Makefile:102`, `values.yaml:99`, README:64 | Derive Helm's timeout from the deadline plus a margin |
| Unclaimed hunks: the svt Keycloak bump, the dev-CI image builds, and the parity-realm clients and users nothing uses | Substantive | `test/svt/common/compose/docker-compose.yml:3`, `.github/docker-dev-config.json`, `test/k8s/parity/idp-seed/parity-realm.json` | A sentence claiming each, or move them to their own change (the realm entries with the cases that use them) |
| Image count stale after adding three images | Substantive | `README.md:59`, `.github/docs-for-publication-task.md:77` | Update both counts |
| `kubectl wait --for=create` needs kubectl ≥ 1.31; the prerequisites name no version | Substantive | `docs/local-integration-tests.md:37` | State the minimum version |
| No test that a matching rule wins over the default route | Taste | `test/integration/pipstub/main_test.go` | Optional: one case with a rule and a `*` route |

Not checked: no kind cluster run, so neither harness was installed and none of the Kubernetes behaviour was observed. I did not read Helm 4's `helm test --logs` code or the external `docker-action`'s tag scheme. The drift script does not parse these languages, so Item 1 rests on reading the diff. There was no style-only pass over the prose.
