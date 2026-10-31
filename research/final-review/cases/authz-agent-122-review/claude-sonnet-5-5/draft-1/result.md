# Final review of `58316ca..HEAD`

**Inputs.** There is no separate task statement, so the claimed cases come from the three commit messages: `8b85515` (test-stand chart and `helm test` suites), `9d25da7` (pip-stub default route) and `17b17fc` (restricted Pod Security Standard). Item 2 is answered from those alone. I loaded `test-authoring` and `english-developer-style` from the given directory; the Go tests are the only code. `comment-drift.py 58316ca HEAD` printed nothing, so I read the changed Go members by hand. I did not run the suite for item 6. I did run `go test` for pip-stub (it passes). I also ran `helm lint` and `helm template` on a scratch copy of the chart with generated files, for both values files.

## Item 1: comments consistent with the code and with each other

Analogue used for the chart, Makefile, Dockerfile and docs: the statements one file makes about another.

- **Go (`pipstub/main.go`):**
  - The package comment's precedence sentence (rules, then legacy routes, then default route, else 404) matches `handlePIP`.
  - The `callRecord`/`RequestURI` comment is true. Its sentence "a caller that encodes a value in the path differently from one that does not can be told apart" is hard to parse (taste only).
  - No comment narrates the change.
- **`README.md:~60`:** "CI builds both via `.github/docker-dev-config.json`" is now false, because that file lists five images. The next paragraph was edited and this sentence was left. Substantive, filed under item 7.
- **Chart, Makefile, Dockerfile and docs:**
  - Every statement I checked holds: the `_helpers.tpl` comments, the `e2e-restart` comment ("Keycloak … restarts when a realm file changes", true via the `checksum/realms` annotation), the Dockerfile and `profile.jq` headers, and the `test/k8s` and `test/parity` READMEs.
  - The Makefile comment says `helm test` "prints the log only at the end". That is true only with `--logs`; plain `helm test` prints none (taste).
- **Doc comments left above unchanged code:** none found.

## Item 2: claimed cases covered

