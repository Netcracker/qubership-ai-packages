# Final review: `58316ca..HEAD` (4 commits)

**Inputs.** No task statement was handed over, so I took the claimed cases from the four commit messages and the comments above the tests. There was no previous report. `comment-drift.py` printed nothing because it parses only Java, Kotlin, Groovy and Scala, so I checked the three changed Go files and every YAML, Makefile and Markdown hunk by hand. I loaded `test-authoring` (with `references/go/testing.md`) and `english-developer-style`. No Go doc-comment skill was provided, so item 1 rests on the code alone.

Commands I ran:
- `go test ./...` in `test/integration/pipstub`: ok.
- `helm lint` and `helm template` with both values files: clean. Helm 4.3.0, on a copy of the chart in the scratchpad, with `files/` built by copying the sources the Dockerfile copies.
- The `files/` layout I rendered from matches the one `make test-stand-files` produces. I did not run it, because it would write into the checkout.
- The realm checksum changes when realm content changes.
- The missing-files errors match the README text.
- The `profile.jq` merge, run on a made-up user file, fills the fields as described.

## Item 1: comments consistent with the code and with each other

- **`Makefile:99-100`**: the comment says "`helm test` … prints the log only at the end, so the log is streamed while it runs." Commit 5dcb6be found the opposite: Helm 4.3.1 prints nothing for a Job hook, and Helm 3 fails. The Makefile never passes `--logs` anyway. A reader will think removing the streaming loop still leaves a log.
- **`docs/local-integration-tests.md:104`**: says `e2e-harness` "installs … and the suite Job; waits until they are Ready". `test/k8s/README.md:57` and the Makefile both say install does not start the Job, which is correct: a test hook is created only by `helm test`.
- **`test/parity/README.md:69-73`**: says "The `parity` realm … also holds the users of `suite/testdata/realm/` … their files declare none [of the profile fields]". That directory holds only `README.md`, and the commit itself says "none so far". A reader will look for users who do not exist.
- **`README.md:58`**: "CI builds both via `.github/docker-dev-config.json`" is stale. That file now lists five images.
- **`.github/docs-for-publication-task.md:77`**: "The two-entry array in this repository's `docker-dev-config.json`" is stale for the same reason (now five).
- **`test/integration/pipstub/main.go:38-39`**: "as it did before the default route existed" describes the history of the change rather than the behavior (taste).
- **Checked and accurate:**
  - `callRecord.RequestURI`, `defaultRoute`, and the precedence paragraph in `main.go`.
  - `LoadConfig` in `helpers.go`, and the testify `Dockerfile` comment.
  - The comments in `values.yaml` and in each template; `suite.yaml` matches `before-hook-creation`.
  - The `idp-seed/README.md` claims about `mt-b`, `mt-b-admin`, `parity-end-user` and the `tenant-id` claim (checked with jq).
  - The `REALM-DESCRIPTION.md` issuer.
  - No stale references remain to the deleted manifests (checked with `git grep`).

## Item 2: claimed cases covered

Claims, and what covers each:

**Commit 8b85515**
- **Every part off by default:** my `helm template` with defaults renders 0 objects. No CI assertion.
- **Keycloak imports realms at every start and restarts on change:** the `checksum/realms` annotation; I checked by hand. No CI assertion.
- **pip-stub instances, tenant map, Secret:** `helm lint` of both values files in the `chart` job, plus the `kind-e2e` and `kind-parity` jobs.
- **Suite Job as a `helm test` hook; harness and suite targets:** `kind-e2e` and `kind-parity` (`make e2e-suite`, `make parity-suite`).
- **Agent and admin resource profiles unchanged:** the diff shows the same arguments.
- **`make test-stand-files`:** the `chart` job runs it.
- **Merging user files and filling profile fields, and failing on a duplicate:** **no test, and no input exercises them**, because there are no user files.
- **Transfer image with three charts:** built by the dev CI through `docker-dev-config.json`. Its contents are not asserted.
- **Release publishes three more images:** `docker.cfg`. The release workflow is manual and no dry run is cited.

**Commit 17b17fc**
- **The stand starts under the restricted Pod Security Standard:** **nothing runs it in a namespace that enforces restricted.** `git grep pod-security` finds nothing in the Makefile or CI.
- **Labels and `helm.sh/chart`:** rendered, but not asserted.

