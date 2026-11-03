I added one test script, `test/scripts/test-kind-make-targets.sh`. It passes 12 of 13 checks on HEAD. The one that fails, on a Job that has no Pod, is a defect in the Makefile, not in the test. I changed no production code and committed nothing.

The script tests the `run-suite` wait used by `make e2e-suite` and `make parity-suite`, and the new `TEST_STAND_HELM_ARGS` split.

**Message for the PR author**

---

**Added: `test/scripts/test-kind-make-targets.sh`**

It's a plain bash script shaped like `test-chart-render.sh`. It runs the real make targets with fake `kubectl`, `helm`, `sleep` and `date` first on PATH. No cluster is needed. The fakes share a fake clock, so the 3-minute wait and helm's 15-minute timeout take about 30 s of real time and come out the same on every run. The fake kubectl acts like a version before 1.31, so it rejects `wait --for=create`.

| Check | HEAD | Base (HEAD~1) |
| --- | --- | --- |
| `e2e-suite` streams the log of a container that starts 150 s in. 150 s is inside the 3-minute window, so a shorter wait would also fail this. | pass | **fail**: `wait --for=create` is rejected, `logs -f` runs at 0 s, and no log is streamed |
| `e2e-suite` and `parity-suite`, container stuck on ErrImageNeverPull: they print the message and the Pod listing, and stop `helm test` within 202 s (180 s plus one 20 s attempt and one 2 s sleep) | pass, 180 s | **fail** |
| `e2e-suite`, Job with no Pod (for example, admission rejects the Pod) | **fail**: 1980 s | **fail** |
| `E2E_SUITE_TIMEOUT=2m`, which is shorter than the start wait: the target still fails, and helm's timeout error is shown | pass | fail |
| `e2e` and `parity` flows: the test-stand install gets only `TEST_STAND_HELM_ARGS`, and the agent and authz-policy-admin installs get only `E2E_HELM_ARGS`. Each flow runs once with both variables set, and `test-stand-files` is skipped with `make -o`. | pass | **fail**: `--set TAG=pr-123` reached the stand |

**Old and new behaviour on each fault**

- **Container stuck on ErrImageNeverPull:**
  - Old: 15 minutes. It printed kubectl's `waiting to start: ErrImageNeverPull` and helm's timeout error.
  - New: 3 minutes. It prints `The runtime-suite container did not start within 3 minutes:` and the Pod listing.
- **Job with no Pod** (the slowest single attempt):
  - kubectl source (`pkg/polymorphichelpers/helpers.go`, `GetPodList`) shows that each `kubectl logs job/<name>` waits `--pod-running-timeout`, 20 s by default, for a Pod to appear.
  - So 90 attempts take 90 × 22 s = 1980 s, about 33 minutes. `helm test` has already timed out at 15 minutes by then. This is also longer than the 30-minute limit on the CI jobs.
  - Old: about 33 minutes, and it printed helm's timeout.
  - New: about 33 minutes, then the message and `No resources found`.
  - So the change is not slower here, but the promised "about three minutes" does not hold for this fault.
- **Job never created** (`helm test` fails before creating it):
  - Old: gave up after 2 minutes, the `wait --for=create` timeout.
  - New: gives up after 3 minutes, and the message says the container did not start.
  - I worked this one out from the code and did not run it.

**Proposed, not done**

1. **Fix the no-Pod case in `run-suite`.** For example, pass `--pod-running-timeout=2s` to the polling `kubectl logs`, or check a deadline from `date +%s`. The fake `date` already reads the fake clock, so either fix will turn the failing check green. Ending the loop once `helm test` has exited (`kill -0 $helm_pid`) would also fix the Job-never-created case. On the no-Pod fault it would end the target at 15 minutes instead of about 3. Printing the Job's events would explain an empty Pod listing.
2. **Run the script in CI.** I suggest a step in the `chart` job of `integration-tests.yaml`, and an entry in `test/readme.md`'s minimum gate. I didn't add it because CI would stay red until item 1 is fixed.
3. **Test the chart-files change.** The `sort -z` / NUL-separated step needs a Docker test: build the `chart-files` stage twice with the user files created in different orders, include a file name with a space, and compare `parity-realm.json`. I wrote no test, because I couldn't run Docker here.
4. **SVT on Keycloak 26.0.** Going back from 26.3.5 needs an SVT run named in the PR. The image also lost its digest pin.

---

Separately, for you rather than the PR: the skill suggests a "stack line" in the repo's instructions file, saying how the plain-bash `fail`/`pass` scripts report results. They keep going after a failed check, report every one, and name each by its message. I can add that line to `AGENTS.md` if you want; I haven't touched it.
