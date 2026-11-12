# Final review: `58316ca..HEAD` (three commits: 8b85515, 9d25da7, 17b17fc)

There was no task statement. The claimed cases come only from the three commit messages and the comments above the tests. The drift script ran and printed nothing, because it parses only Java, Kotlin, Groovy and Scala. I listed the changed Go members by hand: the `pipstub` package doc, `callRecord.RequestURI`, `defaultRoute`, `handlePIP`, `serve`, the three new tests, and `testify.LoadConfig`. The chart, the Makefile, the Dockerfile and the docs were reviewed through the no-code analogues in §2a. What I ran: `go test` and `go vet` on `pipstub` (both pass), and `helm lint` plus `helm template` on both values files. For those I generated the chart's `files/` in the scratchpad with the same jq program, because `make test-stand-files` would write into the repository.

## Item 1: comments consistent with the code and with each other

- **`build/authz-agent-transfer/profile.jq:2-3`.** The comment says "each part capitalized". The code uppercases a whole part when it matches `^([a-z][0-9]+|m2m)$`. I ran it: `parity-r29-level-m2m` becomes `R29LevelM2M`, not `R29LevelM2m`. A reader who follows the stated rule predicts the wrong last name, and the regex has no comment explaining why those parts are special. Request: state the rule ("a part that is one letter followed by digits, or `m2m`, is uppercased whole; any other part is capitalized") and say why it is needed (it matches the last names on the stand the goldens were recorded on).
- **`test/integration/pipstub/main.go:34-35` (package doc) and `:122-123` (`defaultRoute`).** Both say the default route answers a request "whose path has no route of its own". The code at `:241-245` also sends a path to the default route when its own route has no responses, and the commit message claims that case. Request: add "or whose route has no responses" in both places.
- **`main.go:37-38`.** "as it did before the default route existed" describes the change, not the code. Request: "A stub with no default route answers a request with no route 404."
- **Two sentences a reader has to parse twice.**
  - `main.go:74-76`: "so that a caller that encodes a value in the path differently from one that does not can be told apart". Request: "so that the record shows how the caller encoded a value in the path."
  - `main_test.go:222-224`: in "a stub with no default route, or one with no responses, answers 404", the word "one" could mean a stub or a default route. Request: "…and a path answers 404 when there is no default route or the default route has no responses."
- **Term with no source: "part".** It is used for one chart component in `values.yaml:1-2`, in `README.md:5` and in `_helpers.tpl:2-5`. The same helper takes a `component` argument and writes `app.kubernetes.io/component`. Request: use "component" everywhere.
- **`helm-templates/authz-test-stand/values.yaml:9-11`.** It lists the images that `TAG` applies to as "pip-stub, authz-parity-suite, and tenant-manager". `TAG` also tags whatever `suite.imageRepository` names, which is `local/authz-runtime-suite` in the e2e values. Request: "the images this repository builds: pip-stub, the suite image, and tenant-manager."
- **`docs/local-integration-tests.md:104`.** It says `e2e-harness` installs "…and the suite Job; waits until they are Ready". The Job is a `helm test` hook, so installing the chart does not create it. `test/k8s/README.md` gets this right. Request: drop "and the suite Job".

## Item 2: claimed cases covered

| Claimed case | Test or run that covers it |
| --- | --- |
| The default route answers a path with no route | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A path with a route keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses falls through to 404 (the old index −1 panic) | **none**. The 404 rows use a path with no route, or an empty default route. |
| With no `*` configured, a path with no route answers 404 | `…/an_unrouted_path_without_a_default_route_is_404` |
| Rules take precedence over the default route (package doc) | **none**. No test configures a rule and a default route together. |
| The default route serves its responses in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| The call record keeps the raw target "in `requestUri`" | `TestHandlePIP_RecordsTheRequestTargetAsSent` checks the struct field only, not the JSON name that `/pip-stub/calls` serves. |
| `/pip-stub/configure` accepts `*` | Indirect only: the tests write to `routes` directly. Acceptable, since configure stores any path. |
| The chart's components, the e2e and parity values, `helm test` | The kind-e2e and kind-parity CI jobs, plus `helm lint` in the chart job |
| Users merged into the parity realm, profile fields filled in, a duplicate username or id fails the build | **none**. `testdata/realm/` has no user files, so no build exercises this. |
| The stand starts under the `restricted` Pod Security Standard | **none**. No namespace is labeled `pod-security.kubernetes.io/enforce=restricted`, and no render assertion checks the security contexts. |
| Labels on every object, selectors kept as `app: <name>` | No assertion. I checked it by hand with `helm template`. |

