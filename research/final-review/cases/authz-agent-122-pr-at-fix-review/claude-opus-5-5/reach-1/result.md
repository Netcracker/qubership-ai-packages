I filled in the final-review form for `58316ca..HEAD` (four commits). There was no task statement, so the claimed cases come only from the four commit messages. No earlier report exists, so there is no table of previous findings. The drift script ran but printed nothing, because it only parses Java, Kotlin, Groovy and Scala. I read the changed Go, Makefile, YAML and Markdown comments by hand. The two skills I loaded are `test-authoring` (with `references/go/testing.md`) and `english-developer-style`. No doc-comment skill was supplied for Go.

What I ran: `go test ./...` in `test/integration/pipstub` passes. I also ran `helm lint` and `helm template` (Helm 4.3.0) on a copy of the chart in the scratchpad. I filled its `files/` by hand, because `make test-stand-files` needs `docker build`. Both values files lint and render cleanly. I also ran `profile.jq` on a sample user.

## Item 1: comments consistent with the code and with each other

- **`docs/local-integration-tests.md`, the `e2e-harness` row:** it says the harness installs "… the client-credentials Secret, and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` object, so `helm upgrade --install` never creates it and never waits for it. `test/k8s/README.md` says the opposite ("installing the stand does not start it"). Someone debugging would look for a Job after `make e2e-harness` and not find one.
- **`test/parity/README.md`, "Identity provider":** it says the `parity` realm "also holds the users of `suite/testdata/realm/`, so the cases that need those users run…", and that "their files declare none". That directory holds only `README.md`. The commit message itself says "none so far". The README states as fact that cases and user files exist, and neither does.
- **`Makefile:50-51`** (the `E2E_SUITE_TIMEOUT` comment) and **`helm-templates/authz-test-stand/README.md:69-70`:** both say a longer suite raises the helm wait together with `suite.activeDeadlineSeconds`. Neither mentions `-test.timeout 600s` in `suite.args` (both values files and `values.yaml:95-96`), which ends the run at 10 minutes anyway. Details under Item 3.
- **`test/integration/pipstub/main.go:38`:** "as it did before the default route existed" describes the history of the change inside the package comment. Taste.
- **`values.yaml:9-11`:** "the images this repository builds, pip-stub, authz-parity-suite, and tenant-manager" leaves out `authz-runtime-suite`, which `TAG` also tags through `suite.imageRepository` in the e2e values. Taste.
- I checked these and they are consistent: the `callRecord.RequestURI`, `defaultRoute` and `handlePIP` step-2 comments, the comments in the new test, `LoadConfig`, the testify Dockerfile, `values.yaml`'s `idp`/`pipStub`/`suite` comments, the `_helpers.tpl` and template comments, `REALM-DESCRIPTION.md`, `test/k8s/README.md`, and the idp-seed README.

## Item 2: claimed cases covered

| Claimed case (commit) | Covered by |
| --- | --- |
| A pip-stub route registered under `*` answers unrouted paths (9d25da7) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| No `*` route → 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| …**or to 404** | **none**: no case has a routed path with no responses and no default route. On the base commit this is the input that read index −1, so it is the regression case. |
| `/pip-stub/configure` accepts the path `*` | **none**: every test writes `routes[defaultRoute]` directly and never goes through `handleConfigure` |
| Rules take precedence over the default route (package comment) | **none** |
| `requestUri` keeps the request target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| The default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| The chart parts install, and the suite runs as a `helm test` hook (8b85515) | CI `kind-e2e` and `kind-parity`, plus `helm lint` in `chart` |
| Keycloak restarts when a realm file changes (`checksum/realms`) | **none** (no run and no render assertion) |
| Users under `testdata/realm/` are merged, given profile fields, and the build fails on a duplicate | **none**: there are no user files, so the jq merge, `profile.jq`, and both `jq -e` checks never get input |
| The parity realm gains `parity-mt-b` | **none**: `git grep` finds no use of `parity-mt-b`, `mt-a`, or `parity-m2m-tenant-*` outside `idp-seed/` |
| The transfer image carries three charts under `/charts`, with `files/` | Built by the dev build (`docker-dev-config.json`); nothing checks the layout |
| The stand starts under the restricted Pod Security Standard (17b17fc) | **none**: the harness namespace is created by `--create-namespace` with no `pod-security.kubernetes.io/enforce` label, and `test-chart-render.sh` checks only the agent chart's securityContext |
| Read-only root filesystem everywhere except Keycloak | The kind CI jobs, provided they ran green (not stated) |
| A suite can run past 15 minutes via `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` (5dcb6be) | **none**: no run over 15 minutes, and `-test.timeout 600s` caps it (Item 3) |
| `helm test --logs` prints nothing on Helm 4.3.1 and fails on Helm 3.22.1 | The commit quotes both outputs (an observed run) |

