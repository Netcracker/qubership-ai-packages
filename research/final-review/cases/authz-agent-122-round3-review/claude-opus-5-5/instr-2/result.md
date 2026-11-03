# Final review: `5dcb6be..f3b64e0`, one commit

There is no previous report of this form, so there is no table of earlier findings. Most of the change is not code: a Makefile recipe, a Dockerfile `RUN`, Markdown pages, and a Compose file. The items therefore use the §2a analogues for a configuration or script and for a docs page. `comment-drift.py 5dcb6be HEAD` ran and printed nothing, because it parses none of these file types. Skills loaded: `test-authoring` (§3, §4) and `english-developer-style`.

## Item 1: comments consistent with the code and with each other
*Analogue used: each statement a changed file makes about another file, a tool, or the repository.*

- **`docs/local-integration-tests.md:35` says Docker must be 23.0 or later, and the page's own install recipe can install an older one.** The recipe at `:50-53` is `apt-get install -y docker.io`. On Debian 12 that package is Docker 20.10.24, below the new minimum. On a Docker 23 or later without the `docker-buildx` package, `docker build` falls back to the legacy builder. "Where BuildKit is the default builder" can be read either as a condition the reader must meet or as a note on what 23.0 changed, and the recipe does not ensure either. This is filed as finding 3.
- **`Makefile:104-107` says that when `kubectl logs` keeps failing, the container did not start.** That holds for `ErrImageNeverPull`, but not when `helm test` has already exited (finding 1).
- **`Makefile:52-53`, `test/k8s/README.md:69-70`, and `docs/local-integration-tests.md:196` say how to give a suite more time.** All three say to raise the timeout variable "together with `suite.activeDeadlineSeconds`". None names the `-test.timeout 600s` in `suite.args`, which ends both suites at 10 minutes first (finding 2).
- Checked and correct:
  - `README.md:59-61` against `.github/docker-dev-config.json` (five components) and `.qubership/docker.cfg`.
  - `.github/docs-for-publication-task.md:77`.
  - `helm-templates/authz-test-stand/README.md:62`, which matches review comment 1.
- No sentence narrates the change ("now", "no longer").

## Item 2: claimed cases covered

| Claim (source) | Where it is handled | Run that covers it |
| --- | --- | --- |
| Helm 4.3+ prints nothing; 4.0–4.2 and Helm 3 fail (comment 1) | chart `README.md:62` | none: no cluster here; the CI jobs pin Helm v4.3.1 |
| Suite timeout variables listed (comment 2) | `test/k8s/README.md:69-70`, `docs/…:196` | n/a (documentation) |
| Remedy row covers parity (comment 3) | `docs/…:192` names `make e2e` and `make parity` | none from the inherited state; `e2e-down` deletes the whole cluster, so the remedy is sound by construction |
| Works on kubectl older than 1.31 (general comment, commit message) | `Makefile:115` polls `kubectl logs job/<name>` | none on an old kubectl; CI uses kind-action's kubectl |
| `ErrImageNeverPull` fails in about 3 minutes and prints the Pod (general comment, commit message) | `Makefile:115-120` | none in the change. My reading: about 3 min plus 90 kubectl calls |
| Files merged in sorted order, and a name with a space survives (general comment) | `Dockerfile:43-45` | none in the change. I ran it on BusyBox 1.37 with jq 1.8.1, with 0 files and with 3 files including `users/b file.json` and `users/sub/c.json`: merged in sorted order, exit 0. The repository has no user files, so CI covers only the empty case |
| `--set TAG=x` no longer reaches the stand (general comment, commit message) | `Makefile:93,164` take `TEST_STAND_HELM_ARGS` | `make -n` with `E2E_HELM_ARGS='--set TAG=x'`: only the agent and admin installs get it |
| SVT back on Keycloak 26.0 (general comment) | `docker-compose.yml:3` | identical to the merge-base `b7064c7`, so no SVT run is owed |
| README and publication doc stop counting two components (general comment) | `README.md:59`, `docs-for-publication-task.md:77` | n/a |
| Docker 23.0 and Helm 3.14 or later are enough (commit message, `docs/…:35,38,41-42`) | `docs/…:33-42` | **none.** CI runs Helm v4.3.1 and the runner's current Docker only (finding 3) |

