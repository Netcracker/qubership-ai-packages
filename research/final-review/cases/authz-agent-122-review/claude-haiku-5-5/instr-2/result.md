## Final review: `58316ca..HEAD` (three commits: `8b85515`, `9d25da7`, `17b17fc`)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages. No previous report exists, so there is no table of prior findings. The drift script ran with empty output, which is expected: it parses only Java, Kotlin, Groovy and Scala, and this change touches Go, Helm, Make, YAML and Markdown. Go comments were read by hand. The change has no skill or instruction file, so the §2a instruction table does not apply. Docs and chart README were read under the §2a analogues where the items point to them.

**Checks I ran (nothing in the repo was changed):**
- `GOWORK=off go test` in `test/integration/pipstub`: all tests pass, including the five new default-route cases, the sequence test and the request-target test.
- `helm lint` of the chart with both values files: clean. The default render produces zero objects.
- A copy of the chart with `files/` filled in by hand, under the scratchpad at `/private/tmp/claude-501/-private-var-folders-hq-dhvxggnd1gv0fpmt8lg8xzkc0000gn-T-tmp-tFUh7JOofH-repo/fc0f0543-a3c5-44d4-acb4-ba223275bca6/scratchpad/chk/authz-test-stand`. Every rendered object carries the labels, and every pod and container carries the security context that `17b17fc` claims.
- The documented subset command in `docs/local-integration-tests.md` (`helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…`): its render changes the Job env as described.
- `make -n e2e-suite parity-suite`: expanded recipes inspected.
- The user-merge and `profile` jq from the Dockerfile, run locally on a fixture user file: it fills `firstName`, `lastName` and `email` and keeps a declared `firstName`.

### Item 1: comments consistent with code and each other
Findings: F5 (values header contradicts the tenant-manager section), F6 (Makefile comment about `helm test` output). Checked and consistent: the pip-stub package comment and the `defaultRoute` and `RequestURI` comments; the chart helper and template comments; the parity README tenant claims (`mt-a`, `mt-b`, the `tenant-id` claim), verified against the realm JSON; the REALM-DESCRIPTION issuer, which matches `KC_HOSTNAME` with `/auth`.

