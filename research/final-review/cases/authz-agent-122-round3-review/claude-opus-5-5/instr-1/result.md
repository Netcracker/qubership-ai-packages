I found six problems that need fixing and two smaller wording points. The commit answers every review comment. The worst gap is in the new `run-suite` loop: when the suite Job's Pod is never created, the 3-minute stop does not fire.

**Inputs.** The diff of `5dcb6be..f3b64e0` (8 files), the commit message, and the review comments above. No earlier report of this form exists, so there is no follow-up table. I ran `comment-drift.py 5dcb6be HEAD` and it printed nothing, because the change is a Makefile, a Dockerfile, Compose YAML and Markdown, which it does not parse. I loaded `english-developer-style` as the wording skill. `docs-page-authoring` is not among the provided skills, so I did not load it. There is no source code here, so each item below uses the §2a equivalent.

## Item 1: comments consistent with the code and with each other

The equivalent used: what each changed file says about the Makefile, CI and the charts.

- **`Makefile:102-107`** matches the new loop, and the `E2E_HELM_ARGS` comment at `Makefile:46-49` matches both install targets.
- **README files.** `test/k8s/README.md:66-70` and `helm-templates/authz-test-stand/README.md:62` are both correct.
  - The 4.3 split agrees with CI, which pins Helm `v4.3.1`.
  - The `TAG` and `IMAGE_PULL_POLICY` claim matches `values.yaml:12-13` and the templates.
- **Finding, `docs/local-integration-tests.md:196`.** The row says the target "fails after 15 minutes while the Job still runs". It does not.
  - At 15 minutes `helm test` prints its timeout and exits.
  - But `$(1) logs -f job/$(3)` (`Makefile:119`) keeps streaming until the Job's container ends, and only then does `wait $$helm_pid` fail the target.
  - So the target fails when the Job ends, at `activeDeadlineSeconds`. A reader watching for an exit at 15 minutes sees the log still running.
- **Finding, `README.md:59-60`.** "with the test images" reads as all of them.
  - `docker-dev-config.json` lists only two of the four test images: `pip-stub` and `parity-suite`.
  - `authz-runtime-suite` and `tenant-manager` are not built by CI.
- **Checked, no finding.** `.github/docs-for-publication-task.md:77` no longer counts the components.

## Item 2: claimed cases covered

| Claimed case | Where it is handled | Run or check behind it |
| --- | --- | --- |
| Inline 1: Helm 4.3+ prints nothing; earlier releases fail | `authz-test-stand/README.md:62` | CI uses v4.3.1. The pre-4.3 behavior comes from the review comment. |
| Inline 2: suite timeouts listed in `test/k8s/README.md` and the docs | `test/k8s/README.md:69-70`, docs row `:196` | Text only. The `:196` row is wrong (item 1). |
| Inline 3: the `make parity` remedy | docs `:193` | The old `parity-harness` (4050c9b `Makefile:129-135`) did use `kubectl apply`, and `e2e-down` deletes the whole cluster. The row is correct. |
| `--for=create` removed; the loop works on any kubectl | `Makefile:113` | No `--for=create` is left in the repository. **No run on kubectl older than 1.31.** |
| Stop after about 3 minutes on `ErrImageNeverPull` | `Makefile:113-118` | **No run of this fault is stated.** |
| `TEST_STAND_HELM_ARGS` | `Makefile:51, 93, 164` | `make -n` level only. CI passes neither variable. |
| Dockerfile: sorted, NUL-separated, a name with a space | `Dockerfile:43-45` | I ran the same pipeline locally with BSD `sort` and jq 1.x (see the evidence below). **No run on the build image's Alpine/BusyBox tools.** |
| SVT Keycloak back to 26.0 | `docker-compose.yml:3` | Matches the base (`b7064c7` and `58316ca` both have `keycloak:26.0`). |
| README and publication doc counts | `README.md:59`, `.github/docs-for-publication-task.md:77` | See item 1. |
| Docs name Docker 23.0+ and Helm 3.14+ | docs `:35-41` | **None.** |

