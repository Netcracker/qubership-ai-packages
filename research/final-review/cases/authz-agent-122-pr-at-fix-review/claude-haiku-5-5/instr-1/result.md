# Final review: `58316ca..HEAD` (four commits)

**Scope.** No task statement was handed over, so the claimed cases come from the four commit messages. There is no previous report, so §4 has no table. Loaded: `final-review`, `test-authoring`, `english-developer-style`. `godoc-authoring` is not in the skills directory, so Go doc comments were checked by hand against ordinary Go convention. The drift script printed nothing because it parses only Java, Kotlin, Groovy, and Scala, and this change's code is Go. Go members were reviewed by hand.

**What I ran.** `go test` in `test/integration/pipstub` passed. `helm lint` (both value files) and `helm template` passed on a scratch copy with the generated `files/` filled in. The Dockerfile's jq profile stage was run on a scratch copy and produces the names its comment gives. `make -n e2e-suite` expands as intended. The repository is unchanged (`git status` is clean).

**Findings.** Substantive findings come first, then taste. There were no churn findings to report.

## Item 1: comments consistent with code and each other

Findings are in the table below (rows 9, 10, 11, 12, 13). I checked the pipstub header and tests, the chart and values comments, the Makefile comments, and the `profile.jq` comment (verified). Nothing else contradicts the code.

## Item 2: claimed cases covered

- **Default route answers unrouted paths.** Covered by `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` (cases 1–5) and `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`.
- **Routed path with no responses falls through.** Covered by case 3 of the first test. The "or to 404" half of the claim has no test (row 8).
- **Request target kept as sent.** Covered by `TestHandlePIP_RecordsTheRequestTargetAsSent`.
- **`/pip-stub/configure` takes `*`.** No test. The table sets `routes` directly and never calls `handleConfigure` (row 8).
- **Security contexts, labels, restricted Pod Security Standard.** No test, render assertion, or namespace label. The title's "run ... under the restricted Pod Security Standard" has no evidence (row 6).
- **Commands the change tells someone to run.** Every `make` target in the docs and CI runs the same flags, except the chart README's `helm test`, which the Makefile's `run-suite` (`Makefile:107`) covers. Two documented forms have no running counterpart (row 5).
- **Hunks no sentence claims.** Four hunks have no claim (row 7).

## Item 3: boundaries, partitions, negative control, limits, pre-existing state

- **Limits.** The `-test.timeout 600s` in `suite.args` fires before the 900 s deadline and before any raised `E2E_SUITE_TIMEOUT` (row 1). At defaults the helm wait and the Job deadline are equal, and the CI job's `timeout-minutes: 30` encloses the whole run (row 3).
- **Replaced mechanism.** The image-pull fault fails about 3 minutes in the old code and about 15 minutes in the new, with different output. Nothing in the change accepts that (row 2).
- **Pre-existing state.** The ownership-metadata remedy is documented but not run on an inherited cluster (row 4).
- **Negative control.** Pipstub has the control (a routed path keeps its answer, and a route with responses is not shadowed). The parity observed-sidecar writes fail silently on the read-only root filesystem. That predates this change, because `testdata/` was already root-owned, so it is not a regression.

## Item 3a: level, placement, environment

The pipstub tests are in-process, beside the existing tests in `main_test.go`, and reuse `resetState`. The chart's security rules are checkable offline with `helm template` but have no assertion in CI (row 6).

## Item 4: names by content

None. No positional or ordinal names found.

## Item 5: failure report

None. The Go assertions print both operands, and the test names state content.

## Item 6: what the writer says it verified

Neither the commit messages nor the change state a red run on the base commit or a mutation verdict for the pipstub tests. The title's restricted-PSS claim has no evidence either (row 6).

## Item 7: siblings

