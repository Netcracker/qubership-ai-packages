# Final review of `58316ca..HEAD` (four commits)

**Task statement:** there was none. The claimed cases come from the four commit messages (`8b85515`, `9d25da7`, `17b17fc`, `5dcb6be`) and from the doc and test comments in the diff.

**Skills:**
- Loaded: `test-authoring` (Go `testing`; its Go reference files were not provided, so I applied §5 to §9 from the skill body) and `english-developer-style`.
- Not loaded: `docs-page-authoring` and `godoc-authoring`, which the skills mention but are not among the three provided.

**Drift script:** it ran and printed nothing for this range. The Go changes are in `pipstub/main.go` and `testify/helpers.go`, so I read those comments by hand.

**What I ran:**
- `go test` in `pipstub`: passes.
- `helm lint` and `helm template` on a scratch copy of the chart. I filled `files/` with copies of the realm and rule files, because `make test-stand-files` needs Docker.
- Both values files lint clean. A render with `--set TAG=1.2.3` showed the `TAG` problem in item 3.

**Not checked:**
- No cluster, so no `helm test`, `make` target or kubectl output was run.
- The local Helm is v4.3.0. The commit message cites Helm 4.3.1 and 3.22.1, so I could not check the README's statement about `helm test --logs` in either.

## Item 1: Comments consistent with the code and with each other

- **`docs/local-integration-tests.md:104` — Substantive.** The `e2e-harness` row says the target installs the chart including "the suite Job" and "waits until they are Ready". The Job is a `helm test` hook (`suite.yaml`), so installing the stand never starts it. `test/k8s/README.md` words the same row correctly. Remove the Job from the row.
- **`pipstub/main.go:37` — Taste.** "…answers an unrouted request 404, as it did before the default route existed" narrates the change in a package comment. "…answers 404" alone is complete.
- **`helm-templates/authz-test-stand/templates/pip-stub.yaml` — Taste.**
  - The ConfigMap with the rule file carries no checksum annotation, unlike `idp.yaml`.
  - A changed rule file therefore does not restart the stub, which reads it only at start.
  - `test/k8s/README.md` promises only that a changed realm file is picked up, so nothing false is written. A one-line note would help.
- Other comments checked and consistent:
  - the new header and `// 2.` comments in `main.go`
  - `testify/Dockerfile`
  - `helpers.go`
  - the `values.yaml` comments
  - the `REALM-DESCRIPTION.md` issuer fix (`/auth` was already in the old `keycloak.yaml`)
  - the chart README, apart from the finding in item 3

## Item 2: Claimed cases covered

