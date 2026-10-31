**Final review: `58316ca..HEAD` (four commits, 48 files)**

**Scope.** No task statement was handed over, so the claimed cases come from the four commit messages, the Go test comments, and the claims the chart, Makefile, and docs make. There is no previous report. The drift script printed nothing: it parses only `.java`, `.kt`, `.kts`, `.groovy`, and `.scala`, and this change touches none of them. I read the Go, Make, Helm, and Markdown comments by hand. `godoc-authoring` was not among the three copies named, so I did not load it and did not apply the Go doc-comment rules. I did not change any file or commit.

**What I ran.** Scratch copies are under `/private/tmp/claude-501/-private-var-folders-hq-dhvxggnd1gv0fpmt8lg8xzkc0000gn-T-tmp-5IYdESPcNj-repo/237c42de-efa5-49e7-abac-b3e05b2a4b35/scratchpad/`.
- `go test -count=1 -v ./...` in `test/integration/pipstub`: all pass, including the five default-route subtests.
- `helm lint` on both stand value files, on a copy of the chart with the generated `files/` staged by hand (no docker): 0 failed. `helm template` renders 12 objects (e2e) and 10 (parity). Every container has `allowPrivilegeEscalation: false`, `drop: ALL`, and `RuntimeDefault` seccomp; `readOnlyRootFilesystem` is true except on Keycloak; every object carries the helm labels.
- `make -n` on `e2e-suite`, `parity-suite`, and `e2e-harness` expands as the commits describe.
- The `profile.jq` merge and the uniqueness check, on sample users.
- Go's `net/http` on an `OPTIONS *` request: `URL.Path` is `*`.

**Not checked.** No cluster, so nothing was deployed or run end to end. Helm version behaviour in the README (Helm 4.3.1 and 3.22.1), the Keycloak digest, and the red-run evidence were not verified. The wording pass beyond the items was not done.

## Item 1: comments consistent with code and each other
Findings F1–F4. The drift script is empty and no added comment narrates the change.

## Item 2: claimed cases covered
- Test coverage: F5 (missing case), F7 (chart claims with no test), F8 (tenant B realm no case reads).
- Commands the change tells someone to run:
  - Makefile targets and `helm lint` lines match CI (`integration-tests.yaml:77–84`).
  - The chart README's `helm test --timeout 15m` plus `kubectl logs` matches `make parity-suite`'s `run-suite` except for the context and namespace flags.
  - The transfer-image `docker create/cp/rm` (F9) and the subset `helm upgrade --reuse-values` (F10) have no CI counterpart and were not run.
- Hunks no sentence claims: F11–F14.

## Item 3: boundaries, partitions, negative control
F15–F21. Three of these are limits and timing questions, F15–F19.

## Item 3a: level and placement
The pip-stub tests are in-process via `httptest`, beside the existing tests, sharing `resetState`: none. The stand's behaviour has no test at any level, which is F7.

## Item 4: names by content
Taste only: F23.

## Item 5: failure report
None. The Go assertions print their operands, and case names are by content.

## Item 6: what the writer says it verified
F6. No red run on the base commit and no mutation verdict is stated for the `-1` index fix.