Commands the change tells someone to run:

| Command | Outcome it promises | What runs it |
| --- | --- | --- |
| `make e2e-down`, then `make e2e` or `make parity` (`docs:192`) | clears the "cannot be imported" error | CI runs the same targets, but only on a fresh cluster |
| `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` (`docs:196`) | a longer suite completes | **none**; at default values the run still ends at 600 s (finding 2) |
| `make e2e-suite` / `make parity-suite`, failure path (commit message "User-visible") | fails in about 3 minutes with the Pod listing | **none**; CI runs the success path only |

**Hunks with no sentence in the commit message:** `README.md:59-61`, `.github/docs-for-publication-task.md:77`, and the `make parity` remedy row at `docs/local-integration-tests.md:192`. Each answers a review comment, but the commit message, which is what stays in the history, does not mention them (finding 4).

## Item 3: boundaries, partitions, and the negative control

- **Dockerfile user files.** I covered the empty, several-file, nested, and space-in-name cases in my run above. The writer states no run of any of them.
- **Values users already pass.** On the merge-base `b7064c7`, `E2E_HELM_ARGS` reached only the agent and authz-policy-admin installs (`b7064c7:Makefile:83-84,141-142`). So this change restores that scope instead of taking a value away from the stand. `TEST_STAND_HELM_ARGS` is the stand's own setting. `make -n` confirms both: `TAG=x` goes only to the product charts, and `suite.activeDeadlineSeconds=1200` reaches both stand installs. None.
- **Replaced mechanism: suite container never starts (`ErrImageNeverPull`).**
  - Base `5dcb6be`: about 15 min (it waits out `helm test`).
  - Main: 3 min, printing `timed out waiting for the condition`.
  - New: 90 × (2 s + one `kubectl logs`). It prints the message and `get pods -o wide`, which shows the `ErrImageNeverPull` status. Acceptable.
- **Replaced mechanism: `helm test` exits at once** (release not installed, for example `make e2e-suite` before `make e2e-harness`, or a wrong context).
  - Base `5dcb6be`: about 2 min on kubectl 1.31 or later, when the `--for=create` wait times out; immediate on older kubectl.
  - New: **measured 185 s** with stub `kubectl` and `helm` (scratchpad `fake/`). It prints `Error: release: not found`, then `The runtime-suite container did not start within 3 minutes:`, `No resources found`, and `kill: (…) - No such process`.
  - It fails later and gives the wrong cause (finding 1).
- **Longest single attempt.** `kubectl logs` and `get pods` have no `--request-timeout`. Counted as never returning, neither the old loop nor the new one is bounded. This is not a regression; the overrun is noted as finding 5.
- **Limits on the suite run:**
  - `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT`: `Makefile:54-55`, 15m.
  - Go `-test.timeout 600s`: `test/k8s/test-stand-values.yaml:55-56`, and the chart's `values.yaml:95-96` for parity (rendered with `helm template`).
  - `activeDeadlineSeconds: 900`: `values.yaml:99`. It is set at harness time, not suite time.
  - CI `timeout-minutes: 30`: `integration-tests.yaml:120,168`.

  At the defaults, the inner `-test.timeout` fires first. Raising either variable past 600 s, or `activeDeadlineSeconds` with it, changes nothing, because `-test.timeout` is fixed in `suite.args`. For the same reason, the `docs:196` symptom ("fails after 15 minutes while the Job still runs") cannot occur at the defaults. The 3-minute start loop bounds only the start, so it does not count as a limit on the run (finding 2).

## Item 3a: level, placement, and the environment

The recipe and the Dockerfile stage can be tested offline (a stub run, `docker build --target chart-files`). No CI job exercises the failure path or a non-empty `users/`, and the change adds no such check. The placement matches the sibling targets. The offline gate is `make lint` (shellcheck on `*.sh`), which does not cover Makefile recipes, so I did not run it.

## Item 4: names by content, not by position

