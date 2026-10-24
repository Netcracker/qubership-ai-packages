# Final review: `58316ca..HEAD` (four commits)

**Inputs.** I had no task statement, so the claimed cases come from the four commit messages and the comments of the new tests, as the skill allows for a subagent that cannot ask. There is no previous report on this change, so there is no table of earlier findings. `comment-drift.py` ran and printed nothing, because it only parses JVM files (`EXT = (".java", ".kt", …)`). I did its work for the Go members by hand: the package comment, `callRecord`, `defaultRoute`, `handlePIP`, `serve`, the three new tests, and `LoadConfig`.

**What I ran:**
- `go test ./...` and `go vet` in `test/integration/pipstub`: both pass.
- `helm lint` and `helm template` with both stand values files, on a copy of the chart in the scratchpad with hand-copied `files/`: both pass.
- `helm template` with defaults renders nothing, which confirms "off by default".
- `jq` with `profile.jq` on sample users: `parity-r29-level-m2m` becomes `R29LevelM2M`, as claimed.
- `kubectl logs --help`: `--pod-running-timeout` defaults to 20s.

## Item 1: comments consistent with the code and with each other

- **Makefile:193–194 contradicts the chart README and commit 4.** The Makefile says "`helm test` … prints the log only at the end, so the log is streamed while it runs". `helm-templates/authz-test-stand/README.md:61-62` and commit 5dcb6be say Helm prints nothing for a Job (Helm 4) or fails (Helm 3). A reader of the Makefile expects `helm test` to print the suite log.
- **`docs/local-integration-tests.md`, `e2e-harness` row (§3 table).** It says the harness installs "… and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` (`templates/suite.yaml:21`), so installing the chart does not create it. The `test/k8s/README.md` row for the same target correctly leaves the Job out.
- **`test/parity/suite/pip_control.go:29-32` is now false (sibling comment, not edited).** Caveat 3 says "Path matching is strictly literal … No wildcards". The `*` default route is a catch-all. There is also a new interaction this comment should state: a path that `ResetPinnedRoutes` re-pins to a 404 response has responses, so it shadows the default route.
- **`test/k8s/parity/idp-seed/parity-realm.json:30` names a test that does not exist.** The `ROLE_MT_READER` description cites `TestTenantScopedDecisions`; `git grep` finds it nowhere else.
- **`pipstub/main.go:37-38` narrates the change.** "…answers an unrouted request 404, as it did before the default route existed." The rest of the new package paragraph, the `callRecord.RequestURI` comment, and the `defaultRoute` comment are accurate. I checked that `OPTIONS *` never reaches `handlePIP`, so "No request path is *" holds.
- **Unchanged comments.** `LoadConfig` and the testify Dockerfile comments point at `suite.env` and `suite.args`, which exist.

## Item 2: claimed cases covered