| Claim | Covered by |
| --- | --- |
| `*` default route answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, "an unrouted path gets the default answer" |
| A routed path keeps its own answer | same test, "a routed path keeps its own answer" |
| A route with no responses falls through to the default route | same test, "a routed path with no responses gets the default answer" |
| No `*`, or an empty `*`, gives 404 as before | same test, "…without a default route is 404" and "…with an empty default route is 404" |
| The default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the request target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` takes `*` | **No test.** Every case writes `routes[defaultRoute]` directly. `handleConfigure` is unchanged and generic, so the claim holds, but nothing exercises it (taste). |
| Pip-mock and entitlements-mock behave as before | The existing tests (unchanged) and the 404 cases above |
| Every Pod non-root with RuntimeDefault seccomp; every container drops ALL and sets no privilege escalation; read-only root except Keycloak; `/tmp` emptyDir on the suite Job; no `runAsUser`; `app.kubernetes.io` labels and `helm.sh/chart`; selectors keep `app:` | **No test.** `test/scripts/test-chart-render.sh` has no assertion for `authz-test-stand`, and CI only runs `helm lint` on it (`integration-tests.yaml:83-84`). My `helm template` run shows the claims hold for the e2e values: four containers read-only, five Pods with `runAsNonRoot`, `emptyDir` sized 256Mi. That is a one-off run, not a check. Substantive. |

Commands the change tells someone to run:

| Command | Runs elsewhere? |
| --- | --- |
| `make test-stand-files` | CI step `integration-tests.yaml:74-77`. |
| `helm lint helm-templates/authz-test-stand -f <values>` (two forms) | CI, same flags. |
| `make e2e-harness`, `e2e-suite`, `parity-harness`, `parity-suite` | CI jobs `integration-tests.yaml` (the "Parity on kind" job is named in `test/parity/README.md`). |
| `helm upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string suite.env.FULL_RUNTIME_SUITE=false` (`docs/local-integration-tests.md:139`) | **none.** |
| `docker create/cp/rm` on the transfer image, then `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml`, then `helm test authz-test-stand --timeout 15m --logs` (`helm-templates/authz-test-stand/README.md:50-64`) | **none.** `--logs` is not what the Makefile runs (its `run-suite` streams the log itself). The release flow is not exercised. |

For the `--reuse-values` command, the outcome depends on the stored release keeping the generated `files/` and `-f` values. I expect it to work, but no run shows it. For the README step the dependence is on `TAG`: the chart `required`-fails on an empty `TAG`, and the README step 2 says to delete `TAG` from the values. That is consistent. For both, the request is a run or removal of the unverified form. I rate them taste because both are documented paths that I expect to work.

**Hunks beyond the claims:**
- `test/svt/common/compose/docker-compose.yml:3` moves Keycloak from `26.0` to `26.3.5@sha256:…`. No sentence of any commit claims it, and SVT is not part of this stand. Substantive. Either claim it with an SVT run, or move it to its own change.
- `test/k8s/parity/idp-seed/parity-realm.json` gains 318 lines, with no deletions. They add two roles, a `parity-level-claim` mapper, a `parity-m2m-tenant-a` client and about 14 users. Commit `8b85515` says only that the parity realm "gains a second tenant realm, `parity-mt-b`". Substantive. The commit should claim these additions, and the cases that use them should be named. I found no reference to `parity-m2m-tenant-a` or `parity-level-claim` outside the realm file.

## Item 3: boundaries, partitions, negative control

- **pip-stub:**
  - Present: the control "a routed path keeps its own answer" (green on the base commit), each 404 partition alone, and an empty default route.
  - A rule match beating the default route is not tested, though the package comment states it (taste).
- **State left behind (substantive).**
  - The previous harness created these objects by `kubectl apply` in `authz-e2e` and `authz-parity`: Deployments `keycloak`, `idp`, `pip-stub`, `pip-mock`, `entitlements-mock`, `tenant-manager`, the matching Services, ConfigMaps `keycloak-realms`, `parity-realms`, `pip-mock-config`, Secret `authz-agent-client-credentials`, and Job `runtime-suite`.
  - The chart now creates objects with the same names. `helm upgrade --install` refuses to adopt objects it does not own ("invalid ownership metadata").
  - Any developer with a cluster from the base commit hits that on the next `make e2e-harness`.
  - The docs and READMEs name only `make e2e-down` for "Cluster left behind", with no note for this transition.
  - Request: a run of `e2e-harness` over a stand from the base commit, with the outcome documented ("delete the namespace or run `e2e-down`"), or a one-line note.
- **Values that now reach the test-stand chart.**
  - `E2E_HELM_ARGS` is now passed to the test-stand install too (`Makefile:86,150`).
  - The names both the agent chart and the test-stand chart read are `TAG` and `IMAGE_PULL_POLICY` (`values.yaml:8-9`; `test/k8s/values.yaml:9` and `policy-admin-values.yaml:6` set `TAG: ci`).
  - The documented example, `--set IMAGE_PULL_POLICY=Never`, is harmless. A user value for `TAG` meant for the agent's images would retag `local/pip-stub`, `local/tenant-manager` and the suite image to a tag `e2e-images` never builds. `IMAGE_PULL_POLICY=Never` then gives `ErrImageNeverPull`.
  - Substantive. Request: a run with `E2E_HELM_ARGS='--set TAG=x'`, or a test-stand-own key (for example `stand.TAG`).
- **Replaced mechanism: the suite wait.**
  - Old (`wait --for=condition=Ready pod` with a 3-minute timeout) failed in at most 3 minutes after `apply`. On an image-pull fault it printed kubectl's timeout error.
  - New (`run-suite`): `kubectl wait --for=create` allows 2 minutes. The log-poll loop (`seq 90`, each probe up to its default request timeout, plus `sleep 2`) allows about 3 minutes, and then `logs -f` returns at once on a container that never started. The recipe then does `wait $helm_pid`.
  - Pod-level faults (pull failure, unschedulable) hold the Job pending. `helm test --timeout 15m` and `activeDeadlineSeconds: 900` bound it, so the failure arrives at about 15 minutes, not 3.
  - It prints no Ready-wait message in the meantime.
  - Substantive. Request: a run of an image-pull fault on the new target, and a deadline that bounds the wait at the old 3 minutes (a `kubectl wait --for=condition=Ready pod -l job-name=… --timeout=3m` before `logs -f`).
- **Limits on one piece of work.**
  - Limits on the suite: `-test.timeout 600s` (`values.yaml:95`, `test-stand-values.yaml:55`), `suite.activeDeadlineSeconds: 900` (`values.yaml:99`), and `helm test --timeout 15m` hardcoded in `Makefile:102` and the README. 15m equals 900s, so at the default the helm timer started first and fires first.
  - A documented setting raised past them has no effect on the make targets. `activeDeadlineSeconds: 1800` cannot be reached, because `helm test` gives up at 15m and the Job keeps running.
  - The inner `-test.timeout` is not derived from either.
  - Substantive, low severity. Request: derive helm's `--timeout` from the Job's deadline.

## Item 3a: level, placement, environment

- pip-stub tests are in-process, beside the existing `TestHandlePIP_*` tests, and reuse `resetState`. The new `serve` helper builds a request/recorder pair the older tests inline (`main_test.go:103-113`). That is acceptable, since the file has no helper yet.
- The chart behaviors are observable under `helm template`, in one process with no cluster. The in-process test owed is a render assertion in `test-chart-render.sh` for `authz-test-stand`, which the item 2 finding already requests.
- Skip-versus-fail: none of the new Go tests is conditional.

## Item 4: names by content

None. Test names and case ids are by content (`an unrouted path gets the default answer`). I found no "the fifth", "see below" or numbered case id in the changed files.

## Item 5: the failure report

None. The assertions use `t.Errorf` with the input and both operands. `TestHandlePIP_RecordsTheRequestTargetAsSent` checks two fields in one `if` and prints both pairs, which is acceptable.

## Item 6: what the writer says it verified

None of the three commit messages states a red run on the base commit or a mutation verdict. Say so.

## Item 7: siblings

- **Helper `handlePIP` and the `routes` map.** Readers of `routes`: `handlePIP`, `handleConfigure`, `loadDefaultRoutes`, `handleReset` (all in `main.go`). Only `handlePIP` selects a route by request path, so the default route does not apply elsewhere. Another `-1` index site: I found none (the same `counters[...]` read is the one hunk changed).
- **Set of images** (`.github/docker-dev-config.json`, `.qubership/docker.cfg`, `docker-release.yaml`). The three new images are listed in the config, the cfg and the release comment. **Stale:** `README.md` "CI builds both via `.github/docker-dev-config.json`" (after the edits at `README.md:~60-66`). Substantive. Request: change "both" to "the images listed in …".
- **Set of chart parts.** The chart README, `values.yaml`, `docs/local-integration-tests.md`, `test/k8s/README.md` and `test/parity/README.md` name the parts consistently. References to deleted files (`keycloak.yaml`, `runtime-suite-job.yaml`, `parity-suite-job.yaml`, `m2m-credentials`, `E2E_AUTHN`, `PARITY_SEED`) return nothing under `git grep`.
- **Symptom paths.** The README's missing-files failure names both the realm files and the stub rule files, and `make test-stand-files` generates both.

## Added instructions

Not applicable: no skill or instruction file is in the change.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Security-context, label and `/tmp` claims of `17b17fc` have no render assertion; CI only lints the chart | Substantive | `test/scripts/test-chart-render.sh` (no `authz-test-stand` case), `integration-tests.yaml:83-84` | 2 |
| Unclaimed Keycloak bump `26.0` to `26.3.5@sha256` in the SVT compose file | Substantive | `test/svt/common/compose/docker-compose.yml:3` | 2 |
| Parity realm gains roles, a mapper, a client and users that no commit sentence claims | Substantive | `test/k8s/parity/idp-seed/parity-realm.json` | 2 |
| Installing over objects `kubectl apply` created on the base commit is neither tested nor documented | Substantive | `Makefile:86,150`, `docs/local-integration-tests.md:193` | 3 |
| `E2E_HELM_ARGS` now reaches the test stand, which shares `TAG` and `IMAGE_PULL_POLICY` with the agent chart | Substantive | `Makefile:47-48,86,150`, `values.yaml:8-9` | 3 |
| An image-pull fault on the suite now fails at about 15 minutes, not 3 | Substantive | `Makefile:100-106` | 3 |
| `activeDeadlineSeconds` above 900 is capped by the hardcoded `helm test --timeout 15m` | Substantive | `Makefile:102`, `values.yaml:99`, `README.md:64` | 3 |
| "CI builds both" is false: five images are built | Substantive | `README.md:~60` | 7 |
| No red run or mutation verdict stated | Substantive (report) | commit messages | 6 |
| `--reuse-values` subset command and the transfer-image install path run nowhere | Taste | `docs/local-integration-tests.md:139`, chart `README.md:50-64` | 2 |
| `/pip-stub/configure` accepting `*` and rule-beats-default are not tested | Taste | `pipstub/main_test.go`, `main.go:27-38` | 2, 3 |
| `RequestURI` comment sentence is hard to parse; "prints the log only at the end" holds only without `--logs` | Taste | `pipstub/main.go:73-76`, `Makefile:93-94` | 1 |

**Checks that could not be done.** `comment-drift.py` printed nothing for Go or YAML, so the Go members were read by hand. I did not run the Docker `chart-files` stage or `make test-stand-files` (no Docker daemon use), so the generated files in my render check are copies of the inputs and not the stage's output. I could not check any behavior on a cluster.
