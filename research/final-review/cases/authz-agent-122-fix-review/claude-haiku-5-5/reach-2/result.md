**Final review: `17b17fcf..HEAD` (commit `5dcb6be`, four files: Makefile, `docs/local-integration-tests.md`, `helm-templates/authz-test-stand/README.md`, `test/k8s/README.md`)**

Skills: I loaded `english-developer-style` from the given skills directory. `test-authoring` was not loaded because no test changed. The `docs-page-authoring` skill named for pages is not in that directory, so it was not loaded. The drift script ran with no output and exit 0. It does not parse Makefile, YAML or Markdown, so item 1 was done by reading. I ran `make -n` as a dry check and did not change any file.

Verified by dry run: `make -n e2e-suite` and `make -n parity-suite` both pass `--timeout 15m`, and `E2E_SUITE_TIMEOUT=20m` passes `20m`. `go help testflag` confirms `-timeout` panics when a test binary runs past its duration. Local `helm` is v4.3.0, and `helm test --logs` is described as "dump the logs from test pods"; CI pins v4.3.1. No cluster, so no run of any command.

### Item 1: comments consistent with the code and with each other

Substantive. `Makefile:49-50` says "A suite that runs longer raises this together with suite.activeDeadlineSeconds in its values." That is false as shipped. The suite's own `-test.timeout 600s` (`test/k8s/test-stand-values.yaml:55-56` for the runtime suite, `helm-templates/authz-test-stand/values.yaml:95-96` for the parity suite) panics the test binary at 10 minutes. See item 3.

Also substantive: `docs/local-integration-tests.md:190` attributes a `parity-harness` failure to an older `make e2e`. The parity objects come from an older `make parity`. Commit `22a1fe8`'s Makefile applies them in the `authz-parity` namespace (lines 130-139), not the `authz-e2e` one. The same row then says "then `make e2e`", which a parity user would not run.

Checked, not a finding: `helm-templates/authz-test-stand/README.md:69` uses "waits no longer than", a comparison, not a narration of the change. No other "now", "no longer" or "used to" appears in the changed files.

### Item 2: claimed cases covered

Claimed cases, with the run or file that covers each:
- E2E and parity suite waits take the new variables. Covered by `make -n`, shown above.
- `kubectl logs job/<suite.name>` after `helm test` prints the log. Not run. The Job persists after the hook, so the command should work.
- Remedy `make e2e-down` clears the old objects. Makefile:135-136 deletes the kind cluster. Not run.
- Title claim "let a suite outlast 15 minutes". Not met as shipped. See item 3.

Commands the change tells someone to run:
- `make e2e-down`: the target itself. Covered.
- `make e2e`: CI runs its sub-targets after `helm/kind-action` creates the cluster. Equivalent apart from cluster creation.
- `make e2e-harness`, `make parity-harness`: the same targets run in `.github/workflows/integration-tests.yaml`.
- `helm test authz-test-stand --timeout 15m`: `run-suite` runs the same with `--kube-context` and `-n`, which the README leaves to the current context.
- `kubectl logs job/parity-suite`: `run-suite` runs `kubectl logs -f job/<name>` in the same namespace. The README form runs after the Job ends and still prints the log.

No command line is `none`.

Hunks no sentence claims:
- Substantive: `docs/local-integration-tests.md:191` (the "10-minute wait" row) is reworded and the commit message does not claim it. The new text matches `--timeout 10m` in Makefile:90, so the fact is right. Claim it in the message or move it to its own change.

### Item 3: boundaries, partitions, negative control

Limits on the suite work, and where each is set:
1. Go `-test.timeout 600s`: `test/k8s/test-stand-values.yaml:56` and `helm-templates/authz-test-stand/values.yaml:96`. Inside the Job, fires at 10 minutes.
2. `suite.activeDeadlineSeconds: 900`: `helm-templates/authz-test-stand/values.yaml:99`. No override in `test/k8s`.
3. `helm test --timeout`: `Makefile:51-52` (`E2E_SUITE_TIMEOUT`, `PARITY_SUITE_TIMEOUT`, both 15m), and `helm-templates/authz-test-stand/README.md:65`.
4. CI job `timeout-minutes: 30`: `.github/workflows/integration-tests.yaml:120` (`kind-e2e`) and `:168` (`kind-parity`). Wraps cluster creation, images, harness, install and suite.