**Commit 9d25da7**
- **Default route answers unrouted paths, and a routed path keeps its own answer:** `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`.
- **Default route serves its responses in sequence across paths:** `…ServesItsSequenceAcrossPaths`.
- **`requestUri`:** `…RecordsTheRequestTargetAsSent`.
- **A route with no responses falls through to the default route:** the table row `a routed path with no responses gets the default answer`.
- **"…or to 404" (the −1-index crash with no default route):** **no case.** The 404 rows use the unrouted `/users/u-1`, never `/routed` with empty responses.
- **"`/pip-stub/configure` now takes the path `*`":** **no test goes through `handleConfigure`.** The tests write `routes[defaultRoute]` directly.

**Commit 5dcb6be**
- **`E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT`:** CI runs only the 15m default. A raised value is never run (see item 3).
- **README `kubectl logs job/<name>` form:** equivalent to `make parity-suite` on Helm 4.3.1. Helm 3 is cited from the writer's run; CI has no Helm 3 job.
- **`make e2e-down` remedy:** the error text is quoted, but no run of the remedy on a cluster left by the old harness is stated.

Commands the change documents:

| Command | Outcome promised | What runs it |
| --- | --- | --- |
| `make test-stand-files` | generates `files/` | `chart` job |
| `docker build -f build/authz-agent-transfer/Dockerfile .` | transfer image | dev CI build |
| `docker create … true` / `docker cp` / `docker rm` (chart README) | charts copied out | none |
| `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml` | stand from published images | none |
| `helm test authz-test-stand --timeout 15m; kubectl logs job/parity-suite` | suite outcome and log | `make parity-suite` (Helm 4.3.1); Helm 3: none |
| `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false` then `make e2e-suite` | runs a subset | none |
| `make e2e-down`, then `make e2e` | clears the old harness objects | none |

For the "none" rows:
- **`docker create … true`:** `create` does not execute `true`, so it works on a scratch image.
- **Install from published images:** depends on the `ghcr.io/netcracker/qubership-authz-{pip-stub,parity-suite}:<version>` names. They match the chart defaults and `docker.cfg`.
- **`--reuse-values`:** exists in Helm 3 and 4, and `$(RUNTIME_SUITE_RUN)` is expanded by the kubelet.

I found no contradiction in any of these, but none has been run in the documented form. The request is one run of the install from the transfer image and one of the subset recipe.

Hunks that no commit sentence claims:
- **`test/svt/common/compose/docker-compose.yml:3`:** Keycloak `26.0` → `26.3.5@sha256:…` in the SVT compose stack, which this change otherwise does not touch.
- **`test/k8s/parity/idp-seed/parity-realm.json` (+318 lines):**
  - new clients: `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`;
  - new users: `parity-r29-scope`, `parity-r30-scope`, `mt-a`, `mt-a-admin`;
  - new roles: `ROLE_MT_*`.

  The commit claims only "a second tenant realm, parity-mt-b", and nothing in the repository uses these entries yet.
- **`.github/docker-dev-config.json`:** three images added to the dev CI build. The commit claims only the release (`docker.cfg`).

## Item 3: boundaries, partitions, and the negative control

- **pip-stub, missing cases:**
  - A routed path with empty responses and no default route should return 404. This is the base commit's crash and is untested (item 2).
  - Rule precedence over the default route: no case has both a matching rule and a `*` route. `TestHandlePIP_RuleThenLegacyFallback` sets no default.
  - Present: the control "unrouted path, no default route → 404" (green on base), and the empty-default case.
- **Chart, invalid partitions:** none are in CI. These are the `required` / `fail` paths: missing `files/`, empty `tenantManager.tenants`, missing `TAG`, missing `clientCredentials.*`. I confirmed the two missing-files messages by hand.
- **State an earlier version left behind:** the change meets it (the `kubectl apply` objects of the old harness) and offers a documented remedy, but no run of that remedy on that state is stated (item 2).
- **Values users already pass:** `E2E_HELM_ARGS` now reaches the test-stand chart (`Makefile:90,155`). The keys `TAG` and `IMAGE_PULL_POLICY` are read by all three charts. Some consequences:
  - `E2E_HELM_ARGS='--set TAG=1.2.3 --set IMAGE_REPOSITORY=ghcr.io/…'`, used to test a published agent, now makes the stand ask for `local/pip-stub:1.2.3` with `IMAGE_PULL_POLICY: Never`. The result is `ErrImageNeverPull`, and `e2e-harness` waits its full 10 minutes before failing.
  - `--set IMAGE_PULL_POLICY=Always` makes the stand try to pull the `local/*` images from a registry.
  - A `--timeout` meant for the product charts also overrides the harness's 10m.