Requests:
- Add a row "a routed path with no responses and no default route is 404" (the regression case).
- Add a test where a rule and a default route both exist.
- Assert `requestUri` in the JSON that `handleCalls` returns.
- Test `profile.jq` and the merge with jq on a fixture: one user, and two files that declare the same username.
- In `e2e-harness` and `parity-harness`, label the namespace `enforce=restricted`, so the kind jobs exercise that claim.

Commands the change documents:

| Command | What runs it |
| --- | --- |
| `make test-stand-files`, `e2e-harness`, `e2e-suite`, `parity-*` | The CI chart, kind-e2e and kind-parity jobs |
| `helm lint … -f test-stand-values.yaml` (both files) | The CI chart job |
| `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false` (`docs/local-integration-tests.md:228`) | none. I rendered it with `helm template` and got the expected env. Taste-level. |
| The `docker create` / `cp`, `helm upgrade --install … --set TAG=<version>`, `helm test --logs` recipe (`authz-test-stand/README.md:39-67`) | **none**. I rendered the edited parity values with `--set TAG=1.0.0` and they resolve to the published image names. Nothing pulls the transfer image or installs from it. Request: one run of the recipe against a released or dev-built transfer image. |

Taste: `kubectl wait --for=create` needs kubectl 1.31 or later. The prerequisites table (`docs/local-integration-tests.md:37`) gives no minimum version.

Hunks that no commit message claims:
- `test/svt/common/compose/docker-compose.yml:3` bumps Keycloak from 26.0 to 26.3.5 with a digest.
- `test/k8s/parity/idp-seed/parity-realm.json` adds much more than the claimed `parity-mt-b` realm:
  - the `ROLE_MT_*` roles;
  - a new `parity-level-claim` mapper on the existing `parity-m2m` client;
  - the clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`, with their service-account users;
  - the users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`.

  Nothing in the repository refers to any of these. The new mapper on `parity-m2m` changes a client that existing cases use.
- `.github/docker-dev-config.json` adds three images to the dev CI build. The message names only the release (`docker.cfg`).

Request: claim each hunk, with the parity run that shows 135/135 still green, or move the realm additions to the change that adds the cases using them. That is what the pip-stub commit already did with its stub instance.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub.** The boundaries and controls are present, except the two missing partitions listed in item 2: a route with no responses and no default route, and a rule together with a default route.
- **State an earlier version left behind.** On a kind cluster that still runs the old harness, the Deployments, ConfigMaps, the Secret and the ServiceAccount were created by `kubectl apply`. `helm upgrade --install authz-test-stand` then refuses them because their ownership metadata does not name the release. No document gives a remedy. Request: run it from that state, or document `make e2e-down` or deleting the namespace (Helm 4 also has `--take-ownership`).
- **`E2E_HELM_ARGS` now reaches the test-stand chart** (`Makefile:178`, `:251`). The two charts share the names `TAG` and `IMAGE_PULL_POLICY`. A `--set TAG=<x>` meant for the agent makes the stand ask for `local/pip-stub:<x>`, `local/authz-runtime-suite:<x>` and similar images, which `e2e-images` never builds. Request: a separate variable for the test stand, or a run with such a value.
- **The suite runner changed.** The old Makefile waited 3 minutes for the Pod to be Ready, then 1 minute for the Job to complete.
  - On a Pod that never starts (an image not loaded, a bad pull), the old target failed at about 3 minutes with a timeout message.
  - The new target (`Makefile:100-106`) polls about 3 minutes, `logs -f` fails, then `wait $helm_pid` blocks until `helm test --timeout 15m` or the Job's 900-second `activeDeadlineSeconds` ends it. That is about 15 minutes. In CI, after image build plus up to 10 minutes of harness install, this can run into the job's `timeout-minutes: 30`.
  - No sentence in the change accepts the later failure. Request: a run of that fault, with its duration and output, and a deadline near the old 3 minutes. For example, kill helm once the poll loop is exhausted.
- **Limits on the same work.** `helm test --timeout 15m` is hard-coded in `Makefile:102` and `README.md:64`. It equals `suite.activeDeadlineSeconds: 900` and sits inside `-test.timeout 600s` from `suite.args`. Raising `activeDeadlineSeconds` past 900 has no effect through `make e2e-suite`. At the defaults, helm's timeout and the Job deadline race each other. Request: derive the helm timeout from `suite.activeDeadlineSeconds`. The `/tmp` emptyDir `sizeLimit` is already derived from the container's ephemeral-storage limit.

## Item 3a: level, placement, and the environment

