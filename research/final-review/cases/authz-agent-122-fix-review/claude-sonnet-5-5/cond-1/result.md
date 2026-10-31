# Final review: `17b17fc..HEAD` (5dcb6be)

**Inputs.** The change has four files: `Makefile`, two Markdown pages and a chart README. The commit message and the three review comments are the task statement.
- The drift script printed nothing, because the change has no code in a language it parses. I read the Makefile comments by hand.
- I loaded `english-developer-style` and read it in full. I did not load `test-authoring`, because the change adds no tests.
- I used the "change with no code" analogues (§2a) for the pages and the Makefile.
- I ran `make -n e2e-suite` and `make -n parity-suite` with `E2E_SUITE_TIMEOUT=40m PARITY_SUITE_TIMEOUT=40m`. Each `helm test` line takes its own timeout, so the three comments are covered. The targets pass their own variables, and the namespaces and Job names are correct.
- I ran no cluster, no `helm template` and no `helm lint`.

## Item 1: comments consistent with the code and with each other

Analogue: every statement the changed files make about each other.

**Finding 1 (substantive), `Makefile:49-52` and `Makefile:103-104`.** The new comments say a longer suite "raises this together with suite.activeDeadlineSeconds in its values". The comment at `Makefile:104` says "no shorter than its suite.activeDeadlineSeconds". Those two limits are not the whole set:
- The chart's default `suite.args` and `test/k8s/test-stand-values.yaml:55` pass `-test.timeout 600s` to the Go binary.
- That inner limit is below the 900 s deadline at the defaults, so it fires first (item 3).

A reader who follows the comment and raises only those two values still gets a suite killed at 10 minutes. The request is to name `-test.timeout` in `suite.args` as the third value, or to derive it.

**Finding 2 (substantive), `docs/local-integration-tests.md:190`.** The row names two symptoms, `make e2e-harness` and `make parity-harness`. Its action says "Run `make e2e-down` once, then `make e2e`". After a parity failure that does not run the parity stand. The row at `local-integration-tests.md:176` and `test/k8s/README.md:49` ("older `make e2e` or `make parity`") do name both. The request is "then `make e2e` or `make parity`".

**Finding 3 (taste), `helm-templates/authz-test-stand/README.md:61-62`.** The step says "Helm 4 prints nothing … Helm 3 fails with `unable to get pod logs`". The commit message gives the versions (Helm 4.3.1, Helm 3.22.1) and quotes the full error. I did not run either Helm version. I only checked that the README is consistent with the commit message. The shorter form is acceptable.

Other comments checked and consistent:
- The `suite.yaml` comment ("keeps it afterwards so its log stays readable") makes the new `kubectl logs job/parity-suite` valid, because the Job is not deleted after success.
- The "10-minute wait" in the docs row matches `--timeout 10m` at `Makefile:90`.

## Item 2: claimed cases covered

Analogue: each claim in the comments and the commit message, with the target or page that makes it true. There are no tests.

| Claimed case | Covered by |
| --- | --- |
| `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` set the wait, default 15m | `Makefile:51-52`, `e2e-suite` and `parity-suite` pass `$(4)`. `make -n` confirms both defaults and an override. |
| Chart README: `kubectl logs job/<suite.name>` after `helm test` | `README.md:65-66`. Its Job name is hard-coded as `parity-suite`; see item 7. |
| Old stand needs `make e2e-down` once | `test/k8s/README.md:47-49`, `local-integration-tests.md:190` |

Commands the change tells someone to run:
- `helm test authz-test-stand --timeout 15m` followed by `kubectl logs job/parity-suite`. The same shape runs in `run-suite` (`make e2e-suite` and `make parity-suite`), with `-n`, `--kube-context` and `logs -f`. The README form without `-n` runs against the user's current namespace; see item 7.
- `make e2e-down`. This target exists and deletes the cluster, so both namespaces go.

The Helm 4 and Helm 3 behavior of `--logs` rests on the commit message. I have no cluster to confirm it.

Hunks beyond the claim: none that need a claim. The rewritten "10-minute wait" row fixes a stale `rollout status deploy/keycloak`. The commit message does not mention it, but it is a docs correction, so I do not report it.

## Item 3: boundaries, partitions, and the negative control

Analogue: configuration and script. Each question applies as written.

**Pre-existing state.** Remedy: the change documents `make e2e-down` and does not remove the old objects. That is one of the two options in comment 1 and is acceptable. No run starts from an older stand, so the remedy is unverified, and nothing detects the symptom early. Both pages say the install "fails", and Helm's error text is quoted verbatim.

**Other limits on the same work.** I list them below with where each is set.

| Limit | Where set | Value |
| --- | --- | --- |
| `helm test --timeout` | `Makefile` (`E2E_SUITE_TIMEOUT`, `PARITY_SUITE_TIMEOUT`) | 15m |
| Job `activeDeadlineSeconds` | chart `values.yaml:99` | 900 |
| Go `-test.timeout` | `values.yaml` `suite.args` (parity default), `test/k8s/test-stand-values.yaml:55` | 600s |
| CI job `kind-e2e` | `.github/workflows/integration-tests.yaml:120` | 30 min |
| CI job for parity | `integration-tests.yaml:168` | 30 min |
| `kubectl wait` and log polling | `run-suite` | 2m + 3m; these sit inside the helm test window, not outside it |

