No previous report exists for this change, so there is no status table to open with. I did not change any file or commit.

**Inputs and loading.** Read `final-review/SKILL.md` in full. Loaded `english-developer-style`. `test-authoring` is not loaded because the change touches no test code. `docs-page-authoring` and `apm-authoring` are not among the three copies you named, so the no-code analogues are used. The change is one commit, `5dcb6be`, touching `Makefile`, `docs/local-integration-tests.md`, `helm-templates/authz-test-stand/README.md`, and `test/k8s/README.md`. `comment-drift.py 17b17fc HEAD` exited 0 and printed nothing: the change has no code members, and the script does not parse Makefile, YAML, or Markdown.

## Item 1: comments consistent with the code and with each other

Substantive points: F1, F2, F4 below. Otherwise:
- The `e2e-down` remedy in `test/k8s/README.md:47-49` and `docs/local-integration-tests.md:190` matches the Makefile: `e2e-down` is `kind delete cluster`, and that removes the old objects.
- The `10m` row in `docs/local-integration-tests.md:191` matches `--timeout 10m` at `Makefile:91`.
- No comment uses `now`, `no longer`, or `used to`.
- The `E2E_SUITE_TIMEOUT` comment at `Makefile:49-50` says the timeout is raised "together with suite.activeDeadlineSeconds". It omits a third limit, which is F1.

## Item 2: claimed cases covered

No test code changed, so no test names apply. The commit's Helm claims are consistent with local sources: the `helm test --help` text reads "dump the logs from test pods", and Helm v3.15.2's `GetPodLogs` calls `Pods().GetLogs(h.Name)` for each test hook. Helm 4.3.1 and 3.22.1 are not checked: the local binary is 4.3.0, and the module cache has only v3.15.2.

Command lines in the changed files:

| Command | Where | Outcome | Matches a run form? |
|---|---|---|---|
| `make e2e-down`, `make e2e`, `make e2e-harness`, `make parity-harness` | docs:190, test/k8s/README:47-49 | Delete cluster; full run; the install step | Yes, the same targets |
| `helm test authz-test-stand --timeout 15m` | chart README:65 | Runs the suite Job within 15m | `none`: the Makefile form adds `--kube-context` and `-n` (rendered by `make -n`). Those select the release, and the README's install step omits them too. Not a finding. |
| `kubectl logs job/parity-suite` | chart README:66 | Prints the Job's log | Yes: `Makefile:110` runs `logs job/$(3)` after `helm test`. The Job survives because `suite.yaml` sets `before-hook-creation`. |
| `helm test authz-test-stand --logs` (removed) | chart README (old) | Helm reads test Pods only | Confirmed as the reason for the fix |

Substantive: F4.

## Item 3: boundaries, partitions, negative control, and limits

Limits on one run of the suite:
- **Outer:** `helm test --timeout`, which is `E2E_SUITE_TIMEOUT` or `PARITY_SUITE_TIMEOUT`, both `15m` (`Makefile:51-52`, rendered at `Makefile:107`).
- **Inner, Job deadline:** `suite.activeDeadlineSeconds: 900` (`helm-templates/authz-test-stand/values.yaml:99`). Neither `test/k8s/test-stand-values.yaml` nor the parity values override it.
- **Inner, Go test binary:** `-test.timeout 600s` in the suite args (`values.yaml:95-96`, `test/k8s/test-stand-values.yaml:55-56`). It is fixed in the values, not in the code.
- **Environment:** CI jobs `kind-e2e` and `kind-parity` have `timeout-minutes: 30` (`.github/workflows/integration-tests.yaml`). They start before the image builds, so they are not counted under the rule, but they cap the whole run.
- **Not counted:** the 2-minute `wait --for=create` and the 3-minute log loop. They end only the streaming, not the work.

At the defaults the order is 600s (Go) < 900s (Job) = 900s (helm). Findings F1 and F2.

State: the change meets a stand created by the old `kubectl apply` harness, and only the docs remedy covers it. Finding F3.

Negative control: the change adds no run with a non-default value. Requests are in F1-F3.

## Item 3a: level, placement, environment

None. The new variables reach CI through `make e2e-suite` and `make parity-suite`, which use the defaults.

## Item 4: names by content

None.

## Item 5: failure report

None. The change has no assertions.

## Item 6: what the writer says it verified

Not stated. The commit records observed Helm behavior, but no run is recorded: not the remedy on an old cluster, not a suite past 15 minutes, not the Helm 4.3.1 and 3.22.1 output.

## Item 7: siblings

- `run-suite` has two call sites (`Makefile:115`, `:163`). Both pass their own variable.
- `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` each appear once.
- `--logs` appears only in the chart README, and it is fixed there.
- `test/k8s/README.md:67` lists the overrides and omits the two new variables. Taste, F5.

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | The Go test binary's `-test.timeout 600s` caps each suite at 10 minutes, under both the 900s Job deadline and the 15m helm wait. The comment at `Makefile:49-50` and the README at `helm-templates/authz-test-stand/README.md:69-70` name only two limits, so a suite past 10 minutes still fails after the two-variable change. | substantive | `helm-templates/authz-test-stand/values.yaml:95-96`, `test/k8s/test-stand-values.yaml:55-56`, `Makefile:49-51` | Derive the Go `-test.timeout` from the same variable, or document all three limits. Show with a run that a suite past 15 minutes passes. |
| F2 | At the defaults, the helm timeout and the Job deadline are both 900s. Helm starts its watch after the Job is created (`hooks.go:77-84` in v3.15.2), and the Job's deadline counts from its own start. Which fires first is a race, and when helm's timeout wins, the `DeadlineExceeded` report is hidden. | substantive | `Makefile:51-52`, `Makefile:104`, `helm-templates/authz-test-stand/values.yaml:99` | Default the helm wait longer than the deadline (for example `16m`), and change "no shorter than" to "longer than". Show with a run that the Job's deadline reports first. |
| F3 | The remedy for a stand from the `kubectl apply` harness is documented but has not been run on that state. The skill asks for the documented remedy to be run on that state. | substantive | `docs/local-integration-tests.md:190`, `test/k8s/README.md:47-49` | Run `make e2e-down`, then `make e2e`, on a cluster built by the pre-`8b85515` harness. I could not run this: no cluster here. |
| F4 | The chart README says `helm test` "waits no longer than `--timeout`". In v3.15.2 the timeout is applied to the delete wait for the previous Job (`hooks.go:142`) and to the watch on this one (`hooks.go:84`), separately. Helm 4 is not checked. | substantive | `helm-templates/authz-test-stand/README.md:69` | Reword to say `--timeout` limits each wait, and confirm the wording on Helm 4.3. |
| F5 | The override list does not name the two new variables. | taste | `test/k8s/README.md:67` | Add `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` to the list. |
| F6 | "An older `make e2e`" does not say which stands are affected. The `kubectl apply` objects came from the harness before `8b85515`, the commit that moved the stand to the chart. | taste | `docs/local-integration-tests.md:190`, `test/k8s/README.md:47` | Name the boundary, for example "a stand created before the chart install". |

## What this review did not check

I did not run a cluster, `make e2e-harness`, `helm test`, or `kubectl logs`. The `make -n` expansions were checked. Helm 4.3.1 and 3.22.1 output was not checked: the local binary is 4.3.0, and the source in the module cache is v3.15.2. The drift script ran but found no code members. The prose was checked only where wording changes what a sentence says.
