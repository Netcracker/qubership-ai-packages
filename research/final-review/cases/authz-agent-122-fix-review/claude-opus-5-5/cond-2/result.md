I filled in the final-review form for commit `5dcb6be`. It changes only the Makefile and Markdown pages, so I followed the form's version for changes with no code (§2a). The drift script printed nothing, because it does not parse Makefile or Markdown. I changed no files.

## Item 1: comments consistent with the code and with each other
Here "comments" means the Makefile comments and what the pages say about the Makefile, the chart and Helm. I checked each against `Makefile`, `values.yaml`, `templates/suite.yaml` and the two harness values files.

- **`Makefile:49-50`** ("A suite that runs longer raises this together with suite.activeDeadlineSeconds") and **`Makefile:103-104`** ("no shorter than its suite.activeDeadlineSeconds"). Both name two limits, but the suite has three. `suite.args` passes `-test.timeout 600s` (`values.yaml:95-96` for parity, `test/k8s/test-stand-values.yaml:55-56` for e2e). That timeout covers the whole test binary and fires at 10 minutes. A reader who raises only the two named limits still has the suite killed at 10 minutes. The commit message makes the same claim: "a suite given a longer deadline in its values still failed after 15 minutes". On these values the suite already stops at 10 minutes. Details and the request are under item 3.
- `helm-templates/authz-test-stand/README.md:61-70` agrees with `suite.yaml`: the Job is a `test` hook, it is kept after the run, and `before-hook-creation` deletes the earlier Job. Nothing else to report.

## Item 2: claimed cases covered
The three review comments and the commit message claim these cases:

| Claimed case | Where it is handled |
| --- | --- |
| An old cluster stops `e2e-harness` with the ownership error | `test/k8s/README.md:47-49`, `docs/local-integration-tests.md:190` |
| `parity-harness` fails the same way | `docs/local-integration-tests.md:190` (the symptom column only; see item 7) |
| `--logs` prints nothing for a Job; `kubectl logs job/<suite.name>` does | chart README:61-66 |
| A timeout per suite, wired to `--timeout` | `Makefile:51-52, 107, 115, 163`. `make -n e2e-suite E2E_SUITE_TIMEOUT=30m` and `make -n parity-suite PARITY_SUITE_TIMEOUT=30m` both render `--timeout 30m` |

Commands the change tells someone to run:

| Command | Promised outcome | Run elsewhere with the same flags |
| --- | --- | --- |
| `make e2e-down`, then `make e2e` | The install succeeds on an old cluster | `kind delete cluster`, then CI's fresh-cluster path. This is equivalent. |
| `helm test authz-test-stand --timeout 15m` | Exits with the suite's outcome | `run-suite` in CI (Helm v4.3.1) |
| `kubectl logs job/parity-suite` after `helm test` | Prints the suite log | `none`. `run-suite` runs `kubectl logs -f` while the Job runs, not afterwards. |
| `E2E_SUITE_TIMEOUT=… make e2e-suite`, and the parity variant | Sets helm's wait | `make -n` output above. CI uses the default. |

- **Substantive, plausible:** for the `none` row, the outcome depends on how the Job ended.
  - When the suite fails or passes on its own, the Pod stays and the log can be read.
  - When `activeDeadlineSeconds` fires, the Job controller ends the running Pod with reason `DeadlineExceeded`. A Pod that has been deleted has no log to read, so `kubectl logs job/parity-suite` afterwards may find no Pod.
  - The deadline clock starts before the image pull, so a slow pull plus a 10-minute run can reach it.
  - **Request:** run that fault on a cluster, or document streaming the log while `helm test` runs (`kubectl logs -f`, as `run-suite` does).
- I believe the version claims about `--logs` are correct. As I remember the Helm 3 `GetPodLogs` source, it asks for a Pod named after every test hook. The help of the local Helm 4.3.0 says "dump the logs from test pods". The commit message reports runs on 4.3.1 and 3.22.1.
- No hunk changes anything the change does not claim. The rewording of the Keycloak row in the troubleshooting table only fixes a stale step.

## Item 3: boundaries, partitions, and the negative control
- **Pre-existing state:** the remedy is to delete the whole cluster, which removes every object `kubectl apply` created. A run of it on an old cluster is not stated, but its outcome is the fresh path CI already runs. No finding.
- **Values users already pass:** the two new variables are read nowhere else (`git grep`). No finding.
- **Mechanism replaced, `helm test --logs` → `helm test` then `kubectl logs`:** see item 2 for the deadline fault.
  - **Taste:** when the suite fails, `helm test` exits non-zero. A reader who pastes the two lines into a script with `set -e` then loses the log, which is the case the log is for. `helm test …; kubectl logs …`, or a note, would avoid that.