I raised each setting just past the other limits.
- **Finding 4 (substantive), `Makefile:49-52`.** With `E2E_SUITE_TIMEOUT=40m` and `activeDeadlineSeconds: 2400`, the Go `-test.timeout 600s` still kills the suite at 10 minutes. Raised past 30 minutes, the CI job's `timeout-minutes: 30` cancels the run first, which cancels everything including log collection. The inner limit already fires first at the defaults. The request is to derive the Go timeout from the deadline, or to tell the reader to raise all three limits together. The CI cap needs its own note.
- **Finding 5 (taste).** At the defaults `--timeout 15m` equals `activeDeadlineSeconds: 900`. The new comment says "no shorter than". With equality, helm may report its own timeout before the Job reports `DeadlineExceeded`, and the failure text reads less clearly. A few seconds of margin in the default is my preference. Decline freely.

**Negative control.** No test, so the control is that the defaults stay 15m. `make -n` shows the unchanged `--timeout 15m` for both targets, so the default behavior is unchanged.

Added instructions: this change adds no skill or instruction file, so there is no table.

## Item 3a: level, placement, and the environment

Analogue: where each statement lives.
- The Make variables sit beside the other E2E variables.
- The pre-existing-state remedy is in the troubleshooting table and in `test/k8s/README.md`, both pages comment 1 named.
- The chart README holds the chart-level fix.

None.

## Item 4: names by content, not by position

None. Headings and cross-references use names (`suite.name`, `make e2e-down`). Step "3." of the chart README is in an existing numbered procedure.

## Item 5: the failure report

Analogue: what a failure tells the reader.
- The error text is quoted exactly in all three places: `exists and cannot be imported into the current release: invalid ownership metadata`.
- The `unable to get pod logs` text is a prefix of the full message, not the whole line. That is fine as a search string.

None.

## Item 6: what the writer says it verified

The commit message states no run: no red run on the base commit and no run of the new targets on a cluster.
- The Helm 4.3.1 and Helm 3.22.1 behavior of `--logs` is stated as fact and never shown in a run.
- The `exists and cannot be imported` failure is likewise quoted without a recorded reproduction.

I did not run the suite, as the form says. The evidence is the writer's to state.

## Item 7: siblings of the change

**Adds a member to a set.** The new variables sit beside `E2E_HELM_ARGS`, `E2E_BASE_URL` and `PARITY_AC_BASE_URL`. A search for those names outside the `Makefile` found nothing that lists them (my grep command failed on one pattern, then returned only `Makefile` hits and the two docs rows). No page has a table of overrides, so none is owed. The old size of the set appears nowhere in prose.

**Helper: `run-suite`.** It has two call sites, `e2e-suite` and `parity-suite`, and the change updates both.

**Symptom: the ownership error.** The symptom names two targets and the action names `make e2e-down`, which covers both. The wording gap is finding 2. Other paths that show the symptom:
- Other namespaces and releases that an older run created are removed with the cluster.
- Any cluster created with a custom `KIND_CLUSTER` is reached by `make e2e-down` only with the same `KIND_CLUSTER`. The pages do not say so. This is a taste-level gap.

**Symptom: `--logs`.** **Finding 6 (substantive), `helm-templates/authz-test-stand/README.md:65-66`.** The command is `kubectl logs job/parity-suite`, with no `-n`, no `--context`, and a hard-coded name. The step says the Job is named by `suite.name`, but the example gives the default only.
- A reader whose current context namespace is not the release namespace gets `NotFound`.
- The README's `helm test` line also has no `-n`. The two lines are consistent with each other, but a reader who installs with `-n <ns>` must add it to both.

The request is to write `kubectl logs job/<suite.name>` with `-n <namespace>`, or a sentence saying both commands take the release namespace. The `<suite.name>` form is what comment 2 proposed.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Comment names two limits, but the Go `-test.timeout 600s` in `suite.args` fires first | Substantive | `Makefile:49-52`, `Makefile:103-104` | 1 |
| Troubleshooting row names `make parity-harness` but its action ends in `make e2e` | Substantive | `docs/local-integration-tests.md:190` | 1 |
| A raised deadline is cut off by the 600 s Go timeout and by the 30-minute CI jobs | Substantive | `Makefile:49-52`, `.github/workflows/integration-tests.yaml:120,168` | 3 |
| `kubectl logs job/parity-suite` has no namespace and hard-codes the name | Substantive | `helm-templates/authz-test-stand/README.md:65-66` | 7 |
| Helm version behavior stated tersely in the README | Taste | `helm-templates/authz-test-stand/README.md:61-62` | 1 |
| Helm timeout equals the Job deadline at the defaults | Taste | `Makefile:51-52` | 3 |

Not done: no cluster, so the Helm 3 and Helm 4 `--logs` behavior and the ownership failure are checked against the commit message only. I ran no test and no mutation, and no previous report exists.
