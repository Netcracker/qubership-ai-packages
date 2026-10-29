# Final review: `5dcb6be..f3b64e0`, one commit

This is the first round, so there is no previous report to reconcile. The change has no Go code: it touches the Makefile, a Dockerfile, a Compose file and Markdown. I used the §2a analogues where the code items don't fit. The drift script ran (`comment-drift.py 5dcb6be HEAD`) and printed nothing, because it does not parse Makefile, Dockerfile or Markdown, so I compared the comments by hand.

## Item 1: comments consistent with the code and with each other
Analogue: the comments above changed recipes, plus what each changed page says about other files.

- **`Makefile:102`**: this comment sits above the rewritten `run-suite` and nobody edited it. It says "`helm test` … prints the log only at the end, so the log is streamed while it runs". `helm test` without `--logs` prints no suite log at all. The chart README line 61 edited in this same commit says that even `--logs` prints nothing for a Job, or fails. A reader gets the wrong reason for the streaming loop. **Substantive.**
- `Makefile:46-49` (`E2E_HELM_ARGS` / `TEST_STAND_HELM_ARGS`), `Makefile:103-106` (the polling loop) and `test/k8s/README.md:67-70` all match the recipes.
- `helm-templates/authz-test-stand/README.md:62` now matches inline comment 1: 4.3 and later print nothing, earlier releases fail.
- `.github/docs-for-publication-task.md:77`: "The component array" no longer counts the components. Correct.
- **`README.md:59`**: "with the test images and the transfer image". CI's `.github/docker-dev-config.json` builds only two test images, pip-stub and parity-suite. The repository has four (`Makefile:74-77` also builds tenant-manager and authz-runtime-suite). A reader would expect CI to build all four. **Substantive (minor).** Fix: name the two images.
- No comment narrates the change ("now", "no longer").

## Item 2: claimed cases covered
Claimed cases come from the 3 inline comments, the 6 general comments and the commit message.

| Claim | Where it is handled | Run that covers it |
|---|---|---|
| Comment 1: Helm 4.0–4.2 vs 4.3 | chart README:62 | none (wording only) |
| Comment 2: timeout variables listed | test/k8s/README:69-70, docs:196 | n/a |
| Comment 3: `make parity` after `e2e-down` | docs:193 | none. `e2e-down` deletes the cluster (`Makefile:142`), so rerunning `make parity` is correct by reading. |
| `kubectl wait --for=create` removed; works on any kubectl | `Makefile:112` | **none**. CI uses the runner's kubectl. |
| Pod that never starts stops after about 3 min | `Makefile:112-118` | **none**. No run with `ErrImageNeverPull` is stated. |
| Merge order is deterministic; file names with spaces work | `Dockerfile:43-45` | I checked it myself: busybox `find -print0 \| sort -z \| xargs -0 -r cat` in `alpine:3.22` sorts `a b.json`, `b.json`, `empty.json`, `sub/c.json`, and an empty directory exits 0. `jq --slurpfile users /dev/stdin` merges into the realm in that order. `docker build --target chart-files` at base and at head gives byte-identical output. |
| `E2E_HELM_ARGS` no longer reaches the stand | `Makefile:93,164` | `make -n` shows `$(TEST_STAND_HELM_ARGS)` in both harness recipes |
| SVT back on Keycloak 26.0 | compose:3 | Identical to the line before 8b85515 (`git log -p`), so it is a plain revert |
| `README.md` "both" and the "two-entry array" | README:59, docs-for-publication:77 | see item 1 |

**Commands and version claims in the changed files:**

