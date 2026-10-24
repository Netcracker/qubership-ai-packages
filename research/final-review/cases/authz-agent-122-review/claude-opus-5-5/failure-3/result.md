# Final review: `58316ca..HEAD`

I was given no task statement, so the claimed cases come from the three commit messages (8b85515, 9d25da7, 17b17fc), the test comments, and the docs the change edits. There is no previous report. I loaded `test-authoring` (with `references/go/testing.md`) and `english-developer-style`. `comment-drift.py` ran and printed nothing, because it parses only JVM files and this change is Go, Helm, Make, Dockerfile, YAML and Markdown. I read every changed comment by hand instead.

Commands I ran: `go test ./...` in `test/integration/pipstub` (passes). I rebuilt the `files/` directory without Docker, using the same `cp` and `jq` steps as the `chart-files` stage, into a scratch copy of the chart. On that copy I ran `helm lint` and `helm template` with both stand values files on Helm v4.3.0. Both lint clean and render 12 and 10 objects. Every rendered Pod has `runAsNonRoot` and `RuntimeDefault`, and every container drops ALL capabilities and sets `allowPrivilegeEscalation: false`.

The repository's instructions have no test-stack line. I propose one: `Tests: Go testing (standard library), no assertion library; Helm charts by test/scripts/test-chart-render.sh`.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:122` (`defaultRoute`) and the package comment at lines 33–34** both say the default route answers "every request whose path has no route of its own". The code at `main.go:236` also sends a request to the default route when its path's route has **no responses**. The commit message and `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` both say so; neither comment does. A reader would expect a routed path with an empty `responses` list to get 404.
- **`main.go:37–38`** says "as it did before the default route existed", and line 32 keeps "exactly as before". Both describe the change rather than the code.
- **`docs/local-integration-tests.md:104`**: the `e2e-harness` row says the chart installs "the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` (`templates/suite.yaml:16`), so install does not create it. `test/k8s/README.md` says the opposite ("installing the stand does not start it"), and so does that README's own `e2e-harness` row.
- **`test/parity/README.md:69–72`** says the parity realm "also holds the users of `suite/testdata/realm/`" and that "their files declare none". The commit says there are "none so far", and the directory holds only `README.md`. A reader goes looking for user files and finds none.
- **`README.md:59`** still says "CI builds both via `.github/docker-dev-config.json`", but that file now lists five images. Details under item 7.
- Read and found consistent:
  - `callRecord.RequestURI`
  - the step-2 comment in `handlePIP`
  - all four `_helpers.tpl` comments, the `suite.yaml` hook comment, and the Keycloak env and probe comments in `idp.yaml`
  - `values.yaml`
  - the Makefile comments for `run-suite`, `e2e-harness`, `e2e-restart` and `E2E_HELM_ARGS`
  - the comment blocks of the transfer Dockerfile and `profile.jq`
  - the `testify/Dockerfile` and `helpers.go` `LoadConfig` comments
  - the comment in `test/k8s/values.yaml`
  - the issuer fix in `REALM-DESCRIPTION.md` (the old `keycloak.yaml` already set `KC_HOSTNAME=…/auth`, so the fix is true)
- On "No request path is `*`": `net/http` answers `OPTIONS *` before any handler runs, so the claim is true.

## Item 2: claimed cases covered

| Claimed case | Covered by |
| --- | --- |
| An unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| …or to 404 (the old index of −1) | `…/an_unrouted_path_with_an_empty_default_route_is_404` reaches the second guard. A mutant that drops the first guard fails the row with no responses. |
| A stub nobody configures with `*` answers 404 | `…/an_unrouted_path_without_a_default_route_is_404` |
| The default route serves its responses in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `/pip-stub/configure` takes the path `*` | **Not through configure.** Every test writes `routes[defaultRoute]` directly. `handleConfigure` did not change and stores any path, so this is taste. |
| The call record keeps the request target "in `requestUri`" | `TestHandlePIP_RecordsTheRequestTargetAsSent` checks the Go field only. **No test reads the JSON from `/pip-stub/calls`**, so renaming the tag `requestUri`, the key consumers read, stays green. |
| Rules take precedence over the default route (package comment) | **None.** See item 3. |
| Chart parts, each off by default | Rendering with default values was not asserted anywhere. I rendered only the two stand values files. |
| Keycloak re-imports realms and restarts when a realm file changes | The `checksum/realms` annotation exists. No test changes a file and compares the renders. |
| `make e2e-*` and `make parity-*` install the chart and run `helm test` | CI jobs `kind-e2e` and `kind-parity` (`integration-tests.yaml:117–208`) |
| `test-stand-files` merges the users and fills in the profile fields | **None.** `testdata/realm/` holds no `*.json`, so `profile.jq` and both duplicate checks run on empty input in every build. Nothing feeds them a user, or a username declared twice. |
| Release publishes pip-stub, parity-suite and the transfer image | `.qubership/docker.cfg` and `.github/docker-dev-config.json` entries. No run is stated. |
| The stand starts under the restricted Pod Security Standard | **None.** The kind namespaces carry no `pod-security.kubernetes.io/enforce` label, and `test-chart-render.sh` does not render this chart. The rendered fields look right (I checked them), but no gate keeps them. |
| `app.kubernetes.io/*` and `helm.sh/chart` labels on every object; selectors keep `app` | Confirmed on both renders. Nothing asserts it. |

