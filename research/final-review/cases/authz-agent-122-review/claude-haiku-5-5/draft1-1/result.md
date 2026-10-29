## Final review: `58316ca6..HEAD` (three commits)

**Scope.** No task statement was handed over, so the claimed cases come from the three commit messages (`8b85515` test-stand chart, `9d25da7` pip-stub default route, `17b17fc` restricted Pod Security) and from the pip-stub test class comments. The drift script ran and printed nothing, which is correct: the range has no Java, Kotlin, Groovy, or Scala files. I read the Go, YAML, Helm, Makefile, and Markdown changes by hand.

**Checks I ran (nothing in the repo changed; `git status` is clean):**
- `go test` on `test/integration/pipstub`: all tests pass.
- Base-behaviour check: in a scratch copy of the base `main.go` with two shim lines, four default-route subtests fail and the routed-but-empty case panics with `index out of range [-1]`.
- `helm lint` and `helm template` on both values files, with the generated `files/` copied into a scratch chart. Both render. A default render emits nothing. Every object carries the chart and app labels. Every pod has `runAsNonRoot`, `RuntimeDefault` seccomp, and dropped capabilities. Only Keycloak is writable. The `/tmp` emptyDir renders. The realm checksum changes with content.
- The Dockerfile's `jq` merge was simulated with local jq, with users and with no user files.
- `make -n` on the harness targets.

### Item 1: comments consistent with code and each other
Findings F1–F5 and F9 below. Substantive: the e2e-harness row and the realm-import list, both wrong about what is installed. The pip-stub doc comment omits the fall-through the change added. The parity-realm description names a test that does not exist. The TAG comment calls tenant-manager a release image. Taste: F10 and F11. No comment narrates the change; the "used to" lines in the diff pre-date it.

### Item 2: claimed cases covered
- The `/pip-stub/configure` path `*` is never exercised (F6). The 404 branch of "falls through … or to 404" has no case (F7). No case in the range uses the default route, although the commit says the stub "comes with the cases that use it" (F8).
- The restricted Pod Security claim has no enforcement. Nothing in the repo labels a namespace `restricted`, and CI does not either. I checked the rendered fields by reading, so the gap is coverage, not content (F9).
- The subset recipe in `docs/local-integration-tests.md` (`--reuse-values --set-string`) is a form no CI job runs (F12).
- Claims I confirmed by render: the default-off behaviour, the realm checksum restart, the pip-stub keys, the tenant map, the client-credentials Secret, the hook annotation, the release set in `.qubership/docker.cfg`.

### Item 3: boundaries, partitions, control, pre-existing state
- Partition: routed-empty with no default (F7).
- Pre-existing state (F13): the base harness applied objects with `kubectl`. Helm 3 does not adopt objects without its ownership annotations, so `make e2e-harness` on a cluster built from the base commit should fail at install. This is from Helm's documented behaviour; I did not run it. CI always starts a fresh cluster, and no document gives a remedy.
- The negative control is in place: the routed-path and no-default 404 cases pass on base.

### Item 3a: level, placement, environment
None. The new pip-stub tests are in-process, sit beside the existing ones, reuse `resetState`, and run in `go-build.yaml`. Chart behaviour is exercised only by the kind CI jobs.

### Item 4: names by content
F10: "A second instance" in `test/k8s/test-stand-values.yaml:21` refers by ordinal to the entry named on the next line. The same ordinal appears in `docs/local-integration-tests.md:18`.

### Item 5: failure report
None. The new Go assertions print both operands, and the table cases are named by their condition.

### Item 6: evidence the tests can fail
F14: `9d25da7` fixes a `-1` index panic and states no red run. On base, the test file does not compile (`undefined: defaultRoute`, `RequestURI`), so a plain base run shows compile errors, not the symptom. The shim run above shows the behaviour does fail on base. The chart has no red evidence available here; CI is its only check.

### Item 7: siblings
Every call site of `containerSecurityContext`, `podSecurityContext`, and the labels helper is covered. All six `routes[` and `counters[` sites in `main.go` use the key correctly, and `handleReset` clears the default route's counter. No references to the removed manifests remain. Unclaimed: the SVT compose Keycloak pin moved from 26.0 to 26.3.5 with a digest, and no commit names it (F15).

### Findings

| # | Item | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | 1 | substantive | `docs/local-integration-tests.md:104`; Makefile e2e-harness comment (~l. 81–84) | The suite Job is a `helm test` hook, created by `e2e-suite`, not by `e2e-harness`. Say so. |
| F2 | 1 | substantive | `test/k8s/authn/REALM-DESCRIPTION.md:82` | The e2e stand imports four realms (`files/realms/e2e/`), including both tenant realms. List them. |
| F3 | 1 | substantive | `test/integration/pipstub/main.go:35`, `:122–124` | "answers every request whose path has no route of its own" also needs "or whose route has no responses". |
| F4 | 1 | substantive | `test/k8s/parity/idp-seed/parity-realm.json:30` | The description names `TestTenantScopedDecisions`, which exists nowhere in the repo. Name a real test or add it. |
| F5 | 1 | substantive | `helm-templates/authz-test-stand/values.yaml:9–10` | The TAG sentence says tenant-manager is at "the release version"; it is not published. Drop it from that sentence. |
| F6 | 2 | substantive | `test/integration/pipstub/main.go:385–399` | Add a test that PUTs a route with path `*` through `handleConfigure`, then serves an unrouted path. |
| F7 | 2, 3 | substantive | `test/integration/pipstub/main_test.go:225–258` | Add a case: a routed path with no responses and no default route gets 404. |
| F8 | 2 | substantive | commit `9d25da7` message | Name the change that adds the parity cases, or add one that configures `*`, or reword the message. |
| F9 | 2 | substantive | `helm-templates/authz-test-stand/templates/_helpers.tpl`; `Makefile` e2e-harness and parity-harness | Label each stand namespace `pod-security.kubernetes.io/enforce=restricted`, or add a render assertion on the security fields. |
| F10 | 4 | taste | `test/k8s/test-stand-values.yaml:21`; `docs/local-integration-tests.md:18` | Name the instance: "the instance for the entitlements endpoint". |
| F11 | 1 | taste | `helm-templates/authz-test-stand/templates/_helpers.tpl:20–21` | "rejects a pinned one" overstates the SCC, which accepts a pinned uid inside the namespace range (not verified here). The authz-agent chart has the same sentence, so expect this declined. |
| F12 | 2 | substantive | `docs/local-integration-tests.md:139` | Run the subset form on kind once, or make it a target CI runs. |
| F13 | 3 | substantive | `test/k8s/keycloak.yaml` and the other base manifests (now removed) | Run `make e2e-harness` over a stand the base commit installed, and state the outcome. Or document `make e2e-down` before upgrading. |
| F14 | 6 | substantive | commit `9d25da7` message | State the red run. Say that the base test file does not compile, so a plain base run is not evidence. |
| F15 | 7 | taste | `test/svt/common/compose/docker-compose.yml` (Keycloak image) | Name this pin in a commit message. |

**Not checked:** no cluster or `docker build` was run. The Dockerfile's `jq` merge was simulated with local jq only. The Keycloak 26.3.5 and pip-stub image users, the OpenShift SCC behaviour, Keycloak's import-at-every-start behaviour, the `kubectl wait --for=create` path (needs kubectl 1.31+), and the docs' `--reuse-values` recipe were read, not run.