1. **`docs/local-integration-tests.md:38,41-42`** claims "helm 3.14 or later; Helm 4 works too", Docker 23.0+, and "kubectl and kind may be any version that supports the cluster". The commit title says "run the test stand on year-old tools". **Run: none.** Both kind jobs pin `azure/setup-helm` to `v4.3.1` (`integration-tests.yaml:131,177`), and kubectl is whatever the runner ships.
   - The outcome depends on how `helm upgrade --install --wait` treats the stand's Deployments: Helm 3 uses the legacy waiter, Helm 4 uses the kstatus watcher. It also depends on `helm test` running a Job hook on 3.14 and on 4.0–4.2.
   - Nothing the targets use needs 3.14 specifically, so the floor's reason is not stated anywhere.
   - **Substantive.** Request either a CI leg or a recorded local run on Helm v3.14.x, v4.0.x and kubectl 1.30, or narrow the table to the versions CI runs.
2. **`docs/local-integration-tests.md:196`**: `make parity-suite PARITY_SUITE_TIMEOUT=5h30m`. **Run: none.**
   - The outcome depends on `suite.activeDeadlineSeconds`, which defaults to 900 (`values.yaml:99`). That value is rendered into the hook Job at `parity-harness` time. `helm test` uses the stored release, so editing the values and running only `parity-suite` keeps 900.
   - The Job is then killed at 15 minutes whatever the timeout says. The row says "raise it together with `suite.activeDeadlineSeconds` in the values" but never says the harness has to be reinstalled.
   - `test/k8s/README.md:71-74` states this rule for `E2E_BASE_URL`, but not for the deadline. **Substantive.** Request: name `make parity-harness` (or `e2e-harness`) before the suite run in this row.
3. **Reverse check:** every hunk is claimed by a sentence of the commit message. None is left unclaimed.

## Item 3: boundaries, partitions, and the negative control
- **Pre-existing state:**
  - The Dockerfile change produces identical output on the current tree, so `checksum/realms` does not change and Keycloak is not restarted on an existing stand.
  - `test/parity/suite/testdata/realm/` holds only `README.md`, so the repository exercises only the empty-user partition. I checked the non-empty partition by hand, as described in item 2.
- **Values users already pass:**
  - `E2E_HELM_ARGS='--set IMAGE_PULL_POLICY=Never'`, the documented example, no longer reaches the stand. That is harmless, because both stand values files already set `Never`.
  - Any stand-only `--set` someone passed in `E2E_HELM_ARGS` is now dropped silently. The commit's "User-visible" lines say so.
- **Limits on the same work (the suite run):**
  - The startup window: 90 × (2 s sleep + one `kubectl logs` call), so actually ≥3 min. It is fixed in the Makefile.
  - `helm test --timeout` = `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT`, 15m by default, a documented setting.
  - The Job's `activeDeadlineSeconds`, 900 s by default.
  - CI's `timeout-minutes: 30`.
- **The startup window has no exit when `helm test` itself fails fast.** For example, with no release installed, helm exits at once. The loop still polls for 3 minutes, then prints "The … container did not start within 3 minutes" over an empty Pod list. That message is false, because no Job ever existed.
  - At `E2E_SUITE_TIMEOUT` below 3m, the same thing happens after helm's timeout.
  - **Substantive.** Request: end the loop when helm has exited (`kill -0 $$helm_pid || break`) and fall through to `wait $$helm_pid`.
- **Two limits that fire together at the defaults:** helm's 15m and the Job's 900 s are equal, and helm's clock starts first. So helm's timeout always fires first and hides the Job's `DeadlineExceeded` report.
  - Comment `Makefile:108-109` asks only for "no shorter than", and the new docs row documents this case.
  - The defaults came in 5dcb6be, but this commit adds the documentation for them. **Substantive.** Request: derive the helm timeout from the deadline plus the startup window, or set both in one place.
- **CI's 30-minute job limit:** the suite's 15m plus the harness's 10m wait and two 5m installs adds up to more than 30m. That was there before this commit; I'm noting it, not filing it.

## Item 3a: level, placement, and the environment
Analogue: the repository's own gates. `test/scripts/test-chart-render.sh` passes on Helm 4.3.0. Markdown lines are within the MD013 limit of 400. No CI job runs the Helm/kubectl range or the docker version range the docs claim (see item 2).

