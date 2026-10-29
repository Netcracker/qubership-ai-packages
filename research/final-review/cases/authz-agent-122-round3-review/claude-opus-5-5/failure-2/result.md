I checked all nine review comments against the commit. The commit addresses each one in the text, but the new wait loop in `run-suite` still has a case where it runs far past its stated three minutes. I made no file changes or commits.

# Final review: `5dcb6be..f3b64e0` (one commit)

**Inputs.** I had the diff, the commit message, and the review comments you gave. There was no earlier report of this form, so there is no table of earlier findings. The drift script ran without error but listed nothing: the change touches only a Makefile, a Dockerfile, YAML and Markdown, and the script parses none of these. For the docs files I used the no-code analogues from §2a. I loaded `test-authoring` and `english-developer-style` from the given skills directory.

## Item 1: comments consistent with the code and with each other
- **`Makefile:104-109` (`run-suite` comment): finding.** The comment says "`kubectl logs` fails until the Job exists and its container has started, so the loop polls for up to three minutes." That holds only when each `kubectl logs` call fails at once.
  - Once the Job exists but has no Pod, `kubectl logs job/<name>` waits up to `--pod-running-timeout` for a Pod to appear. The default is 20s (`kubectl logs --help`; in kubectl `pkg/polymorphichelpers/helpers.go:58-71`, `GetFirstPod` watches for a Pod until that timeout).
  - So the loop can take 90 × (20s + 2s) = 33 minutes, not three. The message `did not start within 3 minutes` (line 115) is also wrong in that case. Details under Item 3.
- **`Makefile:46-49` (`E2E_HELM_ARGS` comment):** matches lines 93, 99, 100, 164, 168 and 169.
- **`.github/docs-for-publication-task.md:77`:** no longer counts the array.
- **`README.md:59-61`: finding.** "with the test images" reads as every test image. `e2e-images` builds four (`pip-stub`, `tenant-manager`, `authz-runtime-suite`, `authz-parity-suite`), but `.github/docker-dev-config.json` lists only `pip-stub` and `parity-suite`.
- **`helm-templates/authz-test-stand/README.md:62`:** matches inline comment 1.
- **`test/k8s/README.md:66-70` and `docs/local-integration-tests.md:193,196`:** agree with the Makefile defaults (`E2E_SUITE_TIMEOUT ?= 15m`, `PARITY_SUITE_TIMEOUT ?= 15m`).
- No comment narrates the change.

## Item 2: claimed cases covered
| Claimed case | Where it is handled | Run that covers it |
|---|---|---|
| Inline 1: Helm 4.3+ prints nothing, 4.0–4.2 fail | chart README:62 | Docs only; no cluster here to run it |
| Inline 2: suite timeout variables listed | `test/k8s/README.md:69-70`, `docs/local-integration-tests.md:196` | n/a |
| Inline 3: `make parity` remedy | docs:193 | Remedy is `kind delete cluster`; `parity` depends on `e2e-cluster`, so it works |
| No more `--for=create` | Makefile:113 | CI `kind-e2e` and `kind-parity` run the success path on a recent kubectl only |
| A suite that never starts stops after about 3 minutes | Makefile:113-118 | **none** (Item 6) |
| `TEST_STAND_HELM_ARGS` | Makefile:51,93,164 | CI passes neither variable; `make -n e2e-suite` expands and `sh -n` passes |
| Sorted, NUL-separated user files | Dockerfile:43-45 | My local run, below |
| SVT back on 26.0 | compose:3 | Exact reverse of the hunk in 8b85515 (`26.0`, no digest, as before) |
| README "both" and "two-entry" | README:59, publication-task:77 | n/a |
| Docker 23.0, Helm 3.14+, any kubectl or kind | docs:35-42 | **none**: CI pins Helm `v4.3.1` and uses the runner's Docker and kind-action's kubectl |

- **Local run of the jq merge.** I ran the new `find -print0 | sort -z | xargs -0 -r cat | jq --slurpfile users /dev/stdin …` with jq 1.8.2 and BSD tools on copies of `parity-realm.json`:
  - with a file named `b u.json` and a nested `sub/a.json`, the output was `["mt-a-admin","b u","a"]`;
  - with no user files, the realm came out unchanged.
  - The image's busybox `sort -z` and `xargs -0 -r` were not exercised by me; CI's `test-stand-files` step does exercise them. Today `testdata/realm/` holds only `README.md`, so the empty case is the live one.
- **Finding: the version floors have no run.** Nothing runs Docker 23, Helm 3.14 or an older kubectl. I found nothing that needs newer versions:
  - chart functions: `dig`, `sha256sum`, `toYaml`, `required`, `include`;
  - Helm flags: `upgrade --install --create-namespace --wait --timeout`, `test --timeout`;
  - Dockerfiles: `COPY --chmod` with no `# syntax` line, which BuildKit 0.11 (Docker 23) handles.

  So the risk is low, but the floors are inferred, not observed. The title also says "run the test stand on year-old tools", and the message describes no such run (Helm 3.14 is from January 2024).
- **Finding: hunks no sentence of the commit message claims:**
  - `README.md:59-61`;
  - `.github/docs-for-publication-task.md:77`;
  - the ownership-metadata row at `docs/local-integration-tests.md:193`.

