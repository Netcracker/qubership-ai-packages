# Final review of `58316ca..HEAD`

**Inputs.** I reviewed three commits: 8b85515 (the test-stand chart), 9d25da7 (the pip-stub default route) and 17b17fc (the restricted Pod Security Standard). No task statement was handed over, so item 2 takes the claimed cases from the commit messages, the test comments and the changed READMEs only. There is no previous report. `comment-drift.py` printed nothing and exited 0, because it parses only Java, Kotlin, Groovy and Scala. The change is Go, Helm, YAML, Makefile and Markdown, so I read the members and comments by hand.

**What I ran, without changing the repository:**
- `go test`, `go vet` and `gofmt -l` on `test/integration/pipstub`: all clean.
- `helm lint` and `helm template` (Helm 4.3.0) on a copy of the chart in the scratchpad, with `files/` filled the way the `chart-files` stage does. Both values files lint and render.
- Every rendered Pod has `runAsNonRoot` and `RuntimeDefault` seccomp. Every container has `allowPrivilegeEscalation: false` and drops `ALL` capabilities. All but Keycloak have a read-only root filesystem.
- `profile.jq` on sample users: `parity-r29-level-m2m` becomes `R29LevelM2M`, and fields a user already declares are kept.

## Item 1: comments consistent with the code and with each other

- **`docs/local-integration-tests.md:104`** says `e2e-harness` installs "… and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` (`suite.yaml:21`), so install never creates it. `test/k8s/README.md` says "installing the stand does not start it". A reader looks for a Job after the harness step and finds none.
- **`docs/local-integration-tests.md:190`**, a troubleshooting row, still names `rollout status deploy/keycloak`. That command no longer runs: `e2e-harness` is now `helm upgrade --install … --wait --timeout 10m`, which prints a different error.
- **`README.md:59`** still says "CI builds both via `.github/docker-dev-config.json`". That file now lists five images.
- **`helm-templates/authz-test-stand/values.yaml:9`** lists the images that `TAG` and `IMAGE_PULL_POLICY` apply to as "pip-stub, authz-parity-suite, and tenant-manager". It leaves out `authz-runtime-suite`, which the e2e values run with `TAG`.
- **`test/integration/pipstub/main.go:37-38`**: "as it did before the default route existed" describes the change rather than the code. It is true, so this is taste.
- The other comments I checked hold: `_helpers.tpl`, `suite.yaml:42`, the `idp.yaml` probe arithmetic (60 × 5 s = 5 min), the `callRecord.RequestURI` comment, `defaultRoute`, and the `testify` comments.

## Item 2: claimed cases covered

**Commit 9d25da7:**