## Item 4: names by content, not by position
none. The new headings, the row text and the message name things by content.

## Item 5: the failure report
Analogue: what the new failure path tells the reader.
- The never-starts path prints the Job name and `get pods -o wide`, which shows the reason, for example `ErrImageNeverPull`. Good.
- The helm-fails-fast case in item 3 prints a false cause.
- The target tables (`test/k8s/README.md:59`, `docs/local-integration-tests.md:109`, `test/parity/README.md:41`) don't mention the 3-minute stop. The `ErrImageNeverPull` row (docs:192) doesn't quote the new message. **Taste.**

## Item 6: what the writer says it verified
None stated. The commit message gives no run of:
- `make e2e-suite` with a missing image;
- Helm 3.14, 4.0–4.2, or kubectl older than 1.31;
- the Dockerfile with user files present;
- the SVT stack after the revert.

## Item 7: siblings of the change
- `run-suite` is shared by `e2e-suite` and `parity-suite`, so the fix covers both.
- Both harness recipes switched to `TEST_STAND_HELM_ARGS`. Both install recipes keep `E2E_HELM_ARGS`.
- **New variable `TEST_STAND_HELM_ARGS`:** the only list of overrides is `test/k8s/README.md`, and it names the new variable. CI passes neither variable. `docs/local-integration-tests.md` has no list of overrides.
- **Old set size:** I searched the prose for "both" and "two". README:59 and docs-for-publication:77 are updated, and the other hits are unrelated ADR prose. `.qubership/docker.cfg` is the release list and counts nothing.
- **Comment 1's fix in other places:** comment 1 asked only about the chart README. No other page states Helm 4 behavior, apart from the false `Makefile:102` sentence in item 1.

## Findings

| # | Finding | Label | Location | Change requested |
|---|---|---|---|---|
| 1 | Version floors (Helm 3.14, Helm 4.0–4.2, any kubectl, Docker 23.0) claimed with no run; CI runs only Helm v4.3.1 | Substantive | `docs/local-integration-tests.md:35-42` | A CI leg or recorded run on Helm 3.14.x, 4.0.x, kubectl 1.30; or narrow the claim to what runs |
| 2 | Timeout row's remedy leaves out the harness reinstall that `activeDeadlineSeconds` needs; the example command alone still dies at 900 s | Substantive | `docs/local-integration-tests.md:196` | Say to rerun `make e2e-harness`/`parity-harness` after raising the deadline |
| 3 | Startup loop ignores an early `helm test` exit and then reports "container did not start" | Substantive | `Makefile:112-118` | Break the loop when `helm_pid` has exited; fall through to `wait` |
| 4 | Helm timeout equals the Job deadline at the defaults, so helm's timeout hides the Job's own failure report | Substantive | `Makefile:54-55,108-109`; `values.yaml:99` | Derive one limit from the other (deadline + startup window), or document the pair |
| 5 | "It prints the log only at the end" is false for `helm test` without `--logs` | Substantive | `Makefile:102` | State that `helm test` prints no Job log |
| 6 | "the test images" suggests CI builds all four; it builds pip-stub and parity-suite | Substantive (minor) | `README.md:59` | Name the two images |
| 7 | Target tables and the `ErrImageNeverPull` row don't mention the 3-minute stop or its message | Taste | `test/k8s/README.md:59`, `docs/local-integration-tests.md:109,192`, `test/parity/README.md:41` | Optional: quote the message in the troubleshooting row |
| 8 | "within 3 minutes" is at least 3 minutes, because each iteration also runs a `kubectl` call | Taste | `Makefile:115` | Optional: loop on elapsed time |

Not checked: no target ran against a cluster, since there is none. I did not run the SVT stack, Helm 3.x, Helm 4.0–4.2, or Docker 23. I did not do a style-only pass over the prose.
