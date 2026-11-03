## Final review: `17b17fcf..HEAD` (commit `5dcb6be`)

No previous report exists for this change, so there is no table of earlier findings. The change touches `Makefile`, two READMEs, and `docs/local-integration-tests.md`. The drift script produced no output and exit 0, because it parses none of these files, so the comment reading below is manual. The `final-review` skill's Item 2 and Item 6 requirements to name a run are not met by the commit, and I could not run one: there is no cluster here.

Review comment status: (1) the remedy is documented in both files, which satisfies the request. (2) `kubectl logs job/<name>` replaces `--logs`, which matches the Makefile's own `kubectl logs job/$(3)`. (3) a per-suite variable exists, but it does not raise the other limits with it, so the request is only partly met.

### Item 1: comments consistent with the code and with each other

Checked the four comment-bearing hunks against the code. `Makefile:101-104` ("no shorter than its suite.activeDeadlineSeconds") matches `run-suite`. `Makefile:49-50` ("raises this together with suite.activeDeadlineSeconds") is incomplete (finding 1). The README's "keep that at least as long as" (`helm-templates/authz-test-stand/README.md:69`) is true at equality, but equality is the default case (finding 2). No comment narrates the change: "no longer than" at README:69 is a bound, not a "now" or "used to". Findings: 1, 2.

### Item 2: claimed cases covered

Claimed cases: (a) the suite log prints after `helm test`; (b) `make e2e-harness` and `make parity-harness` on an old cluster are fixed by `make e2e-down`; (c) E2E and parity suites can outlast 15 minutes.

Commands the change tells a reader to run, against the target that runs them:

| Documented command | Runs the same way | Outcome |
| --- | --- | --- |
| `helm test authz-test-stand --timeout 15m` (chart README:65) | `make -n e2e-suite` → `helm … test authz-test-stand --timeout 15m` (Makefile:108) | same flags; waits, exits with suite outcome |
| `kubectl logs job/parity-suite` (chart README:66) | `run-suite` → `kubectl logs -f job/$(3)` (Makefile:111) | same command; prints the retained Job's log |
| `make e2e-down` (test/k8s/README.md:49, docs:190) | target `e2e-down` (Makefile:135) | deletes the kind cluster, so the old objects go |
| `make e2e` after `e2e-down` | target `e2e` (Makefile:61) | same |

Hunk-to-claim check: the keycloak troubleshooting row (`docs/local-integration-tests.md:191`) is a hunk no sentence of the commit message claims (finding 5). Every other hunk is claimed.

The commit message's Helm 4.3.1 and Helm 3.22.1 behavior is not verified here. The local binary is `v4.3.0`, and its `helm test --help` says `--logs` dumps "logs from test pods", which agrees with the claim.

Findings: 5, 6, 7, 8.

### Item 3: boundaries, partitions, and the negative control

Limits on the suite work, each with where it is set:

- **Job `activeDeadlineSeconds`**: 900 by default (`helm-templates/authz-test-stand/values.yaml:99`). The release values set it at `e2e-harness`. `E2E_SUITE_TIMEOUT` at `e2e-suite` does not change it.
- **Go `-test.timeout 600s`**: in `suite.args` (`values.yaml:95-96`, runtime `test/k8s/test-stand-values.yaml:55-56`, parity inherits the default). It bounds the whole test binary, so it counts, and it is not raised by the change.
- **`helm test --timeout`**: 15m by default (`Makefile:51`). `make -n` shows it reaches helm, as `--timeout 15m`, and as `--timeout 30m` with `E2E_SUITE_TIMEOUT=30m`.
- **CI job `timeout-minutes: 30`** (`.github/workflows/integration-tests.yaml:120`, `:168`): encloses image builds, harness, install and the suite.
- The `kubectl wait` (2m) and the log poll (180s) in `run-suite` do not enclose the Job, so they are not counted.

Defaults: the Job's 900s and helm's 15m are equal, and helm's wait starts at or before the Job's clock. I did not verify the start order against helm's source. Findings: 1, 2, 3.

Item 3a is covered by the next paragraph; the change adds no test.

The change replaces no mechanism: `--timeout` moves from a constant to a variable, and the wait loop is unchanged.

State the change meets: old objects from the pre-`8b85515` `kubectl apply` harness. The documented remedy is `make e2e-down`, but no run on that state is stated (finding 7).

### Item 3a: level, placement, and the environment

No test is added or changed. The behavior is only observable through a cluster run, which the change does not describe. The new variables are checked by `make -n`, which I ran. Findings: 7.