Commands the change documents:

| Command | Outcome promised | What runs it |
| --- | --- | --- |
| `make test-stand-files` | generates `files/` | CI `chart` job |
| `helm lint … -f test/k8s{,/parity}/test-stand-values.yaml` | lint passes | CI `chart` job |
| `make e2e-harness`, `e2e-suite`, `parity-harness`, `parity-suite` | stand up, run and stream | CI kind jobs, **on a fresh cluster only** (item 3) |
| `docker build -t authz-agent-transfer -f build/authz-agent-transfer/Dockerfile .` | builds the image | the dev-config build, presumably |
| Chart README: `docker create` / `docker cp` / `docker rm` out of the transfer image, `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml`, `helm test authz-test-stand --timeout 15m --logs` | install from the image and run the suite | **none** |
| Docs: `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string suite.env.FULL_RUNTIME_SUITE=false` | runs a subset of the suite | **none** |

For the two `none` rows:

- The transfer flow depends on a released image tag existing for pip-stub and the parity suite, and on the published charts' `files/`. Nothing has run it.
- The subset recipe relies on `--reuse-values` merging the new `--set` keys over the stored `suite.env`. Helm 3 and Helm 4 both do that, but `make e2e-suite` then reruns with whatever is stored, and nothing has run the recipe.
- The request is one run of each, or a note in the docs that they are unverified.

Hunks that no commit sentence claims:

- **`test/svt/common/compose/docker-compose.yml:3`**: the SVT Keycloak image moves from `26.0` to `26.3.5@sha256:…`. It is in commit 8b85515, which says nothing about SVT.
- **`test/k8s/parity/idp-seed/parity-realm.json`** (+318 lines) adds:
  - clients `parity-m2m-tenant-{a,b,empty,unknown}` and `parity-end-user-tenant-a`
  - users `mt-a`, `mt-a-admin`, `parity-r29-scope` and `parity-r30-scope`
  - the department, level, tier, tenant-id and audience mappers

  The commit claims only "a second tenant realm, parity-mt-b", which is a separate file. Nothing in `test/parity/suite` uses the new clients, users or mappers yet.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub partitions:** no default route, an empty default, a non-empty default, a routed path with responses and one without; sequence clamping on the default route. The missing control is **a rule and the default route together**: the package comment promises rules come first. A mutant that checks the default route before the rule engine passes every new test, because none of them sets `rules`. For `requestUri`, the only case is a path with encoded characters. There is no plain-path control showing the two fields agree when nothing is encoded (taste).
- **State an earlier version left behind:** the harnesses used to `kubectl apply` objects whose names the chart now creates:
  - e2e namespace: Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`; ConfigMap `keycloak-realms`; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`
  - parity namespace: `idp`, `pip-mock`, `entitlements-mock`, ConfigMap `pip-mock-config`, and the same Secret

  `helm upgrade --install` refuses objects it does not own ("invalid ownership metadata"). So `make e2e-harness` on a kind cluster an older checkout set up fails. CI always starts from a fresh cluster, and no doc names the remedy (`make e2e-down`, or deleting the namespace). The label change in 17b17fc leaves selectors alone, so upgrading a release from 8b85515 is fine.
- **A setting that now reaches another consumer:** `E2E_HELM_ARGS` now also reaches the stand. Its only documented value, `--set IMAGE_PULL_POLICY=Never`, is what the stand already uses, and Keycloak has its own `idp.imagePullPolicy`. CI passes nothing. No finding.
- **A replaced mechanism: missing local image** (the usual fault, from skipping `e2e-images` or `kind load`). Durations are read from the Makefile and manifests; nothing was run:
  - *Harness:* the old harness failed after 2 m at `rollout status deploy/pip-stub --timeout=2m`. The new one fails after 10 m at `helm … --wait --timeout 10m`.
  - *Suite:* the old suite failed after 3 m at `wait --for=condition=Ready pod … --timeout=3m`, printing `timed out waiting for the condition`. The new one runs `wait --for=create` (fast), then up to 90 × (one `kubectl logs` call + 2 s) ≈ 3 m of silent polling. `logs -f` then prints the waiting reason. After that, `wait $helm_pid` sits until `helm test --timeout 15m` or `activeDeadlineSeconds: 900` ends it: **about 15 m against 3 m**, and nothing in the change accepts that.