## Item 7: siblings
F22 (override list) and F24 (hard-coded `15m`). Checked and clean: no references to deleted paths remain, every container uses the security helper, every object uses the labels helper, and the ownership troubleshooting row names both targets and one action that covers both namespaces.

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | Package comment says no request path is `*`. `OPTIONS *` arrives with `URL.Path` `*`. Harmless, since the default answers it too. | Substantive | `test/integration/pipstub/main.go:36` | Reword: the `*` path is reached by `OPTIONS *`, and the default route answers it. |
| F2 | Default-route comments say it answers paths with "no route of its own". Code and test also answer a route with no responses. | Substantive | `main.go:35`, `main.go:123` | Say "no route, or a route with no responses". |
| F3 | Comment says `helm test` "prints the log only at the end". The chart README says `helm test` prints no Job log. | Substantive | `Makefile:100` | Say `helm test` does not print a Job's log, which is why the loop streams it. |
| F4 | Says the e2e stand runs Keycloak with two realms. It imports four. | Substantive | `test/k8s/authn/REALM-DESCRIPTION.md:82` | List the four realm files. |
| F5 | Commit 9d25da7 claims a zero-response route with no default gives 404. No case covers it. | Substantive | `test/integration/pipstub/main_test.go:225` (case table) | Add the case: `routed` with empty responses, `defaultResponses` nil, expect 404. |
| F6 | No red run or mutation verdict is stated for the `-1` index fix. Base code panics on it. | Substantive | commit 9d25da7 | State the red run on `58316ca` for the zero-response case, or the mutation verdict. |
| F7 | Restricted PSS, read-only root, labels, checksum restart, hook annotation, and missing-file failures are claimed with no test. CI only lints the stand. | Substantive | `helm-templates/authz-test-stand/templates/*`; `.github/workflows/integration-tests.yaml:79–84`; `test/scripts/test-chart-render.sh` | Add `helm template` assertions for these properties, as the script does for the agent charts. Label the stand's namespaces restricted in the harness targets, or in a CI step. |
| F8 | "Gives the stand two tenants": nothing reads realm `parity-mt-b`. Only the Dockerfile, the realm file, and the README mention it. | Substantive | `test/k8s/parity/idp-seed/parity-mt-b-realm.json`; `test/k8s/parity/idp-seed/README.md:8–12` | Add a parity case that reads tenant B, or word the README as preparation. |
| F9 | Transfer-image `docker create` / `docker cp` / `docker rm` has no CI counterpart and was not run. The image is `FROM scratch`. | Substantive | `helm-templates/authz-test-stand/README.md:39–45` | Run the three commands on the published image, or add them to a CI job. |
| F10 | The subset command (`helm upgrade --reuse-values --set …`) has no CI counterpart and no run. | Substantive | `docs/local-integration-tests.md`, "A subset" bullet | Run it once on a cluster and record the result. |
| F11 | Keycloak 26.0 → 26.3.5 digest bump with no sentence in any message. | Substantive | `test/svt/common/compose/docker-compose.yml:3` | Move it to its own change, or claim it with a run. |
| F12 | CI now runs `make test-stand-files` and lints the stand. No message says so. | Substantive | `.github/workflows/integration-tests.yaml:74–84` | Claim it in a sentence, or move it. |
| F13 | Adds three components to the dev build config. Not claimed. | Substantive | `.github/docker-dev-config.json` | Claim it in a sentence, or move it. |
| F14 | Drops `-Dkeycloak.migration.strategy=OVERWRITE_EXISTING` with no sentence. Safe only because the H2 database is fresh at each container start. | Substantive (low) | deleted `test/k8s/keycloak.yaml:38–39` (base commit) | Name the removal and the reason in the commit message. |
| F15 | Replacement fails later. Old: about 3 min (`wait … --timeout=3m`). New, on a suite Pod that never starts (the docs' `ErrImageNeverPull` row): the loop takes about 3 min, then the wait ends at the Job's 900 s `activeDeadlineSeconds`, about 15 min. Not run. No sentence accepts it. | Substantive | `Makefile:105–111` | Run that fault and report duration and output, or bound the whole wait at 3 min, or accept the slower failure in the description. |
| F16 | `kubectl logs` in the loop and `logs -f` have no request timeout. By the rule, a call with no timeout never returns, so the loop's 3-minute bound is not a bound. | Substantive | `Makefile:105–111` | `--request-timeout` on each call, or one deadline over the whole wait. |
| F17 | CI's 30-minute job timeout encloses cluster creation, image build, harness (up to 10 min), install (up to 10 min), and suite (15 min). Worst case exceeds 30. A suite raised past 15 min cannot finish inside the job. | Substantive | `.github/workflows/integration-tests.yaml:120`, `:168` | Derive `E2E_SUITE_TIMEOUT` from the remaining job budget, or raise the job timeouts and state the budget. |
| F18 | Helm's wait equals the Job deadline at defaults (15m = 900 s), with zero margin. Helm's clock and the Job's clock start within moments of each other, so which fires first is a race. This is the symptom the commit describes. | Substantive | `Makefile:51–52`; `helm-templates/authz-test-stand/values.yaml:99`; `helm-templates/authz-test-stand/README.md:69` | Default above 900 s, e.g. 16m. Change "no shorter than" and "at least as long as" to "longer than". |
| F19 | `-test.timeout 600s` in `suite.args` is a limit inside the Job. Raising the deadline and the helm timeout alone leaves a suite past 600 s stopped by the test binary. The Makefile comment and the README name only the two. | Substantive | `helm-templates/authz-test-stand/values.yaml:95–96`; `test/k8s/test-stand-values.yaml:55`; `Makefile:49–50` | Derive `-test.timeout` from `activeDeadlineSeconds`, or name all three in the comment. |
| F20 | Inherited state is never tested. CI always starts from a fresh kind cluster. The documented remedy (`make e2e-down`) is not run on a cluster the old `make e2e` set up. | Substantive | `Makefile` (`e2e-harness`, `parity-harness`); `docs/local-integration-tests.md` troubleshooting row | Run `make e2e-harness` on a cluster built from `58316ca`, show the ownership error, run `make e2e-down`, and rerun. Not run here. |
| F21 | `E2E_HELM_ARGS` now reaches the stand, which reads `TAG` and `IMAGE_PULL_POLICY`, as the agent chart does. `--set TAG=x`, meant for the agent, makes the stand ask for `local/pip-stub:x` and others, none built. The `--wait` fails after 10 min. | Substantive | `Makefile:90`, `:155`; `helm-templates/authz-agent/values.yaml:5`, `:88` | Pass `E2E_HELM_ARGS` to the two product installs only, or give the stand its own variable. Or run once with `TAG` set. |
| F22 | `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` are missing from the override list. | Substantive | `test/k8s/README.md:66–69` | Add both names. |
| F23 | "A second instance" / "a second stub instance" names the entitlements stub by position. | Taste | `test/k8s/test-stand-values.yaml:21`; `docs/local-integration-tests.md:18` | Name it `entitlements-mock`. Taste, so expect it declined. |
| F24 | README hard-codes `--timeout 15m` while the Makefile reads `E2E_SUITE_TIMEOUT`. | Taste | `helm-templates/authz-test-stand/README.md:65` | Say the Makefile default, or derive it. Taste, so expect it declined. |

**Not checked:** the suite and the chart-files Docker stage were not run, and no cluster was used. The Helm version behaviour in the README, the Keycloak digest, the red run for F6, and the Go doc-comment rules were not verified or applied.