### Item 4: names by content, not by position

None. The changed text has no ordinal or positional reference.

### Item 5: the failure report

None. The change has no assertions.

### Item 6: what the writer says it verified

The commit message states no red run and no run of `kubectl logs job/…`, nor a run of `make e2e-down` followed by `make e2e` on a cluster holding the old objects. Findings: 7.

### Item 7: siblings of the change

- Set members: `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` are new. The override paragraph in `test/k8s/README.md:66-70` names the other variables (`E2E_HELM_ARGS`, `E2E_BASE_URL`, `PARITY_AC_BASE_URL`) and not these two (finding 4).
- Stale count and digit prose: none found.
- `--logs` in other docs: none left (grep of `*.md`).
- `15m` elsewhere: only the chart README and the Makefile.
- Symptom rows: the docs row names two targets and its action names one path (finding 6).

Findings: 4, 6.

### Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The Go `-test.timeout 600s` in `suite.args` fires inside the Job at 10 minutes, so raising `activeDeadlineSeconds` and `E2E_SUITE_TIMEOUT` past 10 minutes alone does not let a suite outlast 10 minutes. | substantive | `helm-templates/authz-test-stand/values.yaml:95-96`; `test/k8s/test-stand-values.yaml:55-56`; `Makefile:49-50` | Raise `-test.timeout` in the same change, or name it in the `Makefile` comment and chart README step 3 as the third limit that moves with the other two. |
| 2 | At the defaults the helm wait (15m) equals the Job deadline (900s). The enclosing wait can fire first, so the Job's own `DeadlineExceeded` may not be the reported failure. I did not verify the clock start order in helm's source. | substantive | `Makefile:51`; `values.yaml:99`; `helm-templates/authz-test-stand/README.md:69` | Default `E2E_SUITE_TIMEOUT ?= 16m` and `PARITY_SUITE_TIMEOUT ?= 16m`, and change "at least as long as" to "longer than". |
| 3 | The CI job's `timeout-minutes: 30` encloses the image builds, harness, install and the suite. A suite timeout raised past the job's remaining budget fires there first, and the Makefile and README do not say so. | substantive | `.github/workflows/integration-tests.yaml:120`, `:168`; `Makefile:49-50` | Name the 30-minute job limit in the `Makefile` comment or in the `test/k8s/README.md` override paragraph. |
| 4 | The override paragraph lists the variables and where each takes effect, and omits the two new ones. It also does not say that `suite.activeDeadlineSeconds` is set at `e2e-harness` through `E2E_HELM_ARGS`, not by `E2E_SUITE_TIMEOUT` at `e2e-suite`. | substantive | `test/k8s/README.md:66-70` | Add `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` to the paragraph, with `e2e-suite` as the place for the wait and `E2E_HELM_ARGS` at `e2e-harness` for the Job deadline. |
| 5 | The rewritten keycloak troubleshooting row is a hunk no sentence of the commit message claims. | substantive | `docs/local-integration-tests.md:191` | Add a sentence to the commit message, or move the row to its own change. |
| 6 | The new row's symptom names `make e2e-harness` or `make parity-harness`, but its action names `make e2e` only, which does not rerun the parity stand. | substantive | `docs/local-integration-tests.md:190` | Action: "Run `make e2e-down` once, then `make e2e`, or `make parity` for the parity stand." |
| 7 | The documented remedy for the inherited state (`make e2e-down`) is not shown run on a cluster holding the old `kubectl apply` objects. The commit states no run. | substantive | `test/k8s/README.md:48-49`; `docs/local-integration-tests.md:190`; commit `5dcb6be` message | Run `make e2e-down` then `make e2e` on such a cluster and say so in the commit or the PR. Without a cluster, state the remedy as unverified. |
| 8 | The README example hard-codes `parity-suite`, while the sentence above it says the Job is named by `suite.name`. A reader of another stand copies a wrong name. | taste | `helm-templates/authz-test-stand/README.md:66` | Write `<suite.name>`. I expect this to be declined without discussion. |

### What the review did not check

- No cluster, so no run of `helm test`, `kubectl logs`, the `e2e-down` remedy, or the Helm 3/4 log behaviour the commit message describes.
- The Helm clock start order behind finding 2 is from reasoning, not from helm's source.
- The chart was not rendered: `helm template` needs `make test-stand-files`, which needs Docker.
- The drift script parsed no members, so Item 1 is a manual read of four hunks.
- The English style check was a read of the new prose only; no full style pass was done.