Evidence for the Dockerfile row: I used two user files, one named `b file.json` and one in a subdirectory, plus an empty `users/` directory.
- The users were added in path order and the file with a space was read whole.
- With an empty `users/`, the realm came out unchanged, which matches the old behavior.

Commands the docs tell people to run, and what runs the same form:
- **The Helm 3.14+ and any-kubectl claims, and the commit title's "run the test stand on year-old tools", have no matching run.** Both CI jobs install Helm `v4.3.1` and whatever kubectl `kind-action` v1.15.1 brings.
  - What the result depends on: how Helm 3 waits for a `helm.sh/hook: test` Job (`suite.yaml:21`) and how it fails on `activeDeadlineSeconds`. Helm 4 waits through kstatus instead.
  - Whether Helm 3 behaves the same is believable but not shown.
- **Docker 23.0, "where BuildKit is the default builder" (needs a run).**
  - On 23.0 and later, BuildKit is the default only when the buildx component is installed.
  - The page's own recipe (`apt-get install docker.io`, docs `:51-53`) can leave buildx out on Debian/Ubuntu. On such a host, `test-stand-files` (`docker build --output`) may fail.
  - I did not run this.

Every hunk of the diff is claimed by a sentence of the commit message.

## Item 3: boundaries, partitions, and the negative control

**Pass-through values.** The stand and the product charts both read `TAG` and `IMAGE_PULL_POLICY`. With the stand moved to `TEST_STAND_HELM_ARGS`, `--set TAG=x` reaches only the product charts. The documented `--set IMAGE_PULL_POLICY=Never` is already set by both stand values files (`test-stand-values.yaml:5`, `parity/test-stand-values.yaml:5`). No finding.

**State left by earlier versions.** Remedy row `:193` covers both targets. Today `users/` holds only a README, so the generated files do not change. No finding.

**Replaced mechanism.** Time to fail and output on each fault:

| Fault | Old (5dcb6be) | New |
| --- | --- | --- |
| `ErrImageNeverPull` | wait for the Job about 0 s, poll about 3 min, `logs -f` fails, then `wait` sits out the 15 min `helm test` timeout. About 15 min. | About 90 × (2 s + one kubectl call) ≈ 3–3.5 min, then the message and `get pods`. Fixed as claimed. |
| Job exists, Pod never created (for example, rejected by the restricted Pod Security Standard from 17b17fc, or a quota) | Same loop, about 33 min | About 33 min. Each `kubectl logs job/X` waits out the default `--pod-running-timeout=20s` looking for a Pod, so 90 × 22 s. |
| `helm test` fails at once (for example, no release) | 2 min (`--timeout=2m`) | About 3+ min, then the wrong message "container did not start", "No resources found", and a `kill: No such process` error |

- **Finding: the Pod-never-created fault.** The new loop does not keep the commit's promise to "fail after about three minutes".
  - It runs past `helm test`'s 15 minutes and past CI's `timeout-minutes: 30`, so CI kills the job before the message prints.
  - When it does print, the output has no Pod and no reason, because every `kubectl logs` error goes to `/dev/null`.
- **Finding: the early-exit fault.** It fails later than the old code and says something false.

**Limits.**
- **Finding.** `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` and `suite.activeDeadlineSeconds` sit inside the CI jobs' `timeout-minutes: 30` (`integration-tests.yaml:120, 168`).
  - That 30 minutes also covers the image builds, the 10-minute harness wait and two 5-minute installs.
  - `test/k8s/README.md:70` tells whoever raises `activeDeadlineSeconds` in `test/k8s/*/test-stand-values.yaml` (the files CI uses) to raise the matching variable. In CI, raising it past about 10–15 minutes does nothing: the job limit fires first. The sentence does not name this third limit.
- **No finding.** The 3-minute loop is shorter than the 15-minute default, so it fires first as intended.

## Item 3a: level, placement, and the environment

There is no single-process level for Make recipes. CI runs every changed target (`kind-e2e`, `kind-parity`), but only on the passing path, on Helm 4.3.1, with a current kubectl. The missing runs are listed under item 2 and in the table below. I did not run the markdownlint gate; the long lines are within MD013's 400-character limit.