- **Limits on the suite's run time:**
  - `-test.timeout 600s`, set in the values `suite.args`
  - `suite.activeDeadlineSeconds: 900`, a documented value
  - `helm test --timeout 15m`, fixed in the Makefile's `run-suite` and repeated in the chart README

  The Job deadline and the helm timeout are equal, and helm starts its clock first, so helm fires first and its report hides the Job's `DeadlineExceeded`. Setting `activeDeadlineSeconds` above 900 has no effect under `make e2e-suite` or `make parity-suite`. At the defaults the innermost limit (`-test.timeout 600s`) fires first, which is correct.
- Other limits on the harness: Keycloak's startup probe (60 × 5 s = 5 m) fires before the harness's `--wait --timeout 10m`, so the inner report shows. No finding.

## Item 3a: level, placement, and the environment

- **pip-stub:** the tests are small, call the handler in process, sit in `main_test.go` beside the existing `TestHandlePIP_*` tests, and share `resetState`. The new `serve` helper does not copy an existing helper. No finding.
- **Chart security and labels:** these can be checked with `helm template`, no cluster needed. `test/scripts/test-chart-render.sh:792` already asserts seccomp and read-only root on `authz-agent` and `authz-policy-admin`. The test-stand chart is not in that loop, and `test/BASELINE.md:17` lists only the two charts. The commit's main claim is therefore checked by nothing. The request is to add the test-stand renders (both values files) to the security and label assertions. Labeling the kind namespaces `pod-security.kubernetes.io/enforce=restricted` would also make the CI kind jobs enforce it.
- `run-suite` uses `kubectl wait --for=create`, which needs kubectl 1.31 or later. The docs' prerequisite table (`docs/local-integration-tests.md:37`) gives no minimum version. On an older kubectl the `&&` skips the log loop and the log is not streamed (I have kubectl 1.33 here, so not reproduced). Taste: state the minimum.

## Item 4: names by content, not by position

- Every test name and subtest case is named by content.
- `values.yaml:23` says "its own image and pull policy below", meaning `idp.image` and `idp.imagePullPolicy` (taste).
- `test/k8s/README.md:4` says "The Makefile targets below", which points at the section that follows (taste).

## Item 5: the failure report

- Every new assertion prints got and want, in Go's got-before-want order:
  - `GET %s = %d %s, want %d %s`
  - `statuses of /a, /b, /a = %v, want %v`
  - `requestUri %q, path %q, want %q and %q`
- The table rows are named by condition. `t.Fatalf` is used only before the `calls[0]` dereference.
- `TestHandlePIP_RecordsTheRequestTargetAsSent` puts two comparisons behind one `||`, but its message prints all four values. No finding.

## Item 6: what the writer says it verified

None of the three commits mentions a red run on the base commit or a mutation verdict. That includes the fix for the old index of −1, where a route with no responses panicked on `Responses[-1]`. No run of the restricted Pod Security Standard and no green kind run is cited either. The CI kind jobs are a consistency gate, not that evidence. I did not run the suite on the base commit.

## Item 7: siblings of the change

- **pip-stub:** `matchRule` (`main.go:275`) already guards an empty `respondSequence`. `handleReset` clears `counters`, the `*` key included. No other Go file indexes `counters[`.
- **Images added to `docker-dev-config.json` and `docker.cfg`:** the `docker-release.yaml` comment and the second paragraph of `README.md` were updated. `README.md:59`, "CI builds both", still counts two.
- **Chart added:**
  - The CI lint, the transfer image and the docs list it.
  - `test-chart-render.sh` and `test/BASELINE.md` list only the two product charts (item 3a).
  - `components/authz-policy-admin/README.md` and the policy-admin values are about that one image. Not siblings.
