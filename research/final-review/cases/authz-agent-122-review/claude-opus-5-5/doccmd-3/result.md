# Final review: `58316ca..HEAD` (9d25da7 pip-stub default route, 8b85515 test-stand chart, 17b17fc restricted PSS)

No task statement came with this review, so item 2 takes its claimed cases from the three commit messages and the test comments alone. The drift script exited 0 and printed nothing, because it parses only Java, Kotlin, Groovy and Scala. The change is Go, Helm, YAML, Make, Dockerfile, jq and Markdown, so I did item 1 by hand. The repository's instructions have no test-stack line. Under test-authoring §0 I propose this one: `Tests: Go testing (standard library, no testify) for test/integration/pipstub`.

What I ran:
- `go test` and `go vet` on `test/integration/pipstub`: both green.
- `helm lint` and `helm template` with both harness values files, on a copy of the chart in my scratchpad. I built its `files/` by copying the source realm and rule files.
- The jq merge step of `chart-files` with `profile.jq`, locally with jq 1.8.2, on no user files, on one user file, and on a duplicate user.
- `make -n` on the suite and harness targets.

## Item 1: comments consistent with the code and with each other

Two comments state something false, and three lists or statements are incomplete:

- **`docs/local-integration-tests.md:104`** says the `e2e-harness` row installs "the client-credentials Secret, and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` (`templates/suite.yaml:21`), so `helm upgrade --install` does not create it. `test/k8s/README.md` and `values.yaml:86` say the opposite, correctly. A reader expects the suite to run, or to be waited on, at harness time.
- **`helm-templates/authz-test-stand/templates/_helpers.tpl:2-4`** says the selectors keep `app: <name>` "so the Makefile's deploy/<name> … address a part by its Service name". `deploy/<name>` addresses a Deployment by its object name, whatever the selector is. The fact that does depend on the selector is upgrade-in-place: a Deployment's selector is immutable, so a new selector would make `helm upgrade` over the release that 8b85515 installed fail. The comment gives a reason that is not the real one.
- **`test/integration/pipstub/main.go:34-38` and `:122-123`**: both say the default route answers "every request whose path has no route of its own". The change also sends a path whose route has an empty `responses` list to the default route (`main.go:235`), and the commit message and the test comment both state that case. Neither comment lists it, so a reader concludes that an empty route shadows `*`.
- **`test/parity/README.md` (Identity provider section)** says the `parity` realm "also holds the users of `suite/testdata/realm/`, so the cases that need those users run on the kind harness", and that "their files declare none" of the profile fields. That directory holds no user file; the commit message says "none so far". The README describes users and cases that do not exist yet.
- **`helm-templates/authz-test-stand/values.yaml:9-11`** lists the images TAG applies to as "pip-stub, authz-parity-suite, and tenant-manager". The e2e stand also runs `local/authz-runtime-suite` under TAG (`test/k8s/test-stand-values.yaml:48`).
- **`Makefile` (`run-suite` comment)** says `helm test` "prints the log only at the end". It prints the log only with `--logs`, which the recipe does not pass. Without `--logs` it prints none.
- **Narration:** `main.go:37-38` ends with "as it did before the default route existed". That is history in a package comment.

## Item 2: claimed cases covered

**9d25da7, pip-stub:**

| Claimed case | Test |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| Routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| Route with no responses falls through to the default | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| Route with no responses falls through "…or to 404" | **none.** No row has an empty routed route and no default route. That is the exact base-commit index −1 panic with no `*` configured. |
| No `*` configured: unrouted path is 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| Empty `*` route is 404 | `…/an_unrouted_path_with_an_empty_default_route_is_404` |
| Default route serves a sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| "`/pip-stub/configure` now takes the path `*`" | Every test writes `routes[defaultRoute]` directly; none goes through `handleConfigure`. `handleConfigure` stores any path verbatim, so the claim holds by reading. Taste. |

**8b85515, chart:**

| Claimed case | Coverage |
| --- | --- |
| Parts off by default; pip-stub instances keyed by name; tenant map; Secret; suite Job as test hook | My render with both values files shows every part. CI runs `helm lint` with both files (`integration-tests.yaml:83-84`). |
| Keycloak restarts when a realm file changes (`checksum/realms`) | **none.** No render assertion. It is observable offline with `helm template`. |
| `chart-files` merges user files, fills in profile fields, fails on a duplicate | **none in the repository.** No user file exists, so CI runs the merge on zero inputs and never reaches `profile` or the duplicate check. My local run confirms they work: `parity-r29-level-m2m` becomes `R29LevelM2M`, and a duplicate `mt-a` gives exit 1. That evidence is mine, not the change's. |
| Parity realm gains `parity-mt-b` | No suite case uses it. `parity-realm.json` also gains about 318 lines of clients and users (`parity-m2m-tenant-a/b/unknown/empty`, `parity-end-user-tenant-a`, `mt-a`, `mt-a-admin`, `parity-r29-scope`, `parity-r30-scope`). The commit message does not mention them, and no case uses them. |
| Not claimed at all | `test/svt/common/compose/docker-compose.yml` moves Keycloak from `26.0` to `26.3.5@sha256…`. The commit message does not mention it and no SVT run is cited. |

