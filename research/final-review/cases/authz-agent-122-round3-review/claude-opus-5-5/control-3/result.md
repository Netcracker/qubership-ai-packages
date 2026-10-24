I've finished the review and changed no files. The commit answers most of the review round, but three new problems remain and none of the version claims has a run behind it.

**What I ran:**
- **Merge step:** I built the realm-file merge step of `build/authz-agent-transfer/Dockerfile` at the base and at HEAD. With the repository's files the output is byte-identical. With sample user files added (`b.json`, `sub/a.json`, `with space.json`), the base build fails on the file name with a space. HEAD merges the three in byte order.
- **Stub run:** I ran `make e2e-suite` with stand-in `helm`, `kubectl` and `sleep` commands, since there is no cluster.

Nothing ran against a cluster.

**Previous report:** none was handed over, so there is no status table.

**Drift script:** it printed nothing because the change has no code members (a Makefile, a Dockerfile, Markdown and YAML), so every item below uses the no-code reading of the form.

### Item 1: comments consistent with the code and with each other
- The Makefile comments on `E2E_HELM_ARGS`/`TEST_STAND_HELM_ARGS` match lines 93, 99–100, 164 and 168–169. The product charts do read `IMAGE_PULL_POLICY`.
- The `run-suite` comment (Makefile:102–108) holds when `helm test` creates the Job. It is false when `helm test` fails before creating it: the comment says "prints the Pod and stops helm test", but there is no Pod and no running `helm test` (filed under Item 3).
- The new row in `docs/local-integration-tests.md:196`, "fails after 15 minutes while the Job still runs", is wrong. After `helm test` times out, the foreground `kubectl logs -f` keeps the target running until the container exits. So the target fails when the Job ends, after the suite's verdict is in the log, and not at 15 minutes.
- `README.md:59–60` says "with the test images", but `.github/docker-dev-config.json` lists only two of the four test images `e2e-images` builds: pip-stub and parity-suite. tenant-manager and runtime-suite are missing.
- `README.md:60` also says CI "publishes the two services". Nothing in the repository shows what the shared `docker-build.yaml` publishes for the other three components, and no workflow here references `docker-dev-config.json`.
- `.github/docs-for-publication-task.md:77`, "The component array", is consistent.

### Item 2: claimed cases covered
| Claim | Covered by | Outcome |
| --- | --- | --- |
| Comment 1: Helm 4.3+ prints nothing; 4.0–4.2 and Helm 3 fail | chart `README.md:61–62` | Text matches the comment; no run, no cluster |
| Comment 2: suite timeout variables listed | `test/k8s/README.md:69–70`, `docs/local-integration-tests.md:196` | Covered, but the docs row's symptom is wrong (Item 1) |
| Comment 3: remedy covers `make parity` | `docs/local-integration-tests.md:193` | Holds: the base Makefile at `b7064c7`, lines 129–148, shows `parity-harness` used `kubectl apply`, and `e2e-down` deletes the whole cluster |
| `kubectl wait --for=create` replaced; works "on any kubectl" | Makefile:113 | `kubectl logs job/<name>` is an old feature, but nothing runs on kubectl older than 1.31; CI uses kind-action's kubectl |
| Suite that never starts fails after about 3 minutes with the quoted message | Makefile:114–118 | Stub run: when `helm test` hangs, it prints the message and exits 1 (`make` rc 2). When `helm test` fails at once, the false message below |
| `E2E_HELM_ARGS` no longer reaches the stand; `TEST_STAND_HELM_ARGS` does | Makefile:93, 164 | Holds by reading |
| `find` order and file names with spaces | Dockerfile:43–45 | My builds above confirm it |
| SVT back on Keycloak 26.0 | `docker-compose.yml:3` | Identical to the line at `b7064c7` |
| Docker 23.0 and Helm 3.14 named | `docs/local-integration-tests.md:35–43` | No run on either. CI pins only Helm v4.3.1, and nothing in the change says which feature sets 3.14 as the minimum |

Commands the change documents:
- `make e2e-down` then `make e2e` or `make parity`: no run from the old state.
- `make parity-suite PARITY_SUITE_TIMEOUT=5h30m`: no run.
- `helm test` / `kubectl logs job/parity-suite` in the chart README (unchanged block): no run.

For each, the outcome depends on the tool version, and the change runs only Helm 4.3.1 and a kubectl of 1.31 or later.

Hunks no sentence of the commit message claims: `README.md:59–60` and `.github/docs-for-publication-task.md:77`.

### Item 3: boundaries, partitions, and the negative control
- **False message when `helm test` fails at once.** I stubbed `helm` to fail immediately with `Error: release: not found`. The loop still polls for the full 3 minutes. It then prints "The runtime-suite container did not start within 3 minutes:", then "No resources found", then `kill: … No such process`. The base printed no such message.
  - The same happens when `E2E_SUITE_TIMEOUT` is set under 3 minutes, which is the boundary just past the new limit.