- **Limits on the suite run** (commit 5dcb6be moves one):
  - `helm test --timeout`: `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` (`Makefile:52-53`), 15m. Its clock starts before the Job exists.
  - The Job's `activeDeadlineSeconds`: `values.yaml:99`, 900s, counted from the Job's start.
  - **`go test -test.timeout 600s`:** `values.yaml:95-96` and `test/k8s/test-stand-values.yaml:55-56`. It sits inside the run and fires first at the defaults, which is fine. But the Makefile comment (`:49-50`) says a longer suite "raises this together with `suite.activeDeadlineSeconds`". A suite that follows that advice still panics at 10 minutes, so raising `E2E_SUITE_TIMEOUT` has no effect.
  - **CI `timeout-minutes: 30`** (`integration-tests.yaml:120,168`): this encloses image builds, the 10m harness wait, two 5m installs, and the suite. A suite timeout raised past what is left of that budget is cut by the job's own limit.
  - **When the helm timeout equals `activeDeadlineSeconds`** (as the chart README at line 69 allows, and as the defaults are): helm fires first, by the time it took to schedule the Pod. Helm then reports a timeout while the Job keeps running, which is the very symptom the commit says it fixed.

## Item 3a: level, placement, and the environment

- **pip-stub tests:** they are small, in-process (`httptest`), and sit beside the file's existing `TestHandlePIP_*` tests, sharing its `resetState`. `go-build.yaml:63` runs the module. None.
- **Chart behavior:** the security contexts, labels and failure messages are observable through `helm template` in one process. `test/scripts/test-chart-render.sh` already holds such assertions for the other two charts and none for `authz-test-stand`. That is the place to request the in-process checks:
  - every Pod has `runAsNonRoot` and `RuntimeDefault`;
  - every container drops `ALL` and sets `allowPrivilegeEscalation: false`;
  - every container but Keycloak has a read-only root filesystem;
  - the `fail` messages render.
- **OpenShift claim:** the commit says no `runAsUser` is pinned "as in the authz-agent chart" so that OpenShift can assign a uid. But the agent chart also turns `readOnlyRootFilesystem` off on OpenShift (`helm-templates/authz-agent/templates/deployment.yaml:266`, "as the platform's charts do"), while the stand hard-codes `true` for its `qubership-core-base` images. Nothing in the change runs it on OpenShift, and I could not check what the base image writes there.

## Item 4: names by content, not by position

None. The test names and table rows name the condition (`an unrouted path with an empty default route is 404`). The `$(1)…$(4)` in the `run-suite` macro are Make's positional parameters, each documented by content.

## Item 5: the failure report

None. Every new check uses `t.Errorf` / `t.Fatalf` with got before want (`GET %s = %d %s, want %d %s`; `statuses of /a, /b, /a = %v, want %v`). `RecordsTheRequestTargetAsSent` joins two comparisons in one `if` but prints all four operands. Table rows run through `t.Run` with named cases.

## Item 6: what the writer says it verified

- **pip-stub:** no red run on the base commit and no mutation verdict is stated for the `-1`-index fix or the default route.
- **Helm logs:** commit 5dcb6be cites observed Helm 4.3.1 and 3.22.1 behavior and the ownership-metadata error, which is evidence for those README sentences.
- **Restricted PSS:** no run is stated.
- **Limits:** no run with a raised suite timeout is stated.

## Item 7: siblings of the change