**17b17fc, restricted PSS:**

| Claimed case | Coverage |
| --- | --- |
| Pod and container security contexts; read-only root filesystem except Keycloak; `/tmp` emptyDir; labels; selectors unchanged | Correct in my render for every object. Every image runs a numeric non-root user: `USER 10001:10001` in the pip-stub, parity, tenant-manager and runtime-suite Dockerfiles, and 1000 in the Keycloak image. No repository test asserts any of it. |
| "the stand starts in a namespace that enforces restricted" | **none.** Nothing labels a namespace `pod-security.kubernetes.io/enforce=restricted`, and `--create-namespace` adds no such label. CI's kind jobs therefore never run under enforcement. |

**Command lines:**

| Command (where) | What runs it |
| --- | --- |
| `make test-stand-files` | CI chart job, `integration-tests.yaml:77` |
| `make e2e-harness`, `make e2e-suite`, `make parity-harness`, `make parity-suite` | CI kind-e2e and kind-parity, on a fresh cluster only. `kubectl wait --for=create` needs kubectl 1.31 or later; my local client is 1.33.9. I did not verify which version kind-action v1.15.1 installs. |
| `docker build … build/authz-agent-transfer/Dockerfile .` (Dockerfile header) | `.github/docker-dev-config.json` lists it. I found no workflow under `.github/workflows` that reads that file, so not verified. |
| Chart README steps 1–3: `docker create … true`, `docker cp`, `helm upgrade --install … --set TAG=<version>`, `helm test … --logs` | **none.** These depend on the published transfer, pip-stub and parity-suite images, which exist only after a release. `docker create` works on a `FROM scratch` image only because `true` supplies the missing command. `helm test --logs` and its non-zero exit are Helm's documented behavior. Not run. |
| `docs/local-integration-tests.md`: subset via `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false`, then `make e2e-suite` | **none.** It depends on `--reuse-values` keeping the generated `files/` in the chart directory, which `e2e-harness` regenerates. Not run. |

## Item 3: boundaries, partitions, and the negative control

- **pip-stub:** the control is present: no `*` gives 404 as before. The partition "routed route empty and no default route" is missing (see item 2). The empty-`*` boundary is present.
- **Chart partitions:** with and without a rule file, e2e and parity realms, and with and without a ServiceAccount are all rendered by CI lint.
- **State an earlier version left behind (substantive):** a developer's existing kind namespaces `authz-e2e` and `authz-parity` hold objects that the old `kubectl apply` harness created under the same names. These are the Deployments `keycloak`/`idp`, `pip-stub`, `entitlements-mock`, `pip-mock` and `tenant-manager`; the Secret `authz-agent-client-credentials`; the ConfigMap `keycloak-realms`; and the ServiceAccount `runtime-suite`. None carries Helm ownership metadata, so `helm upgrade --install authz-test-stand` should refuse ("exists and cannot be imported into the current release"). CI always starts on a fresh kind cluster. No document names the remedy (`make e2e-down`, or deleting the namespaces), and no run of it is shown.
- **17b17fc over a release installed by 8b85515:** the selectors are unchanged, so an upgrade in place should work. No run is shown.

## Item 3a: level, placement, and the environment

- The pip-stub tests are in-process with `httptest`. They sit in the existing `main_test.go` and share `resetState`. This is the right level and placement.
- The PSS, label and checksum claims can be observed offline with `helm template`. The repository already has an offline render-assertion script, `test/scripts/test-chart-render.sh`, which CI runs, but it covers only `authz-agent` and the policy-admin stub. The test stand has only `helm lint`, which checks neither security contexts nor the checksum. The request is render assertions for `authz-test-stand` in that script, and optionally a restricted-enforcing namespace label in the kind harness.

## Item 4: names by content, not by position

- Test and case names are by content.
- `values.yaml:11` has "Keycloak has its own image and pull policy below"; naming `idp.image` and `idp.imagePullPolicy` would be better (taste).
- `$(1)`, `$(2)` and `$(3)` in the `run-suite` comment are Make's parameter syntax, so not a finding.

## Item 5: the failure report

- No finding.
- Every new assertion prints got and want, with the request (`GET %s = %d %s, want %d %s`, `statuses of /a, /b, /a = %v, want %v`, `requestUri %q, path %q, want %q and %q`).
- The subtests are named by condition, `t.Errorf` continues, and `t.Fatalf` is used only before indexing `calls[0]`.