- **Makefile `test-stand-files`:** added to `.PHONY`. Both target tables mention it inside the `e2e-harness` row.
- **The other path with the same symptom:** `parity-harness` and `parity-suite` share the `run-suite` macro, so the timing and pre-existing-state findings above hold for both namespaces.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | `helm upgrade --install` on a kind cluster an older checkout set up meets objects it does not own (Deployments, ConfigMaps, Secret, ServiceAccount) and fails. No run starts from that state, and no remedy is documented | Substantive | `Makefile` `e2e-harness`, `parity-harness`; `docs/local-integration-tests.md` | Run the harness on a cluster the base commit set up, or document `make e2e-down` (or deleting the namespace) as the step after this change |
| 2 | With a missing local image the suite now fails after about 15 m instead of 3 m, and the harness after 10 m instead of 2 m. Nothing accepts the trade | Substantive | `Makefile` `run-suite`, `e2e-harness` | Run that fault and state both durations and outputs, or bound the wait (for example, stop when the log loop gives up) |
| 3 | `suite.activeDeadlineSeconds` (900) equals the fixed `helm test --timeout 15m`. Raising the value has no effect, and helm's timeout hides the Job's own report | Substantive | `values.yaml` `suite.activeDeadlineSeconds`; `Makefile` `run-suite`; chart `README.md` | Derive the helm timeout from the value, or document the pair and keep helm's limit above the Job's |
| 4 | Restricted Pod Security Standard and label claims are checked by nothing: no render assertion and no enforcing namespace | Substantive | `test/scripts/test-chart-render.sh:792`; `test/k8s/*-values.yaml` | Add the test-stand renders to the security and label assertions, or label the kind namespaces `enforce=restricted` |
| 5 | No test puts a rule beside the default route, so the documented precedence (rules first) can regress silently | Substantive | `test/integration/pipstub/main_test.go:225` | Add a case with a rule matching the path and a default route present, expecting the rule's answer |
| 6 | `requestUri` is asserted on the Go struct only, so the JSON key consumers read is not covered | Substantive | `main_test.go:276` | Read the record back through `handleCalls` and assert the `requestUri` key |
| 7 | `profile.jq` and the duplicate-user checks run only on empty input, so no claimed behavior of theirs is exercised | Substantive | `build/authz-agent-transfer/Dockerfile:39–46`, `profile.jq` | A fixture user file, or a jq check in CI, covering the `R29LevelM2M` derivation and a duplicate username |
| 8 | The `defaultRoute` and package comments omit that a route with no responses also falls through to the default route | Substantive | `main.go:33–34`, `main.go:122` | Add "or whose route has no responses" |
| 9 | The `e2e-harness` row says the suite Job is installed and waited for, but it is a test hook that install does not create | Substantive | `docs/local-integration-tests.md:104` | Drop "and the suite Job" from that row |
| 10 | The parity README says the realm holds the users of `testdata/realm/`, and none exist | Substantive | `test/parity/README.md:69–72` | Say the stage adds them when that directory holds user files, currently none |
| 11 | "CI builds both" now counts two of five images | Substantive | `README.md:59` | Name the two product images, or count the five |
| 12 | Hunks no sentence claims: the SVT Keycloak bump, and the parity-realm clients, users and mappers beyond `parity-mt-b` | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `test/k8s/parity/idp-seed/parity-realm.json` | A commit-message sentence for each, with the run that checks the SVT bump, or move them to their own change |
| 13 | Two documented commands are run by nothing: the transfer-image install with `helm test --logs`, and the `--reuse-values` subset recipe | Substantive | chart `README.md` steps 1–3; `docs/local-integration-tests.md:137` | One run of each, or a note in the docs that they are unverified |
| 14 | No red run on the base commit or mutation verdict is stated, including for the old index of −1 | Substantive | commit 9d25da7 | State the red run of `…/a_routed_path_with_no_responses_gets_the_default_answer` on `58316ca` |
| 15 | Comments describe the change ("as it did before the default route existed", "exactly as before") | Taste | `main.go:32`, `main.go:37–38` | State the 404 behavior without history |
| 16 | The configure-with-`*` claim is tested by writing `routes` directly, not through `/pip-stub/configure` | Taste | `main_test.go:249`, `main_test.go:263` | Register `*` through `handleConfigure` in one case |
| 17 | `kubectl wait --for=create` needs kubectl 1.31 or later, and the prerequisite table gives no minimum | Taste | `docs/local-integration-tests.md:37`; `Makefile` `run-suite` | State the minimum kubectl version |
| 18 | Positional references ("below") | Taste | `values.yaml:23`; `test/k8s/README.md:4` | Name the section or key instead |

The review did not run the kind harnesses or a cluster, the Docker build of the `chart-files` stage (I reproduced it with local `cp` and `jq`), the transfer-image flow, or the suite on the base commit. I made no pass over the prose for style alone.