None. I checked the new message text, the docs rows, and the variable names. All refer to things by content ("the two services", "earlier releases, Helm 3 included").

## Item 5: the failure report
*Analogue used: what the reader sees on failure.*

On the never-starting container, the Pod listing shows the status, which is good. On a `helm test` that fails at once, the output names a wrong cause and adds a `kill` error (finding 1). `kubectl logs … >/dev/null 2>&1` hides the last error. That is acceptable only because `get pods` follows it.

## Item 6: what the writer says it verified

Nothing is stated:
- No run of either failure fault.
- No run of the Dockerfile stage with user files.
- No run on Helm 3.14, Docker 23.0, or a kubectl older than 1.31.

The SVT revert needs no run, because it matches main.

## Item 7: siblings of the change

- `run-suite` has two callers (`e2e-suite`, `parity-suite`), and both get the fix. `git grep 'wait --for'` finds no other site.
- `E2E_HELM_ARGS` has four consumers, and both stand installs moved to `TEST_STAND_HELM_ARGS`. The subset recipe at `docs:138-143` calls `helm upgrade --reuse-values` directly and is unaffected.
- The set of overrides:
  - `test/k8s/README.md:66-70` lists the new variable.
  - `docs/local-integration-tests.md` lists no overrides at all, so there is nothing there to extend.
  - Searches for "both" and "two-entry" find no remaining count of components.
- Remedy rows:
  - `docs:192` names both targets and both reruns.
  - `docs:191` (`ErrImageNeverPull` → `make e2e-images`) serves both paths, because they share the images.
  - `docs:196` names both variables but misses the inner limit (finding 2).

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | When `helm test` exits at once, the loop still polls for 3 minutes (185 s measured). It then reports "container did not start" plus a `kill: No such process` error, where the base failed in at most 2 min. | substantive | `Makefile:115-118`, comment `:104-107` | In the loop, stop when `kill -0 $$helm_pid` fails. Then `wait $$helm_pid` and exit with its status, without the start message. Rerun the stub fault and give the duration and the output. |
| 2 | Raising `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT` (and `activeDeadlineSeconds`) has no effect past the `-test.timeout 600s` fixed in `suite.args`. `activeDeadlineSeconds` also takes effect only at harness time. The `docs:196` symptom cannot occur at the defaults, and its `5h30m` example does nothing. | substantive | `docs/local-integration-tests.md:196`, `Makefile:52-53`, `test/k8s/README.md:69-70` | Name `-test.timeout` in `suite.args` and the harness rerun (for example `TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=…'` with the matching args). Better: derive the inner limits from one setting. Fix the symptom's duration. |
| 3 | The minimums Docker 23.0 and Helm 3.14, and "any version" for kubectl and kind, have no run; CI runs Helm v4.3.1 only. The page's own `apt-get install docker.io` installs Docker 20.10 on Debian 12, and without `docker-buildx` it falls back to the legacy builder. | substantive | `docs/local-integration-tests.md:35,38,41-42,50-53` | Run `make e2e` on Helm 3.14 and on Docker 23.0 with BuildKit, or state the versions CI runs. Make the install recipe produce the stated minimum with buildx. |
| 4 | Three hunks have no sentence in the commit message. | substantive | `README.md:59-61`, `.github/docs-for-publication-task.md:77`, `docs/local-integration-tests.md:192` | Add one sentence that claims them. |
| 5 | The 3-minute bound is 90 × (2 s + an unbounded `kubectl` call), so a slow API server stretches it with no limit. | taste | `Makefile:115` | Use a wall-clock deadline, or add `--request-timeout` to the polled calls. |
| 6 | The pipeline runs without `pipefail`, so a failing `find` or `cat` hands jq partial input and the build passes. | taste | `build/authz-agent-transfer/Dockerfile:43-45` | Add `set -o pipefail` (BusyBox `sh` supports it). |

Not checked: I did not run either suite on a real cluster, did not run Helm 3.x or Docker 23.0, did not build the transfer image (I checked only its `RUN` pipeline in `alpine:latest` with BusyBox 1.37), and did not read the prose for style.