- The pip-stub tests are in-process, in `main_test.go`, and share `resetState`. That is the right level and place.
- Several chart claims can be seen with `helm template`, which `test/scripts/test-chart-render.sh` already runs in CI for the other two charts: the two `fail` messages, `tenantManager.tenants is required`, the labels, and the security contexts. That script has no assertion for this chart. Request: assertions there.
- Enforcement of the restricted standard only exists at admission, so the CI job that should run it is the kind job, which does not label the namespace (item 2).

## Item 4: names by content, not by position

None. I checked the test names, the subtest names, the comments, and the README and Makefile cross-references. `$(1)`/`$(2)`/`$(3)` are Make macro parameters and are explained where they are defined.

## Item 5: the failure report

None. Every Go assertion prints got and want, the table cases are named by condition, and `t.Fatalf` is used only where the next line would index `calls[0]`.

## Item 6: what the writer says it verified

None of the messages states a red run on the base commit or a mutation verdict. From reading the code, the row "a routed path with no responses gets the default answer" would panic on the base at index −1, but the writer does not say so. Nothing states a run under an enforcing namespace or of the transfer-image recipe.

## Item 7: siblings of the change

- **`README.md:58`.** "CI builds both via `.github/docker-dev-config.json`" now covers five images. Request: update the count and the list.
- The other lists of images (`docker.cfg`, the release workflow header, the release paragraph in `README.md`) and of realms (the Dockerfile header and `COPY`, `idp-seed/README.md`, `test/parity/README.md`) all name the new members.
- `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` still match the instance names.
- The `pipstub` counter key `*` is cleared by `handleReset`, like every other key.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| "each part capitalized" is false for `r29` and `m2m`; the regex is unexplained | Substantive | `build/authz-agent-transfer/profile.jq:2` | 1 |
| Default-route comments omit the case of a route with no responses | Substantive | `test/integration/pipstub/main.go:35`, `:123` | 1 |
| Package doc describes the change ("as it did before") | Substantive | `test/integration/pipstub/main.go:37` | 1 |
| Two sentences a reader has to parse twice (RequestURI; "or one with no responses") | Substantive | `main.go:74`, `main_test.go:224` | 1 |
| Term "part" has no source; the code's word is "component" | Substantive | `values.yaml:1`, `_helpers.tpl:2`, `authz-test-stand/README.md:5` | 1 |
| `TAG` list omits the runtime suite image | Substantive | `helm-templates/authz-test-stand/values.yaml:9` | 1 |
| `e2e-harness` row says it installs the suite Job | Substantive | `docs/local-integration-tests.md:104` | 1 |
| Restricted Pod Security Standard claim not exercised by any test or run | Substantive | `helm-templates/authz-test-stand/templates/_helpers.tpl:17` | 2 |
| No test for a route with no responses and no default route, or for a rule beating the default route | Substantive | `test/integration/pipstub/main_test.go:228` | 2 |
| `requestUri` JSON name not asserted | Substantive | `test/integration/pipstub/main_test.go:276` | 2 |
| User merge, profile fill-in and duplicate check untested | Substantive | `build/authz-agent-transfer/Dockerfile:315` | 2 |
| Transfer-image install recipe never run | Substantive | `helm-templates/authz-test-stand/README.md:39` | 2 |
| Unclaimed hunks: SVT Keycloak bump, parity-realm additions, dev-config images | Substantive | `test/svt/common/compose/docker-compose.yml:3`, `test/k8s/parity/idp-seed/parity-realm.json`, `.github/docker-dev-config.json` | 2 |
| kubectl 1.31 minimum not stated | Taste | `docs/local-integration-tests.md:37` | 2 |
| Install over the old harness's objects fails, with no remedy documented | Substantive | `Makefile:177` | 3 |
| `E2E_HELM_ARGS` `TAG` meant for the agent retags the stand's images | Substantive | `Makefile:178`, `:251` | 3 |
| New suite runner fails a Pod that never starts at about 15 minutes, not about 3 | Substantive | `Makefile:100` | 3 |
| `helm test --timeout 15m` not derived from `suite.activeDeadlineSeconds` | Substantive | `Makefile:102`, `helm-templates/authz-test-stand/README.md:64` | 3 |
| No render assertions for the test-stand chart | Substantive | `test/scripts/test-chart-render.sh` | 3a |
| "CI builds both" now counts five images | Substantive | `README.md:58` | 7 |

Checks I could not do: the drift script does not parse Go, YAML or Makefiles, so I listed the members by hand. With no cluster, I did not run the kind harnesses, the pre-existing-state fault, the image-pull fault, or admission under the restricted standard.