| Claimed case | Covered by |
| --- | --- |
| Unrouted path → default route | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| Routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| Route with no responses → default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| Route with no responses, no default route → 404 (the old index -1 bug) | **none.** The 404 rows use an *unrouted* path |
| No `*` configured → 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| Default route answers in sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` (checks the struct field, not the JSON name) |
| `/pip-stub/configure` takes `*` | **none.** The tests write `routes[defaultRoute]` directly |
| Rules still take precedence over the default route (package comment) | **none** |
| Chart parts off by default | none in CI; my `helm template` shows it |
| Keycloak restarts when a realm file changes | none |
| Merge of `testdata/realm/` users, profile fill-in, build fails on a duplicate | **none.** No user file exists, so the `jq` merge, `profile`, and both uniqueness checks never get input |
| Restricted PSS, labels on every object | **none.** The kind namespaces come from `--create-namespace` with no `pod-security.kubernetes.io/enforce` label, and no render assertion checks them |
| Suite as a helm test hook, harness installs | kind-e2e and kind-parity CI jobs (Helm v4.3.1) |
| `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` let a suite outlast 15m | none, and see the limits under Item 3 |

**Command lines in the changed files:**

| Command | What runs the same form |
| --- | --- |
| `make test-stand-files` | CI `chart` job, and the kind jobs through `e2e-harness` |
| `docker build … build/authz-agent-transfer/Dockerfile .` | `.github/docker-dev-config.json` |
| Chart README step 1 (`docker create … true`, `docker cp`) | **none** (low risk: the image is FROM scratch and is only created, not run) |
| Chart README step 2 (`helm upgrade --install … --set TAG=<version>`) | **none** |
| Chart README step 3 (`helm test --timeout 15m`, then `kubectl logs job/parity-suite`) | **none.** The Makefile streams the log during the run, on Helm 4 only |
| Subset recipe in `docs/local-integration-tests.md` (`helm upgrade --reuse-values …`, then `make e2e-suite`) | **none** |
| Troubleshooting row (`make e2e-down`, then `make e2e`) | trivially correct for e2e, but see Item 7 |

What the untested step 3 depends on: the Pod must still exist after `helm test` returns. When `activeDeadlineSeconds` fires, the Job controller deletes the running Pod. `kubectl logs job/…` then waits its 20s `--pod-running-timeout` and fails, on every Helm version. So the log is lost in exactly the case it is wanted.

**Hunks that no sentence of the commit messages claims:**
- `test/svt/common/compose/docker-compose.yml`: Keycloak goes from `26.0` to `26.3.5@sha256:…`.
- `.github/docker-dev-config.json`: three new dev-CI builds. The commit message only claims the release, through `docker.cfg`.
- `parity-realm.json` +318 lines: the `parity-m2m-tenant-{a,b,unknown,empty}` clients, `parity-end-user-tenant-a`, and the users `mt-a`, `mt-a-admin`, `parity-r29-scope`, `parity-r30-scope`. The commit message claims only `parity-mt-b`, and no test uses any of these.
- `REALM-DESCRIPTION.md`: the `/auth` correction to the issuer. This one is taste.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub.** The negative control is present (no `*` gives 404). The empty partition for the default route is present. The empty partition for a routed path with no default route is missing (see Item 2).
- **Earlier state.** The old-cluster state is handled by the documented remedy, `make e2e-down`, which deletes the cluster and so obviously works.
- **Values users already pass through `E2E_HELM_ARGS`.** The stand chart and the agent charts both read `TAG` and `IMAGE_PULL_POLICY`.
  - `--set TAG=<x>`, meant for the agent, makes the stand ask for `local/pip-stub:<x>`, `local/tenant-manager:<x>` and `local/authz-runtime-suite:<x>` under `Never`. Nothing builds those tags, so `e2e-harness` fails after 10 minutes.
  - `IMAGE_PULL_POLICY=Always` makes the kubelet try to pull `local/pip-stub:ci` from a registry, which fails.
  - Only the documented example value, `Never`, is harmless.
- **Replaced mechanisms, by fault:**
  - Missing image (`ErrImageNeverPull`, the fault the troubleshooting table names):
    - Old `e2e-suite` failed at 3 minutes (`wait --for=condition=Ready pod`).
    - New `e2e-suite`: the poll loop hides about 3.5 minutes of errors, `logs -f` prints one waiting error, then `wait $helm_pid` blocks until the Job deadline or the 15-minute helm timeout. That is about 15 minutes.
    - The old harness failed at 2 minutes on `rollout status deploy/pip-stub` and named the Deployment. The new single `helm --wait --timeout 10m` fails at 10 minutes.
  - No Pod created (admission rejection or quota), the fault on which one loop attempt waits longest:
    - Each `kubectl logs job/…` blocks for the 20s `--pod-running-timeout`. 90 × (20s + 2s) is about 33 minutes, with output sent to `/dev/null`.
    - That passes both the 15-minute helm timeout and the 30-minute CI job timeout.
    - The old `kubectl wait … -l job-name=…` failed at once with "no matching resources".
    - `Makefile:195-196` ("polls for up to three minutes") is false here.
  - No sentence in the change accepts these later failures.
- **Other limits on the suite:**

  | Limit | Set at |
  | --- | --- |
  | `-test.timeout 600s` | `suite.args` (`values.yaml:95-96`, `test/k8s/test-stand-values.yaml:55-56`) |
  | `activeDeadlineSeconds: 900` | `values.yaml:99` |
  | `helm test --timeout 15m` | `Makefile:51-52` |
  | `timeout-minutes: 30` on the job | `integration-tests.yaml`, kind-e2e and kind-parity |

  - Raising `activeDeadlineSeconds` and `E2E_SUITE_TIMEOUT` together, as `Makefile:129-130` and `README.md:69-70` advise, has no effect past 600s: `go test` panics first. Neither comment names `-test.timeout`.
  - In CI, any value past about 30 minutes minus the build and install time is cut off by the job timeout.
  - At the defaults, the Job deadline (900s) and helm's 15m are equal, so which fires first is a race.

## Item 3a: level, placement, and the environment

- The pip-stub tests are in-process and sit beside the existing tests in `main_test.go`, sharing `resetState`. Good.
- The chart's security contexts, labels, off-by-default rendering, and `fail` messages can all be observed with `helm template`, which needs no cluster. They are covered only by `helm lint`, which asserts none of them. The request is assertions in `test/scripts/test-chart-render.sh`, beside the agent chart's.
- The restricted standard depends on admission, so it also needs a kind namespace labeled `enforce=restricted`.

## Item 4: names by content, not by position

None found. Table case names are by condition; I grepped the added lines for ordinals and positional words. The one weak spot is `values.yaml:11` ("…pull policy below"), which is taste.

## Item 5: the failure report

None found. Every new `t.Errorf`/`t.Fatalf` prints got and want with the input (`GET %s = %d %s, want %d %s`, and so on), and table ids are names, not indexes. The chart's `fail` texts name the missing file and the remedy.

## Item 6: what the writer says it verified

No commit states a red run on the base commit or a mutation verdict for the pip-stub tests. Commit 5dcb6be quotes observed Helm 4.3.1 and 3.22.1 behavior and the ownership-metadata error, which is evidence for the documentation claims only.

## Item 7: siblings of the change

- `run-suite` has two callers, and both are updated.
- **The override list in `test/k8s/README.md:66-71` leaves out the new `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`.** Nothing outside the Makefile names them.
- **Stale counts of the images:**
  - `README.md:59`: "CI builds both via `.github/docker-dev-config.json`". It now lists five.
  - `.github/docs-for-publication-task.md:77`: "The two-entry array". It now has five.
- **The troubleshooting row in `docs/local-integration-tests.md`.** Its symptom names `make e2e-harness` or `make parity-harness`; its action says to run `make e2e-down`, then `make e2e`. It names no step for the parity path (`make parity`).
- The `PipStubCall` mirror in `pip_control.go` lacks `requestUri`. That is acceptable, since commit 9d25da7 defers its consumer.

## Findings

| # | Finding | Label | File:line | Requested change |
| --- | --- | --- | --- | --- |
| 1 | The log poll loop can run about 33 minutes when no Pod is created; the comment says 3 | Substantive | `Makefile:195-205` | Bound the whole wait at a deadline (for example `--pod-running-timeout=2s` plus an overall limit), and run the no-Pod fault |
| 2 | The new suite and harness waits fail later than the old ones (3m→~15m, 2m→10m) on a missing image | Substantive | `Makefile:89,199-206` | Run the `ErrImageNeverPull` fault and report its time and output; bound it, or add a sentence that accepts it |
| 3 | `-test.timeout 600s` and CI's 30-minute job timeout make a raised `*_SUITE_TIMEOUT` useless | Substantive | `Makefile:129-132`, `values.yaml:95-99`, chart `README.md:69` | Derive the limits from one another (deadline ≥ test timeout + margin, helm ≥ deadline + margin), and name `-test.timeout` and the CI limit |
| 4 | The Makefile says `helm test` prints the log at the end; the README and commit say it prints nothing for a Job | Substantive | `Makefile:193-194` | Fix the sentence |
| 5 | The docs say `e2e-harness` installs the suite Job and waits for it | Substantive | `docs/local-integration-tests.md` §3 table | Drop the Job from that row |
| 6 | `pip_control.go` caveat 3 ("No wildcards") is now false | Substantive | `test/parity/suite/pip_control.go:29-32` | Update it, including the re-pinned-404 shadowing |
| 7 | No test of a routed path with no responses and no default route (the index -1 regression), of configuring `*` through `/pip-stub/configure`, or of a rule beating the default route | Substantive | `test/integration/pipstub/main_test.go:505-537` | Add these rows or tests |
| 8 | Restricted PSS and the labels are never checked by a render assertion or a restricted namespace | Substantive | `templates/_helpers.tpl`, `.github/workflows/integration-tests.yaml` | Render assertions, plus `enforce=restricted` on the kind namespaces |
| 9 | User merge, profile fill-in, and duplicate failure have no run with input | Substantive | `build/authz-agent-transfer/Dockerfile:338-352` | A fixture run with one user file and one duplicate |
| 10 | `E2E_HELM_ARGS` values for `TAG` or `IMAGE_PULL_POLICY` now break the stand | Substantive | `Makefile:46-48,90,155` | A separate setting for the stand, or a run with such a value |
| 11 | The README's sequential `kubectl logs job/…` loses the log when the deadline fires; steps 1–3 and the subset recipe are never run | Substantive | chart `README.md:39-67`; `docs/local-integration-tests.md` subset recipe | Run the documented forms, or document the limitation |
| 12 | Hunks with no claim: svt Keycloak bump, dev-CI image builds, +318 lines of tenant-A clients and users in `parity-realm.json` | Substantive | `test/svt/common/compose/docker-compose.yml:3`, `.github/docker-dev-config.json`, `parity-realm.json` | Claim each in the message, or move it to its own change |
| 13 | The realm role description cites a test that does not exist | Substantive | `test/k8s/parity/idp-seed/parity-realm.json:30` | Name an existing test, or drop the reference |
| 14 | New overrides missing from the README's list of overrides | Substantive | `test/k8s/README.md:66-71` | Add `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` |
| 15 | Stale image counts ("both", "two-entry") | Substantive | `README.md:59`, `.github/docs-for-publication-task.md:77` | Update the counts |
| 16 | Troubleshooting action names `make e2e` only, though the symptom names parity too | Substantive | `docs/local-integration-tests.md` troubleshooting table | Add `make parity` |
| 17 | Comment narrates the change ("as it did before the default route existed") | Substantive | `test/integration/pipstub/main.go:37-38` | State the behavior without history |
| 18 | `/auth` issuer correction rides along without a claim | Taste | `test/k8s/authn/REALM-DESCRIPTION.md` | A sentence in the commit message |
| 19 | "below" refers by position | Taste | `helm-templates/authz-test-stand/values.yaml:11` | "in `idp`" |

**Not checked.** I did not run the kind suites or the CI workflow, since there is no cluster. I did not run `make test-stand-files` or `docker build`, which would write into the checkout. The Helm 3 and 4 behaviors and the ownership-metadata error are as the commits state them, not verified by me. I did not do a style pass over the prose.