Findings:
- **Substantive, limit 1 caps the setting.** Raising `activeDeadlineSeconds` and either timeout variable past 10 minutes has no effect, because the Go test panics at 600s. The commit's title and the Makefile comment both claim otherwise. Request: raise `-test.timeout` with the other two, or derive it from them, and document the set in one place.
- **Substantive, limits 2 and 3 tie at the defaults.** Both are 900s. `README.md:69` says "at least as long as", which allows equality. The inner (Job) limit should fire first so its `DeadlineExceeded` report is the one the reader sees. Equal timers leave the order to a few seconds of scheduling. Request: make the `helm test` wait longer than `activeDeadlineSeconds` by a margin, and say "longer than".
- **Substantive, limit 4 is not documented.** Request: name it in the Makefile comment or the README pair, or state that a suite raised past about 15 minutes also needs the CI job raised.

Pre-existing state: the stale-cluster remedy is documented, not run. The remedy is correct for both the e2e and the parity case, since `kind delete cluster` removes both namespaces. No new setting reaches a consumer that existing users already pass.

### Item 3a: level, placement, environment

None. The change adds no test. The behavior crosses the cluster boundary, so an in-process test is not owed. CI job `kind-e2e` runs `make e2e-suite` with the defaults.

### Item 4: names by content

none. The changed text uses no ordinal or positional reference.

### Item 5: failure report

none. The change adds no assertion.

### Item 6: what the writer says it verified

Not stated. The commit records no run of `make e2e-down` followed by `make e2e` on an old cluster, and no run of the new timeouts. The commit's Helm 4.3.1 and Helm 3.22.1 behavior claims are not backed by any run in the message. This change has no tests, so the evidence would be a run on a stale cluster.

### Item 7: siblings

- `run-suite`: two call sites, `Makefile:115` and `:163`, both updated. `git grep` finds no others.
- Substantive: `test/k8s/README.md:66-68` lists the overrides ("`KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, and `E2E_ARTIFACTS` override the defaults", then `E2E_HELM_ARGS`, `E2E_BASE_URL`, `PARITY_AC_BASE_URL`). It omits `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`.
- Substantive: the parity remedy (item 1) is attributed to the wrong target in `docs/local-integration-tests.md:190`.
- Taste: `test/parity/README.md:39` (the `parity-harness` row) has no pointer to the `make e2e-down` remedy, which `test/k8s/README.md:47-49` covers for both paths.
- `helm test --logs` appears nowhere else in the repo.

### Report

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| Go `-test.timeout 600s` caps the suite at 10 minutes, so raising the other limits does nothing past that; the title claim is unmet | substantive | `test/k8s/test-stand-values.yaml:56`, `helm-templates/authz-test-stand/values.yaml:96` | Raise `-test.timeout` with the other two, or derive it, and document the set |
| `Makefile:49-50` says two limits are enough to run longer, which is false | substantive | `Makefile:49-50` | Correct the comment with the third limit |
| `helm test` wait and Job deadline tie at 900s; "at least as long as" allows equality | substantive | `Makefile:51-52`, `helm-templates/authz-test-stand/README.md:69`, `values.yaml:99` | Make the wait longer than the deadline by a margin; say "longer than" |
| CI job `timeout-minutes: 30` caps the suite and is not documented | substantive | `.github/workflows/integration-tests.yaml:120,168` | Name it in the Makefile or README pair |
| Parity remedy attributed to an older `make e2e`; "then `make e2e`" is the wrong rerun for parity | substantive | `docs/local-integration-tests.md:190` | Name `make parity` for the parity case |
| Unclaimed hunk: the "10-minute wait" row reworded | substantive | `docs/local-integration-tests.md:191` | Claim it in the message or move it to its own change |
| Override list omits the two new timeout variables | substantive | `test/k8s/README.md:66-68` | Add both variables |
| "Run `make e2e-down` once before the first run" can be read as applying to every fresh clone | taste | `test/k8s/README.md:49` | "On such a cluster, run `make e2e-down` once before the first run of the chart" |
| Parity README has no pointer to the remedy | taste | `test/parity/README.md:39` | Add a pointer |

Not checked: no cluster, so the `kubectl logs` output, the stale-cluster remedy, the Helm 4.3.1 "prints nothing" claim and the Helm 3.22.1 claim are unverified. The Go and Helm behavior above comes from local help text and the source of the Makefile and chart, not from a run. The change's prose was not checked for style beyond the item-1 reading.