**Commands the change tells people to run:**
- `make test-stand-files`, `make e2e-harness / e2e-suite / parity-harness / parity-suite`: CI runs the same targets on Helm v4.3.1. Covered.
- `docker build … -f build/authz-agent-transfer/Dockerfile .`: the dev build runs the same file and context. Covered.
- The chart README, transfer path (`docker create/cp/rm`, then `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml`): **none**. The outcome depends on published images existing under that `TAG`, and on the values left after the deletions the README lists. Nothing runs this outside kind.
- The chart README, `helm test authz-test-stand --timeout 15m` then `kubectl logs job/parity-suite`: on Helm 4 this matches what `run-suite` runs. On Helm 3: **none**. The plain form's promise ("exits non-zero when the suite fails") depends on how Helm 3 treats a Job test hook, and no run shows it.
- `docs/local-integration-tests.md`, the subset recipe (`helm … upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false`, then `make e2e-suite`): **none**. It looks right to me (no commas in the value; `TestCheckResource` exists), but it has not been run.

**Hunks no commit sentence claims:**
- `test/svt/common/compose/docker-compose.yml`: Keycloak `26.0` → `26.3.5@sha256:…`.
- `.github/docker-dev-config.json`: three new dev-build entries. The commit names only `.qubership/docker.cfg`.
- `test/k8s/parity/idp-seed/parity-realm.json`: +318 lines of clients and users (`parity-m2m-tenant-a/b/unknown/empty`, `parity-end-user-tenant-a`, `parity-r29-scope`, `parity-r30-scope`, `mt-a`, `mt-a-admin`, the `ROLE_MT_*` roles). The commit claims only the `parity-mt-b` realm.
- `REALM-DESCRIPTION.md`: the issuer corrected to `/auth`. It was already wrong on the base commit. Taste.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub:** the control is there (no `*` route → 404). Missing: a routed path with empty responses and no default route (the 404 half); a matching rule while a `*` route exists (the precedence control); and `*` registered through `/pip-stub/configure`.
- **State left by earlier versions:** objects created by `kubectl apply` meet a Helm install. The remedy (`make e2e-down`) is documented and deletes the cluster, so it works on that state. None.
- **Values users already pass:** `E2E_HELM_ARGS` now reaches the test-stand install too (`Makefile:91` and `:156`). Two keys are read by both the old consumers and the new one:
  - `IMAGE_PULL_POLICY` means the same thing in all three charts. Harmless.
  - `TAG` is not. Say someone passes `E2E_HELM_ARGS='--set IMAGE_REPOSITORY=ghcr.io/…/qubership-authz-agent --set TAG=1.4.0'` to test a published agent. The test stand then asks for `local/pip-stub:1.4.0` with `Never`, which nothing builds or loads, so `e2e-harness` fails on `ErrImageNeverPull`. Substantive.
- **Limits on the suite run** (all counted from roughly the start of `helm test`):
  1. `-test.timeout 600s`, fixed in `suite.args` in the values files.
  2. `activeDeadlineSeconds: 900`, from `suite.activeDeadlineSeconds`.
  3. `helm test --timeout 15m`, from `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT`.

  At the defaults the innermost limit, (1), fires first, which is right. But the documented recipe ("raises this together with `suite.activeDeadlineSeconds`") has no effect past 10 minutes, because (1) still ends the run. That is exactly the case the commit was made for. Also, when (2) equals (3), as it does at the defaults, Helm's wait started first and expires first, so a deadline failure shows up as a Helm timeout rather than `DeadlineExceeded`.

  The CI job's `timeout-minutes: 30` covers image builds, the 10-minute harness wait, and two 5-minute installs. So in CI, raising the suite timeout much past ~15 minutes cannot take effect either. That one is not counted from the same start, so I note it rather than file it.

## Item 3a: level, placement, and the environment

The pip-stub behavior is tested in-process, in `main_test.go` next to the existing `TestHandlePIP_*` tests and sharing `resetState`. Good. The chart is checked by `helm lint` in CI. `test/scripts/test-chart-render.sh`, which already asserts the agent chart's securityContext (`:828-834`), has no assertions for the test stand. A render assertion (or a namespace labeled `enforce=restricted` on kind) is the small check the PSS claim is missing.

## Item 4: names by content, not by position

The new names and case ids are by content. One positional problem the change caused: `test/parity/suite/pip_control.go:16-29` cites `pipstub/main.go:50-183`, `:52`, `:110`, and `:152-160`. The added comment and code shifted `main.go`, so those lines no longer point at what they describe (for example, the path lookup is now at `:235`).

## Item 5: the failure report

None. Every `t.Errorf` names the call and prints got before want. The two `||` checks print all four operands. Table cases are named by condition.

## Item 6: what the writer says it verified

No red run on the base commit and no mutation verdict is stated for the pip-stub tests (including the −1 index case). No commit states that the kind jobs ran green after the migration, or that the "135/135" and "19 groups" figures still hold. The only stated observations are the Helm 4.3.1 and 3.22.1 `--logs` outputs, and the ownership-metadata error text.

## Item 7: siblings of the change

