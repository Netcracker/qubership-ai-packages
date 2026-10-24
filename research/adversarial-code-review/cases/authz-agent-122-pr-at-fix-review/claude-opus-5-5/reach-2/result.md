I found 2 blocking and 3 non-blocking issues in the four commits. The blocking ones are the suite timeout fix, which doesn't let a suite outlast 15 minutes, and realm and Keycloak changes that no commit message describes.

**What I ran:** `go vet` and `go test` pass on the pip-stub changes. I generated the `chart-files` stage into the scratchpad, not the repository. `helm lint` passes for the chart with both values files, and `helm template` renders it. I compared the deleted kind manifests with what the chart now renders. I did not run anything on a cluster.

# PR/MR review

Result: REQUEST_CHANGES (2 blocking, 3 non-blocking)
Revision: 58316ca6ca5d0d91932873de01fb40397d5dd4df...5dcb6be836474aeecf2c90c9d50541ad6b1bd2f2

## Findings

### [blocking] The new suite timeout setting cannot let a suite run past 10 minutes

Confidence: high

`Makefile:49-52`, `Makefile:105-111`, `helm-templates/authz-test-stand/values.yaml:92-99`, `test/k8s/test-stand-values.yaml:52-58`, `helm-templates/authz-test-stand/README.md:65-70`

- Problem: The suite is held by three limits, but the change documents only two. The Makefile comment says a longer suite raises `E2E_SUITE_TIMEOUT` together with `suite.activeDeadlineSeconds`. Both suites' `args`, however, also pass `-test.timeout 600s`, which fires first at the defaults. So a suite given 30m in both documented settings still panics at 10 minutes, and the stated goal of commit 5dcb6be ("let a suite outlast 15 minutes") is not reached by the settings it documents. The defaults also set `helm test --timeout` (15m) equal to the Job's 900s deadline, and README says "at least as long". Helm's clock starts before the Job's `startTime`, so with equal values the outer `helm test` limit can fire first. That is the failure 5dcb6be describes: Helm gives up while the Job keeps running.
- Proposed solution: In the Makefile comment and the chart README, name all three limits: `-test.timeout` in `suite.args`, below `suite.activeDeadlineSeconds`, below the `helm test --timeout`. Set the defaults so each inner limit fires first, for example a Makefile timeout above 15m.

### [blocking] Realm, Keycloak and SVT changes that no commit message claims

Confidence: high

`test/k8s/parity/idp-seed/parity-realm.json`, `test/svt/common/compose/docker-compose.yml:3`, `helm-templates/authz-test-stand/templates/idp.yaml:49-58`

- Problem: The commit message of 8b85515 claims only that "the parity realm gains a second tenant realm, parity-mt-b". The diff does more than that, and nothing in the change uses any of it:
  - **New clients:** `parity-m2m-tenant-a`, `-tenant-b`, `-tenant-unknown`, `-tenant-empty`, and `parity-end-user-tenant-a`, plus their four service-account users.
  - **New users and roles:** `parity-r29-scope`, `parity-r30-scope`, `mt-a`, `mt-a-admin`, `ROLE_MT_READER`, and `ROLE_MT_ADMIN`.
  - **Changed existing client:** a `parity-level-claim` mapper is added to the existing `parity-end-user` client, which the recorded goldens use.

  In addition, the SVT Compose stack's Keycloak moves from `26.0` to `26.3.5`, and the e2e Keycloak drops `-Dkeycloak.migration.strategy=OVERWRITE_EXISTING`. Without a stated purpose and a run, a change to the golden-recorded realm or to the SVT IdP version may change token claims that other suites depend on.
- Proposed solution: Either add commit-message sentences that claim these hunks, citing the parity and SVT runs that check them, or move them into the change that adds the cases that use them.

### [non-blocking] `E2E_HELM_ARGS` now also reaches the test-stand install, which reads `TAG` with a different meaning

Confidence: medium

`Makefile:91`, `Makefile:154`, `helm-templates/authz-test-stand/values.yaml:9-13`

- Problem: Every install now receives `E2E_HELM_ARGS`. The test-stand chart reads two keys the agent and authz-policy-admin charts also read: `TAG` and `IMAGE_PULL_POLICY`.
  - **`TAG`:** for the agent chart it is the agent image tag; for the test stand it is the tag of pip-stub, tenant-manager and the suite images. `E2E_HELM_ARGS='--set TAG=x'`, meant for the agent, makes the stand ask for `local/pip-stub:x` with `IMAGE_PULL_POLICY: Never`. `e2e-images` builds only `:ci`, so the harness can fail after its 10-minute `--wait`.
  - **`IMAGE_PULL_POLICY`:** `Always` would make kind try to pull the local-only `:ci` images.
- Proposed solution: Give the test-stand install its own pass-through variable, for example `TEST_STAND_HELM_ARGS`, or document which keys must not appear in `E2E_HELM_ARGS`.

### [non-blocking] The ownership-error remedy covers only the e2e path

Confidence: high

`docs/local-integration-tests.md:190`

- Problem: The symptom names both `make e2e-harness` and `make parity-harness`. The action says "Run `make e2e-down` once, then `make e2e`". `e2e-down` deletes the whole cluster, so someone on the parity path is never told to run `make parity` afterwards.
- Proposed solution: Name the follow-up step for each path: `make e2e` or `make parity`.

### [non-blocking] The Makefile comment says `helm test` prints the suite log

Confidence: high

`Makefile:99-100`

- Problem: The comment says `helm test` "prints the log only at the end". Commit 5dcb6be and the chart README (`README.md:61-62`) state that Helm prints no log for a Job hook. The recipe also passes no `--logs`. The comment explains the streaming loop with behaviour that does not happen.
- Proposed solution: Say that `helm test` prints no Job log, which is why the recipe streams it with `kubectl logs -f`.