- **Limits on the same work:**
  - the 3-minute start loop, fixed in Makefile:113;
  - `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT`, documented, 15m;
  - `suite.activeDeadlineSeconds` in `values.yaml:99`, 900s;
  - CI `timeout-minutes: 30` in `integration-tests.yaml:120` and `:168`.
- **How those limits interact:**
  - The start loop fires first at the defaults, which is correct.
  - At the defaults, helm's 15m and the Job's 900s are equal, and `helm test` starts first. So helm's timeout fires a little before the Job's `DeadlineExceeded` and hides that report. This predates the change, but the new row documents the pair.
- **What `E2E_HELM_ARGS` now reaches:** its documented example (`--set IMAGE_PULL_POLICY=Never`) still means the same thing to the product charts. That stand values no longer get through is stated under User-visible.
- **State left by earlier versions:**
  - A Job left by the kill path is deleted at the next run (Makefile:111).
  - The sort can change `checksum/realms` once, which restarts Keycloak once. That is harmless, and the repository has no user files today.

### Item 3a: level, placement, and the environment
- No CI job runs the lower versions the docs now promise: Helm 3.14, kubectl older than 1.31, Docker 23.0.
- No job and no stated run exercises the start-timeout path.
- `kind`/`kubectl` "any version that supports the cluster" is a claim with no check behind it.

### Item 4: names by content, not by position
None. The new text names variables, targets and versions by name; "the three" at `test/k8s/README.md:64` is unchanged.

### Item 5: the failure report
- The new message names the Job and lists the Pod with `-o wide`, which shows `ErrImageNeverPull`. That is good.
- When no Pod exists, the report blames a container that was never created and adds a `kill` error (Item 3).

### Item 6: what the writer says it verified
The commit states no run of any kind:
- none on old kubectl or Helm 3.14;
- none of the ErrImageNeverPull path;
- none of the Dockerfile change;
- none of the SVT stack.

My Docker builds and stub runs are consistency checks, not the writer's evidence.

### Item 7: siblings of the change
- `git grep` finds no other `--for=create` and no other unquoted `$(find …)` outside the archived handover docs.
- `TEST_STAND_HELM_ARGS` is listed everywhere `E2E_HELM_ARGS` is: the Makefile and `test/k8s/README.md`.
- The old counts ("both", "two-entry") are gone. "Besides the two services" at `README.md:66` is still correct.
- The e2e and parity twins both get the fix through `run-suite` and both installs.

### Findings
| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| When `helm test` fails before creating the Job, the target polls for 3 minutes and then blames a container that doesn't exist | Substantive | `Makefile:113–118` | Break out of the loop when `helm test` has exited (`kill -0 $$helm_pid \|\| break`) and pass on its exit status; only print the "did not start" message while `helm test` is still running |
| The troubleshooting row says the target "fails after 15 minutes while the Job still runs"; it actually fails when the Job ends, after the log shows the result | Substantive | `docs/local-integration-tests.md:196` | Describe the real symptom: the log runs to the end, then the target fails with helm's timeout error |
| Docker 23.0, Helm 3.14, any kubectl, and the `kubectl logs` loop on kubectl older than 1.31 have no run; the reason for 3.14 isn't stated | Substantive | `docs/local-integration-tests.md:35–43`; Makefile:113 | Run `make e2e` with Helm 3.14 and kubectl 1.30 (or add a CI matrix entry), or name only the versions CI runs |
| The start-timeout path and the Dockerfile change have no stated run | Substantive | Commit message | State the run, for example `make e2e-suite` after removing a loaded image, and the sorted merge of sample files |
| The `README.md` and `.github/docs-for-publication-task.md` hunks aren't claimed by the commit message | Substantive | `README.md:59`; `.github/docs-for-publication-task.md:77` | Add a sentence for them to the commit message |
| "the test images" covers only pip-stub and parity-suite; "publishes the two services" is unsupported for the other three components | Substantive | `README.md:59–60` | Name the two test images; say what the shared workflow does with the other components, or drop "the two services" |
| At the defaults, helm's 15m timeout fires a few seconds before the Job's 900s deadline and hides its report | Taste (predates this change) | `Makefile:55`; chart `values.yaml:99` | Make the default helm timeout a little longer than the deadline, or document the pair |
| The new "did not start within 3 minutes" message has no troubleshooting row | Taste | `docs/local-integration-tests.md:192` | Add the message text to the `ErrImageNeverPull` row |

I did not run any suite against a cluster, and I did not check the commit against old tool versions. I did not run markdownlint, and I did not read the prose for style alone.