## Item 3: boundaries, partitions, and the negative control
**New mechanism, most common fault (`ErrImageNeverPull`).**
- Old: up to 2m in `kubectl wait --for=create`, then the 3-minute loop, then `logs -f` fails, then `wait` sits out `helm test --timeout` (15m).
- New: each attempt fails fast with "waiting to start", so the loop gives up in about 3 to 3.5 minutes and prints `get pods -o wide`, which shows the status. This matches the claim, but it is derived, not run.

**Partition the change misses: the Job exists but no Pod is ever created.** Causes include a restricted Pod Security admission rejection (the case 17b17fc targets), a ResourceQuota, or a missing ServiceAccount.
- Each attempt then blocks for 20s, so the loop runs about 33 minutes.
- `helm test` fails at 15m, but the loop keeps going because it does not watch `helm_pid`.
- CI's `timeout-minutes: 30` kills the job before the loop's message ever prints.
- When it does print, `get pods` shows only "No resources found". The Job's `FailedCreate` event, the one line that explains the failure, is never shown.

**Other limits on the same work:**
- the 20s `--pod-running-timeout` per attempt (inner, from kubectl's default);
- `helm test --timeout` = `E2E_SUITE_TIMEOUT`, 15m;
- `suite.activeDeadlineSeconds` = 900s (`values.yaml:99`);
- CI `timeout-minutes: 30` (`integration-tests.yaml:120,168`).

**Taste:** at the defaults, `activeDeadlineSeconds` (900s, counted from when the Job is created) never fires before `helm test --timeout` (15m, counted from the earlier `helm test` start). So helm's timeout hides the Job's `DeadlineExceeded`. That default pair comes from 5dcb6be; the new docs row at :196 describes the symptom.

**Other partitions:**
- **Pre-existing state:** the docs:193 remedy deletes the cluster, so no inherited state survives it.
- **Values users already pass:** `E2E_HELM_ARGS` no longer reaches the stand. Its documented example `--set IMAGE_PULL_POLICY=Never` is already in both stand values files (line 5), so nothing is lost.

## Item 3a: level, placement, and the environment
None. The behavior exists only in a cluster. The CI `kind-e2e` and `kind-parity` jobs run `make e2e-suite`, `make parity-suite` and (through `*-harness`) `test-stand-files`. The CI `chart` job lints both stand values files.

## Item 4: names by content, not by position
None. I checked the new Makefile comment, the message text, the docs rows and the README sentences.

## Item 5: the failure report
Analogue used: what the new failure prints.
- Covered by the Item 3 finding: when no Pod exists, the output omits the Job's events.
- **Taste:** if `helm test` itself exits at once (for example, the release is not installed), the loop still polls for 3 minutes. It then says the container "did not start", which misleads, and `kill` then fails on a pid that has already exited.
- **Taste:** the new message is not quoted in the docs troubleshooting table (row at :192).

## Item 6: what the writer says it verified
No evidence is stated:
- no run of `ErrImageNeverPull` with its duration and output;
- no run on kubectl older than 1.31;
- no build twice to show `checksum/realms` stays stable;
- no run on Docker 23 or Helm 3.14.

## Item 7: siblings of the change
- `run-suite` serves both `e2e-suite` and `parity-suite`, so the fix covers both.
- Both harness targets moved to `TEST_STAND_HELM_ARGS`.
- `git grep` finds no other `--for=create` or `$(find …)`.
- The lists of override variables: `test/k8s/README.md` names all of them. The workflow names only `KIND_CLUSTER`. The docs page has no list of override variables.
- Old counts: "both" and "two-entry" are fixed; no other count of the components remains.
- Helm 3 and 4 are both named in the chart README.

## Findings
| Finding | Label | File:line | Request |
|---|---|---|---|
| Loop runs about 33 min, not 3, when the Job exists but no Pod is created; it outlasts helm's 15m and CI's 30m and does not print the `FailedCreate` event | Substantive | `Makefile:104-118` | Pass `--pod-running-timeout=2s` to the polling `kubectl logs` (or bound the loop by elapsed time and stop it when `helm_pid` exits); print `describe job` or the events too |
| The never-starts path has no run | Substantive | `Makefile:113-118` | Run `ErrImageNeverPull` and the no-Pod case; state the durations and the output |
| Docker 23.0 and Helm 3.14 floors, "any kubectl", and the title's "year-old tools" have no run | Substantive | `docs/local-integration-tests.md:35-42`, commit title | Run `make e2e` on those versions, or say the floors are inferred and untested |
| Hunks no sentence of the message claims | Substantive | `README.md:59`, `.github/docs-for-publication-task.md:77`, `docs/local-integration-tests.md:193` | Add a sentence to the commit message for each |
| "the test images" reads as all four; CI builds two | Substantive | `README.md:59` | Name `pip-stub` and `parity-suite` |
| Helm's 15m timeout hides `activeDeadlineSeconds` 900s at the defaults (pair set in 5dcb6be) | Taste | `Makefile:54`, `values.yaml:99` | Derive one from the other, or give helm a margin |
| "did not start" is printed when `helm test` itself failed early | Taste | `Makefile:113-117` | Check `kill -0 $helm_pid` inside the loop |
| New message not in the troubleshooting table | Taste | `docs/local-integration-tests.md:192` | Quote it in the `ErrImageNeverPull` row |

I did not run the kind suites (no cluster), the Docker build of `chart-files` with busybox, or any Helm 3.x or Docker 23 binary, and I did not do a style pass over the prose.