### Item 2: claimed cases covered, and hunks claimed
Claimed cases and their tests:
- Default route for unrouted paths: `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, cases "an unrouted path gets the default answer" and "a routed path keeps its own answer".
- Empty routed path falls through to the default: "a routed path with no responses gets the default answer".
- No default route, or an empty one, gives 404: "an unrouted path without a default route is 404" and "…with an empty default route is 404".
- Sequence across paths: `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`.
- Request target as sent: `TestHandlePIP_RecordsTheRequestTargetAsSent`.
- Restricted Pod Security Standard, labels, no `runAsUser`: rendered and checked as above, but no run enforces the standard (F1).

Hunks no sentence claims (F2, F3). Commands the change tells someone to run: the chart README install-from-transfer-image path has no equivalent run in CI (F12). Makefile and CI commands match what the Makefile and CI run.

Comment-only follow-ups in `test/integration/testify/*` and `test/k8s/values.yaml` are consequences of the move the first commit describes. I did not count them as unclaimed hunks.

Commit messages state no red run and no mutation verdict for any test. Item 6 is answered in its own section.

### Item 3: boundaries, partitions and the negative control
- Pip-stub negative controls are present: no default route gives 404, and a routed path keeps its own answer.
- `E2E_HELM_ARGS` now reaches the test-stand chart. The keys the charts share are `TAG` and `IMAGE_PULL_POLICY`, and both mean the same thing to every consumer. None.
- Pre-existing state: F9.
- Replaced mechanisms: F7 (later failure on a missing image) and F8 (equal limits). Not verified without a cluster: the old `rollout status` output versus the new `helm --wait` output, which depends on the Helm version.

### Item 3a: level, placement, environment
The new pip-stub tests sit beside the existing ones, run in-process, and are in the `go-build` matrix. The chart claims have no in-process or render check: `test-chart-render.sh` renders only the agent and policy-admin charts (F1).

### Item 4: names by content
F-taste: `test-stand-values.yaml:21` says "A second instance for the entitlements endpoint." The content name is `entitlements-mock`. No other ordinals found in the new names or comments.

### Item 5: failure report
The new assertions print both operands, and the table cases are named by content. None.

### Item 6: what the writer says it verified
Not stated in any commit message: no red run on the base commit, no mutation verdict. The `-1` index regression in `9d25da7` would show red only as a panic on the base commit, and no run is recorded.

### Item 7: siblings
- `E2E_LOCAL_DEPLOYMENTS` and the parity list match the rendered Deployment names.
- `docker.cfg` and `docker-dev-config.json` name the same images.
- The CI lint list includes both new values files.
- Call-record consumers in `testify` and `parity/suite` decode `/pip-stub/calls` additively, so the new `requestUri` field breaks none of them.
- Stale count: F4.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| F1. `17b17fc` says the stand runs under the restricted Pod Security Standard, but nothing enforces it. The harness namespaces are created without a `pod-security.kubernetes.io/enforce` label, and no render assertion covers the security context. | substantive | `Makefile:86`, `Makefile:150`; `test/scripts/test-chart-render.sh` | Label both harness namespaces `restricted` and run on kind, or add a render assertion for the security context and labels to the render script. Otherwise drop "run … under the restricted Pod Security Standard" from the subject. |
| F2. Hunk with no claim: Keycloak in the SVT compose stack moves from 26.0 to 26.3.5 with a digest. No commit mentions it. | substantive | `test/svt/common/compose/docker-compose.yml:3` | Add a sentence and a run of the SVT stack, or move the bump to its own change. |
| F3. Hunks with no claim: dev CI now builds three more images, and CI adds a test-stand file generation step and two lint lines. | substantive | `.github/docker-dev-config.json:12-23`; `.github/workflows/integration-tests.yaml:76-85` | Add a sentence claiming them, or split them out. |
| F4. Stale count: the README still says CI builds "both" images, but `docker-dev-config.json` now lists five. | substantive | `README.md:57` | List the five images, or say "all five". |
| F5. Contradiction in one file: the header says the repo's images, including tenant-manager, carry "the release version". The tenant-manager section says the release does not publish its image. | substantive | `helm-templates/authz-test-stand/values.yaml:9-11` vs `:57-59` | State that tenant-manager carries the local `ci` tag, not the release version. |
| F6. The comment says `helm test` "prints the log only at the end". Without `--logs` it prints no log, and `run-suite` passes none. | substantive | `Makefile:95-96` | Reword: without `--logs`, `helm test` prints no log, so the log is streamed with `kubectl logs -f`. |
| F7. A replaced mechanism fails later with no accepting sentence. If the test image is never loaded, the old `wait … Ready --timeout=3m` failed after 3 min. The new loop expires after 3 min, then `wait $helm_pid` waits up to 15 min for `helm test` or the Job's 900 s deadline. Separately, if the release is missing, `helm test` exits at once, but `kubectl wait --for=create` still runs its full 2 min. | substantive | `Makefile:100-106` (for `run-suite`) | Run the missing-image fault on kind with duration and output (not run here: no cluster), and bound the pod-start wait at 3 min. Let the create wait return when `$helm_pid` exits. |
| F8. Equal limits: `helm test --timeout 15m` and the Job's `activeDeadlineSeconds: 900`. The outer limit can fire first, so the Job's own deadline may never be the reported reason. | substantive (low) | `Makefile:101`; `helm-templates/authz-test-stand/templates/suite.yaml:25`; `README.md` of the chart, step 3 | Raise the `helm test` timeout just past 900 s, or derive the Job's deadline from it. |
| F9. Pre-existing state. Objects from the earlier version lack Helm ownership: `keycloak` Deployment and Service, `keycloak-realms`, `authz-agent-client-credentials`, and in the parity namespace `idp`, `pip-mock`, and others. `e2e-cluster` reuses an existing cluster, so `make e2e-harness` on a stand the previous version built should fail on adoption. No remedy is written. | substantive | `Makefile:86`, `:150` | Run `make e2e-harness` over a stand from the previous version, or document the remedy (`make e2e-down` first, or delete the named objects). Expected refusal per Helm's ownership check; not run here. |
| F10. Untested claims in pip-stub. The 404 half of "a route with no responses falls through to the default route, or to 404" has no case. The precedence in the package comment (rules, then legacy routes, then the default route) has no case where a matching rule answers an unrouted path while `*` is configured. | substantive (low) | `test/integration/pipstub/main_test.go:233-240`; `test/integration/pipstub/main.go:29-31` | Add a case: an empty routed path with no default gives 404. Add a case: a rule answers an unrouted path while `*` is configured. |
| F11. The user-merge and `profile` path is claimed, but no input in the tree runs it. `testdata/realm/` holds only a README. | substantive (low) | `build/authz-agent-transfer/Dockerfile:32-47`; `build/authz-agent-transfer/profile.jq:1-10` | Add a fixture user file under a test, or a documented run. My local run of the same jq on a fixture passed. |
| F12. The chart README's install path (`docker create`, `docker cp`, `helm upgrade --install ./charts/…`, `helm test … --logs`) has no CI or Makefile equivalent. The transfer image is never installed in CI, and `run-suite` omits `--logs`. Outcome: none. | substantive | `helm-templates/authz-test-stand/README.md:39-65` (the `helm test` line is 64) | Run the install from the transfer image on kind, or mark the path as unverified in the README. |
| T1. "A second instance for the entitlements endpoint." | taste | `test/k8s/test-stand-values.yaml:21` | Name it by content: "The entitlements endpoint instance." |

### Not checked
I did not run the suites, a kind cluster, `docker build`, or `make test-stand-files`, and I did not check the Keycloak image's writable paths or its non-root user offline. The Helm version's `--wait` output is unverified. The English style pass was not done; I read wording only where it changes what a sentence says.