- **`test/parity/suite/pip_control.go:28-31`, caveat 3:** "Path matching is strictly literal … No wildcards / regex / templates." This is no longer true now that `*` exists.
- **`README.md:58`:** "CI builds both via `.github/docker-dev-config.json`". The file now lists five images.
- **`.github/docs-for-publication-task.md:77`:** "The two-entry array in this repository's `docker-dev-config.json`". Also five now.
- **`run-suite` uses `kubectl wait --for=create`**, which needs kubectl 1.31 or later. The prerequisites table in `docs/local-integration-tests.md` gives no version. With an older kubectl the `&&` chain skips the wait, `logs -f` fails, and the user sees no suite log at all, because Helm 4 prints none.
- The other siblings are covered: the `.PHONY` list, `.gitignore`/`.dockerignore`, the CI lint list, `docker-release.yaml`'s comment, and `go-build.yaml`, which already runs the pipstub tests.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| `-test.timeout 600s` caps the suite under the documented "raise both" recipe; at the defaults Helm's wait equals and outlasts nothing | Substantive | `Makefile:50-51`, `helm-templates/authz-test-stand/README.md:69-70`, `values.yaml:92-99` | Name all three limits, derive the Helm wait from the deadline plus a margin, or put `-test.timeout` in a value that moves with the deadline |
| No run shows a suite outlasting 15 minutes | Substantive | 5dcb6be | A run with a raised deadline, or drop the claim |
| `E2E_HELM_ARGS` with `--set TAG=…` breaks the test-stand install | Substantive | `Makefile:91`, `:156` | A setting of the test stand's own (for example `TEST_STAND_HELM_ARGS`), or document the shared keys |
| Docs say `e2e-harness` installs and waits for the suite Job | Substantive | `docs/local-integration-tests.md` (the `e2e-harness` row) | Drop "and the suite Job" from that row |
| Parity README describes user files and cases that don't exist | Substantive | `test/parity/README.md` ("Identity provider") | Say there are none yet, as the commit does |
| Restricted PSS is claimed with no enforcing run or render assertion | Substantive | 17b17fc; `test/scripts/test-chart-render.sh` | Label the kind namespace `pod-security.kubernetes.io/enforce=restricted`, or add test-stand render assertions |
| Routed path with empty responses and no default → 404 is untested; so are `*` via `/pip-stub/configure` and rule-over-default precedence | Substantive | `test/integration/pipstub/main_test.go:225` | Add those cases |
| User merge, `profile.jq`, and the duplicate check are never exercised | Substantive | `build/authz-agent-transfer/Dockerfile:36-46` | A fixture run (two user files, one duplicate), or defer the code until the first user file lands |
| New parity-realm clients and users and `parity-mt-b` are unclaimed and unused | Substantive | `test/k8s/parity/idp-seed/parity-realm.json`, `parity-mt-b-realm.json` | Claim them with the cases that use them, or move them to that change |
| Keycloak bump in the SVT compose file is unclaimed | Substantive | `test/svt/common/compose/docker-compose.yml:3` | A sentence that claims it, or a separate change |
| Dev-build entries in `docker-dev-config.json` are unclaimed | Substantive | `.github/docker-dev-config.json:13-27` | A sentence that claims them |
| Transfer-image install path and the Helm 3 `helm test` form are not run anywhere | Substantive | `helm-templates/authz-test-stand/README.md:39-67` | One run outside kind (and on Helm 3, if supported), or say it is untested |
| Docs subset recipe has not been run | Substantive | `docs/local-integration-tests.md` (subset bullet) | Run it once |
| `pip_control.go` caveat 3 ("no wildcards") and its `main.go:NN` line references are stale | Substantive | `test/parity/suite/pip_control.go:16-31` | Mention `*`, and refer to functions by name instead of line numbers |
| Stale image counts: "both" and "two-entry" | Substantive | `README.md:58`, `.github/docs-for-publication-task.md:77` | Update both counts |
| `kubectl wait --for=create` needs kubectl ≥ 1.31, but no version is stated | Substantive | `Makefile:111`, `docs/local-integration-tests.md` (prerequisites) | State the minimum version, or add a fallback |
| No red run or mutation evidence is stated | Substantive | all four commits | State the red run of the pip-stub cases on the base commit, and the kind results |
| "as it did before the default route existed" narrates the change | Taste | `test/integration/pipstub/main.go:38` | Drop the clause |
| `TAG` comment leaves out the runtime-suite image | Taste | `helm-templates/authz-test-stand/values.yaml:9-11` | Add it |
| `REALM-DESCRIPTION.md` issuer fix is unclaimed | Taste | `test/k8s/authn/REALM-DESCRIPTION.md:10` | One sentence in the commit message |

I did not check:
- The kind suites, `make test-stand-files` and `docker build` (no cluster; I did not use docker).
- What the Qubership base image's entrypoint writes under a read-only root filesystem.
- Helm 3 behavior.
- A style-only pass over the prose.

No files in the repository were changed.
