# Final review: `58316ca..HEAD` (4 commits)

There was no task statement, so the claimed cases in item 2 come only from the four commit messages and the comments above the tests. The drift script printed nothing because it parses only Java, Kotlin, Groovy and Scala, and this change is Go, YAML, Make and Markdown. I checked the comments of every changed member by hand. No previous report exists.

Commands I ran: `helm lint` and `helm template` on both values files (Helm 4.3.0, against a copy of the chart in the scratchpad), the `chart-files` Docker stage, the README's `docker create`/`docker cp` recipe on a locally built transfer image, the jq realm merge on sample user files, and `go test`/`go vet` in `test/integration/pipstub` (green). My `go test` run created an ignored `go.work.sum`, which I deleted. `git status` is clean.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-38`, `:121-123`, `:232-233`.** The package comment, the `defaultRoute` comment and the step-2 comment all say the default route answers "every request whose path has no route of its own". None of them mentions the second case the change added: a route that exists but has no responses also falls through to the default route, or to 404. A reader would expect such a route to answer 404 (or panic, as the old code did).
- **`main.go:37-38`.** "as it did before the default route existed" narrates the change inside a code comment.
- **`docs/local-integration-tests.md:104`.** This says `e2e-harness` installs "the suite Job" and "waits until they are Ready". The Job is a `helm test` hook, so installing the chart does not create it. `test/k8s/README.md` says the same: "installing the stand does not start it".
- **`test/parity/README.md:69-73`, `build/authz-agent-transfer/Dockerfile:30-36`.** The README says the `parity` realm "also holds the users of `suite/testdata/realm/`, so the cases that need those users run on the kind harness", and that "their files declare none". The Dockerfile's comment gives `parity-r29-level-m2m` as an example. But that directory holds only `README.md`, the commit says "none so far", and no file in the repository contains that user. A reader would believe these users exist.
- **`helm-templates/authz-test-stand/README.md:69`, `Makefile:49-50,103-104`.** These sentences are false about the limits; see item 3.
- The other changed comments are true of their code: `helpers.go` `LoadConfig`, the testify `Dockerfile` CMD note, `values.yaml`, `_helpers.tpl`, `idp.yaml` (the checksum does restart the Pod: I changed one realm file and the checksum changed), `REALM-DESCRIPTION.md` (the `/auth` issuer fixes an already stale line), and `test/k8s/README.md`.

## Item 2: claimed cases covered

**From 9d25da7 (pip-stub):**
- An unrouted path gets the default route's answer: `DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer`.
- A routed path keeps its own answer: `…/a_routed_path_keeps_its_own_answer`.
- With no `*` configured, an unrouted path is 404, as before: `…/an_unrouted_path_without_a_default_route_is_404`.
- A route with no responses falls through to the default route: `…/a_routed_path_with_no_responses_gets_the_default_answer`.
- **A route with no responses and no default route answers 404 ("or to 404"): no test.** This is exactly the old index -1 panic.
- The default route serves its responses in sequence: `DefaultRouteServesItsSequenceAcrossPaths`.
- `requestUri` keeps the request target as it arrived: `RecordsTheRequestTargetAsSent`.
- `/pip-stub/configure` takes `*`: tested only by writing `routes` directly, which is how the neighbouring tests set up routes too (taste).
- **The header comment says rules are tried before the routes and the default route (`main.go:29-31`): no test** with a matching rule and `*` both configured. `TestHandlePIP_RuleThenLegacyFallback` is where it would go.

**From 17b17fc (Pod security):**
- **The stand starts in a namespace that enforces the restricted Pod Security Standard: no test or run.** The kind namespaces carry no `pod-security.kubernetes.io/enforce` label, and `test/scripts/test-chart-render.sh` does not render this chart.
- Labels on every object: I checked `helm template` by hand; no test covers it.
- Selectors keep `app: <name>`: confirmed against 8b85515.

**From 8b85515 (the chart):**
- The kind harnesses install the chart, run the suites with `helm test` and stream the log: covered by the CI jobs `kind-e2e` and `kind-parity`.
- Both values files lint: `integration-tests.yaml:83-84`.
- Keycloak restarts when a realm file changes: I checked the checksum by hand.
- `parity-mt-b` is generated into the chart: confirmed in the files the stage writes.
- **The realm merge, the profile fill and the duplicate-user check: no input in the repository ever exercises them.** I ran the jq on two sample files. The fill produces `Parity` / `R29LevelM2M` / `…@example.test`, and a duplicated user makes the check exit 1. Nothing in the build or CI does this.