## Item 4: names by content, not by position

None. The checked text names things by content ("the `make parity` remedy", "`TEST_STAND_HELM_ARGS`"). No ordinals were added.

## Item 5: the failure report

This is folded into item 3. When the Pod is missing, the stop message prints `get pods`, which shows nothing. The output gives no reason, such as the Job's `FailedCreate` events.

## Item 6: what the writer says it verified

Neither the commit nor the description states any run:
- not the `ErrImageNeverPull` stop,
- not a run on Helm 3.14 or on kubectl older than 1.31,
- not a build of the `chart-files` stage on Alpine.

## Item 7: siblings of the change

- **`run-suite`.** Both callers (`e2e-suite`, `parity-suite`) get the fix. No other `kubectl wait --for=create`, `$(find`, or log-polling loop exists in the repository.
- **`E2E_HELM_ARGS` readers.** `e2e-install`, `parity-install` and `test/k8s/README.md` are all updated. The docs page has no table of overrides to update.
- **Set size.** "both" and "two-entry" are gone. The helm values comments that mention `docker-dev-config.json` (`authz-agent/values.yaml:8`, `authz-policy-admin/values.yaml:8`) name only their own component.
- **Remedy rows.** The `exists and cannot be imported` row now names a step for both paths.
- **Wording points (no fix required).**
  - `docs/local-integration-tests.md:109` and `test/k8s/README.md:59` still describe `e2e-suite` as failing only "if the Job did not complete".
  - The `ErrImageNeverPull` row (`:192`) could quote the new "did not start within 3 minutes" message.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| A Job whose Pod is never created keeps the loop running for about 33 min. Each `kubectl logs job/X` waits the default 20 s for a Pod. The output has no reason. | Substantive | `Makefile:113-118` | Limit the whole loop to 3 min: a deadline it checks, or `--pod-running-timeout=2s`. On stop, also print the Job's events. Run the fault, for example a suite Pod rejected by the restricted Pod Security Standard. |
| When `helm test` exits early, the loop still polls about 3 min, then prints "container did not start" and a `kill` error | Substantive | `Makefile:113` | Stop the loop when `kill -0 $$helm_pid` fails, and let `wait` report helm's own error. |
| No run on Helm 3.14 or on kubectl older than 1.31, though the docs claim them and the commit title promises "year-old tools" | Substantive | `docs/local-integration-tests.md:35-41` | Run `make e2e` on Helm 3.14 and kubectl 1.30 (or add a CI matrix entry), or name only the versions CI runs. |
| "Docker 23.0+, BuildKit default" holds only with buildx installed; the page's `docker.io` recipe may lack it (not run) | Substantive (needs a run) | `docs/local-integration-tests.md:35` | Name the buildx component, or run `make test-stand-files` on a host installed with that recipe. |
| Row says the target "fails after 15 minutes", but `logs -f` holds it until the Job ends | Substantive | `docs/local-integration-tests.md:196` | Describe the symptom as `helm test` printing its timeout while the log keeps streaming. |
| Raising the suite timeout and `activeDeadlineSeconds` in the CI values files does nothing past CI's 30-minute job limit | Substantive | `test/k8s/README.md:69-70`, `.github/workflows/integration-tests.yaml:120,168` | Name the CI `timeout-minutes` as the third limit to raise. |
| "with the test images" suggests all test images; CI builds two of four | Substantive | `README.md:59` | Name `pip-stub` and `parity-suite`. |
| Target tables and the `ErrImageNeverPull` row don't mention the new 3-minute stop or its message | Taste | `docs/local-integration-tests.md:109,192`; `test/k8s/README.md:59` | Mention the stop and quote the message. |

Not checked: I ran no suite, Docker build or cluster. Helm 3 and kubectl `logs` behavior come from the tools' defaults and from reading their source, not from a run. The Dockerfile pipeline ran with macOS tools, not BusyBox. The prose was not reviewed for style.