- **Limits on the suite's work** (the request is the same for each):

  | Limit | Set at | Default |
  | --- | --- | --- |
  | `-test.timeout` | `suite.args` in both values files | 600s |
  | Job `activeDeadlineSeconds` | values (`values.yaml:99`) | 900s |
  | `helm test --timeout` | `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` | 15m |
  | CI job `timeout-minutes` | `.github/workflows/integration-tests.yaml:120, 168` | 30 (also covers the image build, the harness's 10m wait and the installs' 5m+5m) |

  - **Substantive:** raise `PARITY_SUITE_TIMEOUT` and `activeDeadlineSeconds` past 10 minutes, as the comments say, and `-test.timeout 600s` still ends the run at 10 minutes. The raise has no effect.
  - **Substantive:** in CI, a suite timeout above roughly 10 to 15 minutes is cut off by the 30-minute job limit, because the steps before the suite use part of it.
  - **Smaller point:** at the defaults, helm's 15m and the Job's 900s are equal. Helm's clock starts before the Job exists, so helm stops waiting before the Job's own deadline fires. The README's "at least as long as" allows that.
  - **Request:** derive one limit from the next in the Makefile comment and the chart README: `-test.timeout` below `activeDeadlineSeconds`, below the helm timeout, below the CI `timeout-minutes`. Or name all four limits in the sentence that says what to raise.

## Item 3a: level, placement, and the environment
The changed files are documentation, a Makefile, and no chart template, so `helm lint` has nothing new to check. `make -n` on both suite targets renders the variables correctly. The pages are in the places their sibling pages are. Nothing to report.

## Item 4: names by content, not by position
The `$(1)`…`$(4)` parameters of `run-suite` are positional because `$(call)` allows nothing else, and the comment names each one. Nothing to report.

## Item 5: the failure report
The change adds no assertions or tests. Nothing to report.

## Item 6: what the writer says it verified
The commit message gives the observed `--logs` behavior on Helm 4.3.1 and 3.22.1. It does not state:
- a run of a suite longer than 15 minutes with the new variables;
- the remedy run on an old cluster;
- `kubectl logs job/…` run after a Job that hit its deadline.

## Item 7: siblings of the change
- **Substantive:** `docs/local-integration-tests.md:190` names `make e2e-harness` or `make parity-harness` in the symptom. The cause names only "an older `make e2e`", and the action says "then `make e2e`". A parity user needs `make parity` after the cluster is deleted. **Request:** "then `make e2e` or `make parity`", and "an older `make e2e` or `make parity`" in the cause.
- **Substantive:** `test/parity/README.md:28-31` ("Run the replay suite") is the parity twin of the section where the note was added in `test/k8s/README.md`. It has no note, although the review comment says `parity-harness` fails the same way. **Request:** add the same sentence there, or a link to it.
- **Substantive:** the list of override variables in `test/k8s/README.md:66-71` names `KIND_CLUSTER`, `E2E_HELM_ARGS`, `E2E_BASE_URL`, `PARITY_AC_BASE_URL` and the others, but not `E2E_SUITE_TIMEOUT` or `PARITY_SUITE_TIMEOUT`. **Request:** add them, with the limits from item 3.
- The root `README.md:122-126` run block links to `test/k8s/README.md` for details, so it needs no note of its own.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| "Raise with `suite.activeDeadlineSeconds`" leaves out `-test.timeout 600s` in `suite.args`, which ends the suite at 10m; the commit message's 15-minute claim is wrong too | Substantive | `Makefile:49-50, 103-104` | 1, 3 |
| The four limits (`-test.timeout`, `activeDeadlineSeconds`, helm `--timeout`, CI `timeout-minutes: 30`) are not derived from each other; helm fires before the Job deadline at the defaults | Substantive | `Makefile:49-52`, `helm-templates/authz-test-stand/README.md:69-70` | 3 |
| `kubectl logs job/…` run after `helm test` may find no Pod when `activeDeadlineSeconds` fired; no run of that case | Substantive (plausible) | `helm-templates/authz-test-stand/README.md:64-66` | 2 |
| The symptom names `parity-harness`, but the cause and action name only `make e2e` | Substantive | `docs/local-integration-tests.md:190` | 7 |
| The parity run section has no note about old clusters | Substantive | `test/parity/README.md:28-31` | 7 |
| The list of override variables leaves out `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` | Substantive | `test/k8s/README.md:66-71` | 7 |
| Under `set -e`, a failed `helm test` skips the `kubectl logs` line | Taste | `helm-templates/authz-test-stand/README.md:64-66` | 3 |

The drift script printed nothing for this commit, because it does not parse Makefile or Markdown. I checked the comments by hand under item 1.