**From 5dcb6be (timeouts and run notes):**
- `E2E_SUITE_TIMEOUT` lets a suite outlast 15 minutes: not possible; see item 3.
- The README's `kubectl logs` after `helm test`, and `make e2e-down` on an old cluster: see the commands below.

**Commands in changed files, and what runs the same form:**

| Command | What runs the same form |
| --- | --- |
| `make test-stand-files` | CI chart job, `integration-tests.yaml:77` |
| `make e2e-*` / `make parity-*` | the kind CI jobs, Helm v4.3.1 |
| README `docker create … true` / `docker cp` / `docker rm` | none in CI. I ran it on a local build: `/charts` holds the three charts and `files/`. It does not depend on the image having `true`, since `docker create` does not run it. |
| README `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml` | none. I only rendered it with `helm template`: images resolve to `ghcr.io/netcracker/qubership-authz-*:<version>`. Not installed. |
| README `helm test authz-test-stand --timeout 15m` then `kubectl logs job/parity-suite` | CI runs this form with Helm 4.3.1 only. The README describes Helm 3 users, who would take the recipe as working there; nothing runs it on Helm 3. I believe Helm 3 also waits for Job hooks, but that is from memory, not cited. |
| docs subset recipe `helm … upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false`, then `make e2e-suite` | none. It depends on `--reuse-values` keeping the `BASE_URL` that `e2e-harness` set. |
| `make e2e-down` on a cluster an older `make e2e` set up | The commit quotes the error from that state, so the state was met. `e2e-down` deletes the cluster, so the remedy cannot fail on it. |

## Item 3: boundaries, partitions, and the negative control

**pip-stub boundaries.**
- Present: sequence clamped to the last response, the counter shared across paths, an empty default route, no default route.
- Missing: the empty-route-with-no-default case from item 2.

**Earlier state the change meets.**
- Objects that an old `kubectl apply` created: the remedy is documented.
- A release of the chart from 8b85515: selectors unchanged, so `helm upgrade` works.
- An old Job: removed by `before-hook-creation` and by `delete job` in `run-suite`.
- A stale `files/` directory: `rm -rf` first.

**Limits on how long the suite runs:**

| Limit | Value | Where it is set | Counted from |
| --- | --- | --- | --- |
| Go `-test.timeout` | 600 s | `values.yaml:96`, `test/k8s/test-stand-values.yaml:56`, in `suite.args` | container start |
| `activeDeadlineSeconds` | 900 | `values.yaml:99` | Job start |
| `helm test --timeout` | `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT`, 15m | `Makefile:51-52`, README:65 | `helm test` start |
| CI job `timeout-minutes` | 30 | `integration-tests.yaml:120,168` | whole job: image builds, a 10m harness wait, 2×5m installs |

Not limits on this work: the 2m `wait --for=create` and the 3-minute log poll. They bound only the log stream.

- **Substantive: the documented settings cannot do what they promise.** The Makefile comment and the README tell a longer suite to raise the helm timeout together with `activeDeadlineSeconds`. But `-test.timeout 600s` in `suite.args` ends the test binary at 10 minutes either way. Raising both settings past 600 s does nothing, so the commit title's "outlast 15 minutes" cannot happen unless the args change too. In CI, the 30-minute job limit also caps both settings.
- **Substantive: "no shorter than" and "at least as long as" allow equal values.** Helm starts counting before the Job exists. With equal values, Helm's timeout expires first and hides the Job's `DeadlineExceeded`. At the defaults the 600 s limit fires first, so this only bites once someone raises the settings as the comment says.
- Harness: the Keycloak startup probe (300 s) fires before the 10m `--wait`. Inner fires first, as it should.

## Item 3a: level, placement, and the environment

- The pip-stub tests are small, in-process tests, sit beside their neighbours and reuse `resetState`. `go test` and `go vet` pass.
- The chart is linted in CI with both values files.
- The Pod Security claim can only be observed at admission, and no CI job enforces it. The request is the namespace label in `e2e-harness` and `parity-harness`.
- **`Makefile:108` uses `kubectl wait --for=create`, which needs kubectl 1.31 or later (from memory).** The prerequisites table at `docs/local-integration-tests.md:37` gives no version. With an older kubectl, the wait fails, the poll is skipped, `logs -f` fails, and no log is streamed. The Helm exit code still decides the result.

## Item 4: names by content, not by position

None. The test case names state their condition. The `$(1)`…`$(4)` in `run-suite` are Make's positional parameters, and each is defined in the comment.

## Item 5: the failure report

None. Every check prints the input with got and want (`GET %s = %d %s, want %d %s`, `statuses of /a, /b, /a = %v, want %v`, `requestUri %q, path %q, want …`). `t.Fatalf` is used only before indexing `calls[0]`.