- The security context is on all five containers and all five Pods in the render, so there is no missed sibling there.
- The Makefile twins (`e2e-*`/`parity-*`) are symmetric.
- Two prose sentences still count the old set (row 9).
- The `pip_control.go` caveat is the sibling comment of the same control surface (row 10).

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | `-test.timeout 600s` (Go's own limit) fires at 10 min, before the 900 s Job deadline and before any raised `E2E_SUITE_TIMEOUT`. The commit's stated use case (a longer suite) still fails at 10 min. | Substantive | `helm-templates/authz-test-stand/values.yaml:95`, `:99`; `test/k8s/test-stand-values.yaml:55`; `Makefile:49-51` (comment says to raise only the wait and `activeDeadlineSeconds`) | Derive `-test.timeout` from `activeDeadlineSeconds`, or name it in the comment and the chart README as a third value to raise. |
| 2 | Image-pull fault: old `wait --for=condition=Ready --timeout=3m` failed at about 3 min. The new loop runs 90 × 2 s, then `logs -f` fails, then `wait $helm_pid` returns only when `helm test` times out (or the Job deadline fires), about 15 min, with helm's generic error. Not run (no cluster). | Substantive | `Makefile:105-112` (loop at `:109`) | Run the fault (remove the image from the node, `make e2e-suite`), record duration and output. Then bound the wait at the old 3 min or print the pod state as the old `wait` did. |
| 3 | At defaults, helm's 15 m timeout and the Job's 900 s deadline are equal. Helm's clock starts before the hook Job exists, so helm's timeout reports first and the Job's deadline never decides. Raising `E2E_SUITE_TIMEOUT` above the CI job's remaining budget (`timeout-minutes: 30`) has no effect in CI. | Substantive | `Makefile:51-52`; `helm-templates/authz-test-stand/values.yaml:99`; `.github/workflows/integration-tests.yaml:120`, `:168` | Default the wait above the deadline (for example 16 m), or derive it, and note the CI job cap in the comment. |
| 4 | The remedy for "invalid ownership metadata" (`make e2e-down`) is documented but not run on a state an older `make e2e` left behind. | Substantive | `test/k8s/README.md:47-49`; `docs/local-integration-tests.md:190` | Run the base commit's `make e2e-harness`, then the new one (expect the failure), then `make e2e-down`, then the new one. Record the output. |
| 5 | Documented commands with no running counterpart: the `helm upgrade --reuse-values` subset run, and the transfer-image install (`docker create`, `docker cp`, `helm upgrade --install ./charts/...`). No CI job or target runs them. | Substantive | `docs/local-integration-tests.md:137-140`; `helm-templates/authz-test-stand/README.md:40-66` | Run each once on kind (the subset on the stand; the transfer steps from the built transfer image) and record the outcome, or make them Make targets. |
| 6 | The restricted Pod Security Standard is claimed (title of `17b17fc`) but nothing enforces or checks it: no namespace label in the harness targets, no CI step, no render assertion. The chart does satisfy the rules in `helm template` (five containers, five Pods). | Substantive | `Makefile:89-90` and the parity harness target; `.github/workflows/integration-tests.yaml:83-84` (lint only); `test/scripts/test-chart-render.sh` (no test-stand assertions) | Label the harness namespaces `pod-security.kubernetes.io/enforce: restricted`. Add render assertions for `runAsNonRoot`, `seccompProfile`, `allowPrivilegeEscalation: false`, `drop: [ALL]`, and `readOnlyRootFilesystem` on every container except Keycloak. |
| 7 | Hunks no commit sentence claims: the dev CI config adds three images that get built and published on dev CI (only the release is claimed); a Keycloak pin in the SVT compose file changes 26.0 to 26.3.5@digest; the issuer correction in the realm description; the CI generate and lint step. | Substantive | `.github/docker-dev-config.json:12-24`; `test/svt/common/compose/docker-compose.yml:4`; `test/k8s/authn/REALM-DESCRIPTION.md:10-12`; `.github/workflows/integration-tests.yaml:76-84` | Name each in the commit message with its run, or move the SVT pin and the dev-config change to their own commits. |
| 8 | Claimed cases with no test: a routed path with no responses and no default route should get 404 (commit `9d25da7` says "or to 404"). `/pip-stub/configure` accepting `*` is claimed but not exercised through the handler. | Substantive | `test/integration/pipstub/main_test.go:235-242` (table lacks the case); `test/integration/pipstub/main.go:385-405` (`handleConfigure`, no test) | Add the case to the table. Add a test that PUTs `[{"path":"*",...}]` to `/pip-stub/configure` and then GETs an unrouted path. |
| 9 | Stale counts: the README says CI "builds both" images from the dev config, which now lists five. The publication doc says "The two-entry array". | Substantive | `README.md:59`; `.github/docs-for-publication-task.md:77` | Replace with a count-free phrase ("the images in ...") in both places. |
| 10 | Parity caveat 3 says "No wildcards" for path matching. The same stub now has a `*` default route, so a reader would think no catch-all exists. | Substantive | `test/parity/suite/pip_control.go:29-30` | Name the `*` default route in the caveat, or say it applies to route keys only. |
| 11 | The commit message for `8b85515` names only the `parity-mt-b` realm. `parity-realm.json` also gains roles, the `parity-m2m-tenant-a` client, a claim mapper, and the `mt-a` users, which only the README describes. | Taste | `test/k8s/parity/idp-seed/parity-realm.json:29`, `:121`; `test/k8s/parity/idp-seed/README.md` | Name them in the commit message. |
| 12 | The idp-seed README puts the `parity-m2m-tenant-b` client in the paragraph about `parity-mt-b-realm.json`. The client is in `parity-realm.json`. | Taste | `test/k8s/parity/idp-seed/README.md:12` | Say which realm holds the client. |
| 13 | "so the cases that need those users run on the kind harness" refers to no case, since `testdata/realm/` holds only a README ("none so far" in the commit). | Taste | `test/parity/README.md:70` | Say that no case uses the mechanism yet. |

**Not checked:** I did not run the suites, any Makefile target that touches a cluster, a Helm install against a cluster, or the image builds (`docker` was not run for `test-stand-files`). I did not run the other Go modules' tests (only pipstub). I did not verify whether Go's server maps `OPTIONS *` to path `*`, so the pipstub header sentence "No request path is *" is unconfirmed. The drift script parses no Go, so the member-level comment checks were manual.