- **New Makefile settings missing from the override list:** `test/k8s/README.md:66-70` lists every Makefile override (`KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, `E2E_ARTIFACTS`, `E2E_HELM_ARGS`, `E2E_BASE_URL`, `PARITY_AC_BASE_URL`) but not `E2E_SUITE_TIMEOUT` or `PARITY_SUITE_TIMEOUT`.
- **Stale image counts after three images were added:** `README.md:58` ("builds both") and `.github/docs-for-publication-task.md:77` ("two-entry array"); see item 1.
- **Remedy row covers one of two paths:** in the troubleshooting row at `docs/local-integration-tests.md:190`, the symptom names `make e2e-harness` **or** `make parity-harness`, but the action names only `make e2e`. A parity user needs `make parity` after `make e2e-down`. `test/parity/README.md`, which parity users read, has no such note.
- **Other `helm test` mentions:** `Makefile:99` is the remaining wrong statement about the log (item 1). The rest are accurate.
- **pip-stub default route vs. rule config:** `/pip-stub/reset` keeps routes, including `*`, as it does for every route. That is consistent. No other caller indexes `routes` by path.

## Findings

| # | Finding | Label | File:line | Request |
| --- | --- | --- | --- | --- |
| 1 | Inner `-test.timeout 600s` fires first when a suite is raised as the Makefile advises; CI's 30-minute job limit encloses the suite; helm's timeout equal to `activeDeadlineSeconds` fires first | Substantive | `Makefile:49-53,104`; `helm-templates/authz-test-stand/values.yaml:95-99`; `test/k8s/test-stand-values.yaml:55-56`; `helm-templates/authz-test-stand/README.md:69`; `.github/workflows/integration-tests.yaml:120,168` | Derive `-test.timeout` and the helm wait from `activeDeadlineSeconds` (helm wait = deadline + a stated margin), or document all three together; name the CI limit |
| 2 | `E2E_HELM_ARGS` now reaches the stand; `TAG` / `IMAGE_PULL_POLICY` meant for the product charts break the stand | Substantive | `Makefile:44-46,90,155` | A stand-only setting such as `TEST_STAND_HELM_ARGS`, or a run with `--set TAG=<x>` |
| 3 | Comment says `helm test` prints the log at the end; it prints none for a Job | Substantive | `Makefile:99-100` | State that helm prints no log for the Job, so the target streams it |
| 4 | No pip-stub case for a routed path with empty responses and no default route (the −1 crash), none for rule precedence over `*`, none through `/pip-stub/configure` | Substantive | `test/integration/pipstub/main_test.go:225-258` | Add the row `/routed`, `[]pipResponse{}`, no default → 404; a rule + `*` case; one case that configures `*` through `handleConfigure` |
| 5 | The restricted-PSS claim is never run under enforcement, and the stand chart has no render assertions | Substantive | `helm-templates/authz-test-stand/templates/_helpers.tpl:17-40`; `test/scripts/test-chart-render.sh` | Label the kind namespaces `pod-security.kubernetes.io/enforce=restricted`, and add stand assertions to the render script |
| 6 | Read-only root filesystem is hard-coded on OpenShift, while the agent chart turns it off there | Substantive | `helm-templates/authz-test-stand/templates/pip-stub.yaml:58`, `suite.yaml:57`, `tenant-manager.yaml:48` | A run on OpenShift, or the agent chart's `PAAS_PLATFORM` condition |
| 7 | Profile fill and duplicate-user check are never exercised (no user files) | Substantive | `build/authz-agent-transfer/Dockerfile:40-46`; `profile.jq` | A fixture user file in a build test, plus a duplicate that must fail |
| 8 | Unclaimed hunks: SVT Keycloak pin; new parity-realm clients, users and roles; dev-CI image entries | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `test/k8s/parity/idp-seed/parity-realm.json`; `.github/docker-dev-config.json:12-26` | A sentence that claims each, or move them to a change of their own |
| 9 | Parity README describes testdata users that do not exist | Substantive | `test/parity/README.md:69-73` | Say the directory is empty for now and what a file there gets |
| 10 | Docs say `e2e-harness` installs and waits for the suite Job | Substantive | `docs/local-integration-tests.md:104` | Drop "and the suite Job", as `test/k8s/README.md:57` does |
| 11 | Stale image counts ("both", "two-entry") | Substantive | `README.md:58`; `.github/docs-for-publication-task.md:77` | Count the images the file now lists |
| 12 | New timeout settings missing from the README's override list | Substantive | `test/k8s/README.md:66-70` | Add `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` |
| 13 | Remedy row names two harness targets, but its action covers only the e2e one | Substantive | `docs/local-integration-tests.md:190`; `test/parity/README.md` | "`make e2e-down`, then `make e2e` or `make parity`", and the note in the parity README |
| 14 | Documented forms with no run: install from the transfer image, the subset recipe, the `e2e-down` remedy on the old harness's state | Substantive | `helm-templates/authz-test-stand/README.md:39-67`; `docs/local-integration-tests.md:135-143,190` | One run of each, with its output |
| 15 | Package comment describes the history of the change ("as it did before the default route existed") | Taste | `test/integration/pipstub/main.go:38-39` | Describe the behavior only |
| 16 | No test-stack line in `AGENTS.md` (test-authoring §0) | Taste | `AGENTS.md` | Proposed: `Tests: Go testing (engine and assertions) for test/integration/pipstub; testify in test/integration/testify` |

Not checked:
- I did not run `make test-stand-files` or the Docker builds, and there was no cluster, so nothing ran on kind, under PSS enforcement, on OpenShift, or on Helm 3.
- My `helm` checks used Helm 4.3.0, not the 4.3.1 that CI pins.
- The Go comments were checked by hand because the drift script does not parse Go.
- No separate pass over the prose for style was done.