## Item 6: what the writer says it verified

None stated. No commit gives a red run on the base commit or a mutation verdict for the new pip-stub tests.

## Item 7: siblings of the change

- **`test/parity/suite/pip_control.go:17-31`, `:185`.** The package note still says pip-stub path matching has "No wildcards". `ResetPinnedRoutes` resets every pinned path to an explicit 404 response. Under the new rules that 404 route shadows a `*` default route that a later test configures. Re-registering a path with an empty response list would now unregister it instead.
- No other site needs the same fix:
  - `handlePIP` is the only reader of `routes` and `counters`.
  - The Deployment names in `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS`, and `exec deploy/pip-stub` and `deploy/pip-mock`, match the chart's names.
  - `git grep` finds no reference to the deleted manifests.
  - Every rendered object uses the labels helper, and every container uses the security-context helper.

## Findings

| # | Finding | Label | Where | Change requested |
| --- | --- | --- | --- | --- |
| 1 | `-test.timeout 600s` caps the suite below `activeDeadlineSeconds` and the helm timeout, so the documented knobs have no effect past 10 min; CI's 30-min job limit caps them too | Substantive | `Makefile:49-50,103-104`; README:69; `values.yaml:96`; `test-stand-values.yaml:56` | Name all three limits in one place and derive one from another, or document that `suite.args` must change too; mention the CI cap |
| 2 | "no shorter than" / "at least as long as" allow equal values, so Helm's timeout expires first | Substantive | `Makefile:104`; README:69 | Require the helm timeout to be strictly longer than `activeDeadlineSeconds`, with a margin for Job start |
| 3 | The restricted Pod Security claim has no test or run | Substantive | `_helpers.tpl`; `Makefile:90,155` | Label the kind namespaces `pod-security.kubernetes.io/enforce=restricted` before installing, so the CI kind jobs enforce it |
| 4 | Comments omit that a route with no responses falls through to the default route or 404; one comment narrates the change | Substantive | `main.go:34-38,121-123,232-233` | Add the second case to each comment; drop "as it did before the default route existed" |
| 5 | No test for a route with no responses and no default route (the old index -1 panic) | Substantive | `main_test.go:233-243` | Add the row `/routed`, `[]pipResponse{}`, `nil` → 404 |
| 6 | The claimed order "rules before routes and default route" has no test | Substantive | `main.go:29-31`; `main_test.go:135` | Add a case with a matching rule and `*` both configured |
| 7 | The docs say `e2e-harness` installs the suite Job and waits until it is Ready | Substantive | `docs/local-integration-tests.md:104` | Drop the Job from that row, as `test/k8s/README.md` already does |
| 8 | The parity README and the Dockerfile describe realm users that do not exist; the merge, profile fill and duplicate check are never run | Substantive | `test/parity/README.md:69-73`; `Dockerfile:30-36` | Say no user files exist yet, or add the first one; give the merge an input the build exercises |
| 9 | `pip_control.go`'s "No wildcards" note is stale, and `ResetPinnedRoutes` leaves 404 routes that shadow `*` | Substantive | `test/parity/suite/pip_control.go:30,185` | Fix it in this change (reset with empty responses, update the note), or name it as follow-up |
| 10 | Documented commands never run in the form or on the version given: the README install, `helm test` + `kubectl logs` on Helm 3, the docs subset recipe | Substantive | README:42-66; `docs/local-integration-tests.md` subset recipe | Run each once (the README recipe also on Helm 3.22.1), or say which Helm version it was run on |
| 11 | `kubectl wait --for=create` needs kubectl 1.31+, and the prerequisites table states no version | Substantive | `Makefile:108`; `docs/local-integration-tests.md:37` | State the minimum kubectl version |
| 12 | No red run on the base commit or mutation verdict stated for the pip-stub tests | Substantive | 9d25da7 | State the red run on 58316ca |
| 13 | The SVT compose Keycloak moved from 26.0 to a pinned 26.3.5, which no commit message mentions | Taste | `test/svt/common/compose/docker-compose.yml:3` | Mention it in the 8b85515 message |
| 14 | The default-route tests write `routes` directly instead of calling `/pip-stub/configure` | Taste | `main_test.go:247-249,263` | One case through `handleConfigure` with path `*` |

This review installed nothing, since there is no cluster: no install, Pod Security admission, `helm test` or Helm 3 behaviour was observed. Of the test suites, only the `pipstub` package was run. The drift script does not parse these languages, so item 1 was done by hand, and the prose was not reviewed for style alone.