| Claim | Test or evidence |
| --- | --- |
| Unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| Routed path keeps its own answer | `…/a routed path keeps its own answer` |
| A route with no responses falls to the default route | `…/a routed path with no responses gets the default answer` |
| A route with no responses falls "or to 404" | **No test.** The 404 rows cover an unrouted path with no or empty default, not a routed path with empty responses and no default. |
| No default route gives 404, as before | `…/an unrouted path without a default route is 404` |
| Empty default route gives 404 | `…/an unrouted path with an empty default route is 404` |
| Default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the raw target | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` "now takes the path `*`" | **No test.** Both tests seed `routes` directly, so no test goes through `handleConfigure`. |
| Pods non-root, seccomp, caps dropped, no escalation, read-only root except Keycloak, `/tmp` emptyDir, no `runAsUser`, labels, selectors keep `app:` | **No test.** I confirmed most of them in a manual render. CI runs only `helm lint`, and `test/scripts/test-chart-render.sh` has no case for the new chart. |
| Realm merge, profile fields, duplicate user check | Only the `jq -e` guards in the Dockerfile. There are no user files yet, so the merge and `profile.jq` never run on a user. |
| `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` set the wait | No test. Defaults are 15m, equal to `activeDeadlineSeconds: 900`. |

**Command lines the change tells someone to run:**

| Command | What runs it |
| --- | --- |
| `make e2e-harness`, `e2e-suite`, `parity-harness`, `parity-suite` | CI jobs run these targets. The new `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` values are CI's defaults. |
| `helm lint helm-templates/authz-test-stand -f …` | `integration-tests.yaml:83-84`, same flags. |
| `helm test authz-test-stand --timeout 15m`, then `kubectl logs job/parity-suite` (chart README step 3) | `none`. The Makefile uses a different form, with a background `helm test` and a poll loop. The README's claim about `--logs` rests on Helm's behavior for Job hooks, which I could not verify here. The local help says only "dump the logs from test pods". |
| `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string suite.env.FULL_RUNTIME_SUITE=false` (`docs/local-integration-tests.md`) | `none`. It depends on `files/` existing and on the release already being installed. |
| `make e2e-down`, then `make e2e` (the "exists and cannot be imported" row) | `none`. See item 3. |

- **Hunks beyond the claims:** none that I found. `.dockerignore`, `.gitignore`, the CI lint step, the docker configs and the `docker-compose.yml` hunk are all covered by the commit messages. I saw only the `docker-compose.yml` diffstat line and did not read that hunk.
- **Substantive findings from this item:**
  - the missing "routed, empty responses, no default route → 404" row
  - the missing test through `handleConfigure`
  - the missing render assertions for the security-context claim (also item 3a)
- **Observation:** the new default route and `requestUri` have no consumer in this change. The commit says the stub instance "comes with the cases that use it". That is acceptable, but the feature is untested end to end.

## Item 3: Boundaries, partitions, negative control

**Pass-through setting — Substantive. `Makefile:46-48`.**
- `E2E_HELM_ARGS` now reaches the test-stand install as well. The comment says "every chart install, the test stand's included".
- The stand chart defines `TAG` and `IMAGE_PULL_POLICY`, the same names the agent and policy-admin charts define.
- The documented example, `--set IMAGE_PULL_POLICY=Never`, means the same to every consumer.
- `--set TAG=<agent tag>` does not. I rendered `--set TAG=1.2.3`: the stand then wants `local/pip-stub:1.2.3`, `local/tenant-manager:1.2.3` and `local/authz-runtime-suite:1.2.3`, none of which `e2e-images` builds. Pods fail with `ErrImageNeverPull`.
- Request: give the stand its own tag key, or run the stand install with a value of `TAG` it controls, and render once with `--set TAG=…`.

**Limit fixed elsewhere — Substantive. `values.yaml` (`suite.args`, `suite.activeDeadlineSeconds`), `Makefile:51-52`, `5dcb6be`.**
- The commit's goal is a suite that outlasts 15 minutes.
- The default and the e2e values pass `-test.timeout 600s`, so Go kills the run at 10 minutes.
- Raising `suite.activeDeadlineSeconds` to 1800, and the suite timeout with it, changes nothing, because the inner limit fires first.
- At the defaults, the inner limit (600s) does fire before the deadline (900s) and the Helm wait (15m).
- Request: derive `-test.timeout` from `activeDeadlineSeconds` in the template. Otherwise make the Makefile and README comments say that `-test.timeout` must be raised too. Add a case just past 600s.

**Replaced mechanism — Substantive. `Makefile` `run-suite`.**
- *Old:* the Job's Pod had to be Ready within 3 minutes (`kubectl wait --for=condition=Ready pod --timeout=3m`), then Complete within 1 minute.
- The failure the troubleshooting table lists most often is `ErrImageNeverPull` or a Pending Pod.
- Old time to fail: about 3 minutes, with kubectl's timeout error.
- *New:* `helm test --timeout 15m` waits on the Job.
  - A Pod that never starts never fails the Job, so Helm waits out its timeout. The Job's own `activeDeadlineSeconds` (900s) ends at the same moment.
  - The poll loop (90 × 2s, plus the 2m `wait --for=create`) prints nothing helpful in the meantime.
  - New time to fail: about 15 minutes, and the output comes from Helm, not from the old pod-wait message.
- No sentence in the change accepts this.
- Request: run this fault on the new mechanism. Bound the whole wait at the old 3 minutes until the Pod is Ready, for example by adding the old Ready wait before streaming. Otherwise state the 15 minutes as accepted.

**Inherited state — Substantive. `test/k8s/README.md`, `docs/local-integration-tests.md`.**
- The change replaces `kubectl apply` objects with Helm-owned ones. Same-named objects such as `keycloak-realms`, `authz-agent-client-credentials` and the `runtime-suite` ServiceAccount exist after an old `make e2e`.
- The error text and the remedy (`make e2e-down` once) are documented in both places. Every test and run in the change starts fresh, so the remedy was not run on an old cluster.
- Request: run it on a cluster set up by the base commit and state the result.
- Two smaller questions for that run:
  - `make e2e-down` deletes the whole kind cluster, which also takes the parity namespace.
  - The old `runtime-suite` Job has no hook annotation.

**Boundaries in the Go tests:** the empty-responses row and the unrouted/empty-default row are both present. The missing "routed + empty + no default" combination is the one gap, listed in item 2. The empty `*` path value is not a partition anyone can send, since no request path is `*`.

## Item 3a: Level, placement, and the environment

- The default route and `requestUri` are tested in-process in `pipstub/main_test.go`, beside the existing tests. They reuse `resetState`, and `serve` is a new helper with no sibling. Good.
- **Substantive:** the security-context, label and selector claims are observable under `helm template` with no cluster. The only checks are `helm lint` and the CI job `Render assertions` (`test-chart-render.sh`), which does not cover the new chart.
- Request: add render assertions for the test-stand chart to that script.
- The CI lint step generates `files/` first, so the chart can render in CI.

## Item 4: Names by content, not by position

None. The Go cases are named by content (`an unrouted path gets the default answer`). I found no ordinals in the new comments or README text.

## Item 5: The failure report

None.
- The Go assertions print both operands, with the path or request target in the message.
- The table cases carry content names, not indices.
- `len(calls) != 1` has its own `Fatalf` with the count.

## Item 6: What the writer says it verified

- None of the four commit messages states a red run on the base commit, a mutation result or a render check.
- For the `pipstub` tests, the 404 and `requestUri` cases cannot go red on the base: before the change the unrouted-path case also gave 404, and `RequestURI` did not exist.
- I did not run the suite to supply this evidence.

## Item 7: Siblings of the change

- **Sets that gained a member.**
  - The release image list grew from 2 to 5.
  - I searched for "two images", "both" and similar, and checked the places that list the images: `README.md`, `docker-release.yaml`, `.qubership/docker.cfg`, `docker-dev-config.json`.
  - `README.md:60` still says "CI builds both via `.github/docker-dev-config.json`", but that sentence names only the two services and sits beside the paragraph that now lists the five. Taste, no request.
  - `.agents` and `.claude` carry the phrase "two images" in a generic example. It is unrelated.
- **Deleted files.** I searched for references to the removed manifests (`runtime-suite-job.yaml`, `keycloak.yaml`, `m2m-credentials`, `E2E_AUTHN` and the like). None remain outside `docs/handovers`, which is historical.
- **`/pip-stub/configure` callers.**
  - Callers are in `test/integration/testify` (`check_resource_test.go`, `entitlements_test.go`, `pip_admin_test.go`) and `test/parity/suite/pip_control.go`.
  - None sends `*`, and routed paths are unchanged.
  - A routed path with an empty `responses` list used to index `-1`. It now falls to the default route or 404, so no caller depends on the old behavior.
- **Symptom paths.** The "exists and cannot be imported" remedy names `e2e-down`, which covers both namespaces. The troubleshooting row names `make e2e-harness` and `make parity-harness`, and the action covers both.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| `e2e-harness` row says the target installs and waits on the suite Job, which `helm test` runs | Substantive | `docs/local-integration-tests.md:104` | 1 |
| Package comment narrates "as it did before the default route existed" | Taste | `test/integration/pipstub/main.go:37` | 1 |
| A changed pip-stub rule file does not restart the stub (no checksum annotation) | Taste | `helm-templates/authz-test-stand/templates/pip-stub.yaml` | 1 |
| No case for a routed path with empty responses and no default route → 404 | Substantive | `test/integration/pipstub/main_test.go` | 2 |
| `/pip-stub/configure` with `*` is claimed but no test goes through `handleConfigure` | Substantive | `test/integration/pipstub/main_test.go` | 2 |
| Security-context, label and selector claims have no render assertion | Substantive | `test/scripts/test-chart-render.sh` | 2, 3a |
| Subset command in the docs runs under no target | Taste | `docs/local-integration-tests.md` (subset bullet) | 2 |
| `E2E_HELM_ARGS` `--set TAG=…` now changes every stand image to a tag nothing builds | Substantive | `Makefile:46-48` | 3 |
| `-test.timeout 600s` fires before a raised `activeDeadlineSeconds` | Substantive | `values.yaml` (`suite.args`), `Makefile:51-52` | 3 |
| Image-pull or Pending fault now fails after about 15 minutes instead of 3, with no stated acceptance | Substantive | `Makefile` `run-suite` | 3 |
| The "exists and cannot be imported" remedy was never run on an old cluster | Substantive | `test/k8s/README.md`, `docs/local-integration-tests.md` | 3 |
| No red-run, mutation or render evidence in any commit message | Substantive | commit messages | 6 |

No check the form asks for was skipped, other than the ones listed under "Not checked" at the top (running the make targets and `helm test`).