## Item 6: what the writer says it verified

- None of the three commits states a red run on the base commit or a mutation verdict.
- By reading, the base commit would answer 404 on the default-route rows and panic on the empty-route row. That is my inference, not the writer's evidence.
- Nothing states a run of the harness under restricted enforcement, or on an existing stand.

## Item 7: siblings of the change

- **Index −1 fix:** its sibling is `matchRule`'s `respondSequence`, which already guards with `len(...) > 0` (`main.go:275`). No defect there.
- **`counters` keyed by `*`:** `handleReset` clears the whole map, so the default route's sequence resets too.
- **`callRecord`:** it is built only at `main.go:212`. The echo response builds its own map (`main.go:350-356`), so `requestUri` does not reach echoed bodies or goldens. The `/pip-stub/calls` consumers (`testify/entitlements_test.go:244`, `pip_admin_test.go:128,160,206`, `parity/suite/pip_control.go:162`) decode into structs, so the extra field is ignored.
- **Labels and security-context helpers:** every template uses both, as the render shows.
- **Keycloak image pin:** used at `values.yaml:21` and in the SVT compose file. `test/BASELINE.md:24` names 26.3.5 without a digest, which is consistent.
- **Deleted manifests:** no reference to them is left in the tree.

## Findings

| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| `e2e-harness` row claims the suite Job is installed and waited on | Substantive | `docs/local-integration-tests.md:104` | Drop "and the suite Job"; `helm test` creates it in `e2e-suite`. |
| Selector comment gives a false reason (`deploy/<name>` doesn't use the selector) | Substantive | `templates/_helpers.tpl:2-4` | State the real reason: an immutable selector, so `helm upgrade` over an earlier release works. Keep the `-l app=<name>` reason. |
| Default-route comments omit the empty-`responses` fall-through | Substantive | `test/integration/pipstub/main.go:34-36`, `:122-123` | Add "or whose route has no responses". |
| No test for an empty routed route with no `*` (the base-commit panic site) | Substantive | `test/integration/pipstub/main_test.go:236-245` | Add a row: `/routed` with `[]pipResponse{}`, no default route, expect 404 `{"error":"no rule or route for /routed"}`. |
| README describes parity users and cases that don't exist | Substantive | `test/parity/README.md`, Identity provider | Say the directory is empty for now and what happens when a file is added, or defer the sentence until users exist. |
| `chart-files` merge, profile fill-in and duplicate check never run on any input | Substantive | `build/authz-agent-transfer/Dockerfile:39-46`, `profile.jq` | A fixture-based check in CI: one user file (expect the filled-in names) and one duplicate (expect failure). |
| Restricted-PSS, label and realm-checksum claims have no test or run | Substantive | `templates/*.yaml`; `test/scripts/test-chart-render.sh` | Render assertions for `authz-test-stand` in the existing script, and/or label the kind namespaces `pod-security.kubernetes.io/enforce=restricted`. |
| An existing stand's `kubectl apply` objects block `helm upgrade --install` | Substantive | `Makefile` (`e2e-harness`, `parity-harness`); `test/k8s/README.md` | Document the remedy (`make e2e-down`, or deleting both namespaces) and run it on a stand that the old harness created. |
| Unmentioned changes: SVT Keycloak 26.0 → 26.3.5, and about 318 lines of new parity clients and users | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `test/k8s/parity/idp-seed/parity-realm.json` | Name both in the commit message, or split them out; cite an SVT run for the bump. |
| `run-suite` comment: `helm test` "prints the log only at the end" | Substantive | `Makefile`, comment above `define run-suite` | It prints the log only with `--logs`; reword. |
| TAG image list omits `authz-runtime-suite` | Substantive | `helm-templates/authz-test-stand/values.yaml:9-11` | Add it. |
| No red run or mutation evidence stated | Substantive | commit messages | State the base-commit failure for the pip-stub tests. |
| Change narration in a package comment | Taste | `test/integration/pipstub/main.go:37-38` | End the sentence at "answers an unrouted request 404". |
| Tests bypass `handleConfigure` for `*` | Taste | `test/integration/pipstub/main_test.go:241` | One case that registers `*` through `PUT /pip-stub/configure`. |
| "below" points at `idp.image` by position | Taste | `helm-templates/authz-test-stand/values.yaml:11` | Name `idp.image` and `idp.imagePullPolicy`. |

I did not check: anything on a Kubernetes cluster or under OpenShift, `make test-stand-files` itself (no Docker build), any release or publish workflow, which kubectl version kind-action installs, or the wording outside the sentences above, since no prose pass for style alone was done.