| Claimed case | Test |
| --- | --- |
| An unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/"an unrouted path gets the default answer"` |
| A routed path keeps its own answer | same test, "a routed path keeps its own answer" |
| A route with no responses falls through to the default route, or to 404 | "a routed path with no responses gets the default answer", "an unrouted path with an empty default route is 404" |
| No `*` route: 404 as before (the control) | "an unrouted path without a default route is 404" |
| The default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| **`/pip-stub/configure` takes the path `*`** | **none.** Every test writes `routes[defaultRoute]` directly; `handleConfigure` has no test at all. |
| The precedence "rules first, then path routes, then the default route" | **none.** No test has a rule and a `*` route together. |

**Commit 8b85515:**

| Claimed case | Test or run |
| --- | --- |
| Each part off by default | `helm template` with default values renders nothing (my run). No CI assertion. |
| Keycloak restarts when a realm file changes (`checksum/realms`) | none |
| The `chart-files` stage fills in profile fields | **none.** `test/parity/suite/testdata/realm/` holds no `*.json` ("none so far"), so the merge and `profile` run on no input in any build. |
| "The build fails if a user is declared twice" | **none.** The check runs on every build, but its failing branch never does. |
| `make e2e-harness`, `parity-harness`, `e2e-suite`, `parity-suite` | CI jobs `kind-e2e` and `kind-parity` (`integration-tests.yaml:145-197`), the same commands. |
| `helm lint` of both values files | CI job `chart`, the same commands. |
| `make test-stand-files` | CI job `chart`, step "Generate the test-stand files". |

**Commit 17b17fc:**

| Claimed case | Test or run |
| --- | --- |
| "The stand starts in a namespace that enforces the restricted Pod Security Standard" | **none.** The Makefile creates the namespace with `--create-namespace` and no `pod-security.kubernetes.io/enforce` label, so kind admits the Pods under the default (privileged) level. Nothing renders the chart and asserts the security fields either. My static count matches the rules, but whether the `qubership-core-base:2.4.2` entrypoint (pip-stub, both suites) runs on a read-only root needs a run. |
| app.kubernetes.io labels on every object; selectors keep `app` | none (my render only) |

**Command lines in changed files that no CI job runs:**
- **`helm-templates/authz-test-stand/README.md`, transfer-image steps 1–3** (`docker create … true`, `docker cp`, `helm upgrade --install ./charts/authz-test-stand --set TAG=<version>`, `helm test … --timeout 15m --logs`): **none.** The outcome depends on the published images being pullable and on the scratch image accepting `docker create` with a command. That command is never executed, so it should work, but no run shows it.
- **`docs/local-integration-tests.md:139-140`** (`helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false`): **none.** Helm `--set` splits only on `,` and `=` in this value, so `^`, `$` and `/` reach the env var intact. The note that "`make e2e-harness` restores the values" holds, because an upgrade given `-f` without `--reuse-values` starts from the chart defaults. Unrun.

**Hunks no sentence claims:**
- **`test/svt/common/compose/docker-compose.yml`**: Keycloak goes from `26.0` to `26.3.5@sha256:…` in the SVT stack. No commit mentions SVT, and no SVT run is shown.
- **`test/k8s/parity/idp-seed/parity-realm.json`**: +318 lines. Commit 8b85515 claims only "a second tenant realm, parity-mt-b". The file also gains:
  - roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`;
  - five clients (`parity-m2m-tenant-a`, `-b`, `-unknown`, `-empty`, `parity-end-user-tenant-a`) and their service-account users;
  - users `parity-r29-scope`, `parity-r30-scope`, `mt-a`, `mt-a-admin`;
  - a `level` claim mapper.

  No test under `test/parity` refers to any of them (`git grep` for `mt-a-admin`, `ROLE_MT_` and `parity-m2m-tenant` finds only docs).
- **`.github/docker-dev-config.json`**: three new dev-CI image builds. The commit claims only `.qubership/docker.cfg`.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub partitions:** present. Unrouted, routed, routed-empty, no default route, and an empty default route each have their own case; the no-`*` case is the control. Two partitions are missing: a rule match while a `*` route exists, and `*` registered through `handleConfigure`.
- **State an earlier version left: substantive.** On a kind namespace set up at the base commit, the objects were created by `kubectl apply`:
  - e2e: Deployments `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`; ConfigMap `keycloak-realms`; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`;
  - parity: `idp`, `pip-mock`, `pip-mock-config` and the Secret.

  The chart renders the same names. Helm 3 and 4 refuse to adopt objects without its ownership metadata ("exists and cannot be imported into the current release"), so `make e2e-harness` fails on such a stand. CI starts fresh every time, and no doc names the remedy (`make e2e-down`, or deleting those objects).
- **Values users already pass (`E2E_HELM_ARGS`): substantive.** The variable now reaches the test-stand chart (`Makefile:86,150`). The keys it shares with the agent and authz-policy-admin charts are `TAG` and `IMAGE_PULL_POLICY`.
  - The documented example, `--set IMAGE_PULL_POLICY=Never`, means the same thing in all three charts.
  - `--set TAG=<x>`, passed to try another agent build, now also points the stand at `local/pip-stub:<x>`, `local/tenant-manager:<x>` and `local/authz-runtime-suite:<x>`. `e2e-images` builds only `:ci`, so the harness stalls in `ErrImageNeverPull` until `--wait --timeout 10m` runs out.
- **Replaced mechanism (`e2e-suite` and `parity-suite`): substantive.** Most common fault: a missing image (`ErrImageNeverPull`, the troubleshooting row at `docs/…:189`).
  - **Old:** `kubectl wait --for=condition=Ready pod … --timeout=3m` failed after 3 min with a timeout message.
  - **New:** `wait --for=create` succeeds. The poll loop then runs 90 × (`kubectl logs` + 2 s) ≈ 3 min with its output sent to `/dev/null`. `logs -f` then fails at once with the waiting reason, and `wait $helm_pid` blocks until the Job's `activeDeadlineSeconds: 900` or `helm test --timeout 15m` expires.
  - **Result:** about 15 min instead of 3, inside a CI job with `timeout-minutes: 30` that has already spent up to 10 min on the harness. No sentence accepts this.
  - The fault where one attempt waits longest (a suite that hangs) is bounded by `-test.timeout 600s` in both the old and the new mechanism.
- **Limits: substantive.** On the same suite run there are three limits:
  - `suite.activeDeadlineSeconds: 900`, a documented value in `values.yaml:99`;
  - `helm test --timeout 15m`, fixed in `Makefile:102` and `README.md:64`;
  - `-test.timeout 600s` in `suite.args`.

  At the defaults the inner one (`-test.timeout`) fires first, as it should. Raising `activeDeadlineSeconds` past 900 has no effect, because the fixed 15 min Helm timeout fires first and both count from about the same start.

  On the harness, `--wait --timeout 10m` against Keycloak's 5 min startup probe is consistent: the inner limit fires first.

## Item 3a: level, placement, and the environment

- **pip-stub:** the tests are in-process (`httptest`), sit in `main_test.go` beside the existing `TestHandlePIP_*` tests, and share `resetState`. The in-process route through the interface would be `handleConfigure` followed by `handlePIP`; the new tests bypass it by writing the routes map.
- **Chart:** the security context, labels, checksum and default-off behavior can all be seen by rendering, with no cluster. The repository already has that level: `test/scripts/test-chart-render.sh` runs in CI job `chart` for the other two charts. The test stand has no render assertions.
- **Admission under the restricted standard** crosses the cluster boundary, and the CI kind jobs do not enforce it (item 2).

## Item 4: names by content, not by position

- Test and case names are by content.
- `test/k8s/test-stand-values.yaml:294` says "A second instance for the entitlements endpoint" next to the key `entitlements-mock`. That is taste.
- The Makefile's `$(1)`–`$(3)` are make's positional call arguments and are named in the comment.

## Item 5: the failure report

None. Every new assertion prints its operands and expectations: `GET %s = %d %s, want %d %s`, `statuses of /a, /b, /a = %v, want %v`, and `requestUri %q, path %q, want …`. Table cases have names, not indexes.

## Item 6: what the writer says it verified

None of the three commits states a red run on the base commit or a mutation verdict. On the base commit, the routed-empty case would panic at index -1, and the default-route cases would return 404. The chart's PSS claim states no run, kind or otherwise.

## Item 7: siblings of the change

- **`E2E_HELM_ARGS` as a set of consumers:** every place that names the old count ("both chart installs") was updated (`Makefile:46`, `test/k8s/README.md:63`).
- **The image set:** `.qubership/docker.cfg`, `docker-dev-config.json`, the `docker-release.yaml` header and `README.md:61-69` were updated, but `README.md:59` still says "both" (item 1). `test-chart-render.sh` says "both charts" only of the two product charts, which is correct there.
- **Deleted manifests:** `git grep` finds no remaining reference to any of them.
- **`handlePIP` callers:** `handlePIP` is the only reader of `routes` and `counters` besides `handleConfigure`, `handleReset` and `loadDefaultRoutes`. `handleReset` clears the `*` counter along with the others, which is correct.
- **`requestUri` consumers:** `testify` and `test/parity/suite/pip_control.go` decode call records without `DisallowUnknownFields`, so the new field does not break them.
- **The read-only root filesystem:** the parity suite's `writeObservedSidecar` (`compare.go:145`) already failed silently as uid 10001 on root-owned `testdata/`, so this change does not alter it.

## Findings

| # | Finding | Label | File:line | Requested change |
| --- | --- | --- | --- | --- |
| 1 | "Starts under the restricted Pod Security Standard" has no run and no render test | Substantive | `helm-templates/authz-test-stand/README.md:9`; `Makefile:86,150` | Label the harness namespaces `pod-security.kubernetes.io/enforce=restricted` so the CI kind jobs exercise the claim. Add render assertions for the test stand to `test-chart-render.sh`. |
| 2 | `make e2e-harness` on a stand set up at the base commit fails: Helm will not adopt the same-named objects `kubectl apply` created | Substantive | `Makefile:86,150`; `docs/local-integration-tests.md` §6/§8 | Run that transition, or document the remedy (`make e2e-down`, or delete the listed objects) and show it run. |
| 3 | `E2E_HELM_ARGS` now reaches the stand: `--set TAG=x` redirects the stand to images `e2e-images` never builds | Substantive | `Makefile:86,150` | Give the stand its own variable, or pin `TAG=ci` after `$(E2E_HELM_ARGS)`, or run with that value. |
| 4 | A missing suite image now fails after ~15 min instead of 3, with the log silenced for the first 3 | Substantive | `Makefile:100-107` | Stop `helm test` when `logs -f` fails, or bound the wait. Show a run of the missing-image fault with its duration and output. |
| 5 | `suite.activeDeadlineSeconds` above 900 has no effect: `helm test --timeout 15m` is fixed | Substantive | `values.yaml:99`; `Makefile:102`; chart `README.md:64` | Derive one limit from the other, or say the Helm timeout bounds it. |
| 6 | `/pip-stub/configure` with `*` is claimed but untested; so is rules-over-default precedence | Substantive | `test/integration/pipstub/main_test.go:216-278` | Add a case through `handleConfigure`, and a case with a matching rule and a `*` route. |
| 7 | The profile fill and the duplicate-user failure of `chart-files` run on no input | Substantive | `build/authz-agent-transfer/Dockerfile:333-347`; `profile.jq` | Add a fixture user file, or a CI step that runs the stage on a sample with a duplicate. |
| 8 | Unclaimed hunks: the SVT Keycloak bump, the parity-realm additions, `docker-dev-config.json` | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `test/k8s/parity/idp-seed/parity-realm.json`; `.github/docker-dev-config.json` | Add a sentence that claims each, with the run that checks it, or move them to their own change. |
| 9 | Docs say `e2e-harness` installs the suite Job and waits for it to be Ready | Substantive | `docs/local-integration-tests.md:104` | Drop the Job from that row; `helm test` creates it. |
| 10 | The troubleshooting row names `rollout status deploy/keycloak`, which no longer runs | Substantive | `docs/local-integration-tests.md:190` | Describe the `helm --wait` timeout instead. |
| 11 | "CI builds both" now covers five images | Substantive | `README.md:59` | Restate the count or the list. |
| 12 | The `TAG` comment leaves out `authz-runtime-suite` | Substantive | `helm-templates/authz-test-stand/values.yaml:9` | Add it to the list. |
| 13 | `wait --for=create` needs kubectl 1.31+, but the prerequisites table states no minimum | Taste | `docs/local-integration-tests.md:37` | State the minimum version. |
| 14 | "as it did before the default route existed" narrates the change | Taste | `test/integration/pipstub/main.go:37-38` | State the behavior without the history. |
| 15 | "A second instance" names by ordinal | Taste | `test/k8s/test-stand-values.yaml:294` | Say "The entitlements stub". |

**Not checked:** no kind or Kubernetes run, so admission, image entrypoints on a read-only root, and the Makefile timings above come from reading the code and the tools' help text, not from a run. I did not build the Docker stages. I did not check SVT, and I did not make a style-only pass over the prose.
