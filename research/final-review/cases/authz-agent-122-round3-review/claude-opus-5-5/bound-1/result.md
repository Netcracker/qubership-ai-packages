I reviewed `f3b64e0` against all nine review comments: four substantive findings and two of taste. The worst is that the new "suite never starts" check is limited by attempt count, not by time, so the "three minutes" in the code comment, the error message and the commit message is false for one realistic fault.

No earlier report of this form exists for this change, so there is no table of earlier findings to check against. The drift script printed nothing: the change is a Makefile, a Dockerfile, a Compose file and Markdown, which it does not parse. I loaded the `english-developer-style` and `test-authoring` skills. Where there were no functions or tests, I used the stand-ins for configuration and docs from §2a of the review skill.

## Item 1: comments consistent with the code and with each other

- **`Makefile:104-107`, the comment above `run-suite`:** "the loop polls for up to three minutes". The loop is 90 attempts of `kubectl logs job/<name>` plus `sleep 2`, not three minutes. The echo at `Makefile:115` ("did not start within 3 minutes") and the commit's user-visible line ("fail after about three minutes") make the same claim. When the Job exists but has no Pod, each attempt waits kubectl's `--pod-running-timeout` default of 20s. I confirmed that default with `kubectl logs --help` (v1.33.9) and in `k8s.io/kubectl@v0.35.0/pkg/polymorphichelpers/helpers.go:61-75`, where GetPodList watches for a Pod until that timeout. Filed as finding S1 under item 3.
- **Other comments, all consistent:**
  - The `E2E_HELM_ARGS`/`TEST_STAND_HELM_ARGS` comment (`Makefile:46-49`) matches `make -n` output: `--TS` reaches only `authz-test-stand`, `--EA` only the agent and authz-policy-admin installs.
  - `test/k8s/README.md:66-70` matches the Makefile.
  - The Dockerfile comments still hold.
  - `.github/docs-for-publication-task.md:77` no longer counts the entries.
  - `README.md:59-61` matches the five-entry `.github/docker-dev-config.json`.
  - The chart README's Helm sentence matches inline comment 1.
  - No comment narrates the change.

## Item 2: claimed cases covered

**Claimed cases:**

| Claim | Where it is handled | Run or test |
| --- | --- | --- |
| C1, comment 1: Helm 4.3+ prints nothing; 4.0–4.2 and Helm 3 fail | `helm-templates/authz-test-stand/README.md:62` | none; needs a cluster, so I rely on the reviewer's statement |
| C2, comment 2: list the timeout variables | `test/k8s/README.md:69-70` and `docs/local-integration-tests.md:196` | n/a (docs) |
| C3, comment 3: the remedy covers both targets | `docs/local-integration-tests.md:193` names both causes and both reruns | n/a (docs) |
| C4: the start wait works on any kubectl | `--for=create` removed; the loop uses `kubectl logs job/` only | none |
| C5: a suite that never starts fails after about 3 minutes and prints the Pod | `Makefile:113-118` | **none**; see S1 and S2 |
| C6: `E2E_HELM_ARGS` no longer reaches the stand | `Makefile:93,164` | confirmed with `make -n` |
| C7: user files merged in a fixed order, and a name with a space works | `Dockerfile:43-45` | **no test in the change**; see S4 |
| C8: SVT stack back on Keycloak 26.0 | `docker-compose.yml:3` | line is byte-identical to the one before `8b85515` |
| C9: README and the publication note updated | both files | n/a |
| C10: tool versions documented | `docs/local-integration-tests.md:35,38,41-42` | **none**; see S3 |

**Commands the change tells someone to run:**
- `make e2e`, `make parity`, `make e2e-suite`, `make parity-suite`: CI runs them only on Helm v4.3.1 (`integration-tests.yaml:131,177`), on the runner's own Docker and kind-action's kubectl.
- The documented minimums have no run: Docker 23.0, Helm 3.14, Helm 4.0–4.2, and "any kubectl or kind that supports the cluster". Each is `none`.
- For Helm 3.14, the outcome depends on how `helm test` waits on a Job hook with `before-hook-creation`, and how `upgrade --install --wait` judges readiness.
- For Helm 4.0–4.2, it depends on the kstatus waiter, which only 4.3.1 exercises.
- "The targets use no tool feature newer than these versions" (`docs/local-integration-tests.md:41`) has nothing behind it.
- `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` (row at line 196): `none`. It uses the same `run-suite`, so it is covered by the CI form apart from its value.

**Every hunk is claimed by the commit message.**

## Item 3: boundaries, partitions, and the negative control

**Old and new start wait on two faults** (finding S1):

| Fault | Old mechanism | New mechanism |
| --- | --- | --- |
| ErrImageNeverPull, the one the reviewer names: Pod exists, each `logs` call fails at once | ~15 min (helm timeout) | ~3 min plus 90 fast API calls, then prints the Pod listing |
| Job exists but no Pod is ever created | ~33 min | ~33 min, with a wrong message |

In the second fault the Job controller reports FailedCreate, for example on the restricted Pod Security admission the chart README says the stand runs under, on a ResourceQuota, or on a missing ServiceAccount. Each of the 90 attempts then waits 20s plus a 2s sleep, about 33 minutes. Along the way:
- `helm test` has already failed at about 15 minutes, when `activeDeadlineSeconds: 900` (`values.yaml:99`) fails the Job.
- The loop never checks whether helm has exited, so it keeps polling.
- It then prints "did not start within 3 minutes" and `get pods`, which shows "No resources found"; the cause is in the Job's events.
- In CI, `timeout-minutes: 30` cancels the job first, so no message is printed at all.

The old loop had the same 33 minutes on this fault, so this is not a regression. But the change claims a three-minute bound it does not have.

When `helm test` fails at once (for example, the release is missing), the new target fails after 3 minutes with the same misleading message. The old one failed after about 2 minutes.

**Limits:**
- The new start limit sits inside `E2E_SUITE_TIMEOUT` and `activeDeadlineSeconds`, and they sit inside the CI `timeout-minutes: 30`. CI never raises the suite timeouts.
- At the defaults, the inner limit does not fire first on the no-Pod fault. It fires after helm's 15 minutes and after CI's 30. That is the same finding.

**Values users already pass:**
- `TAG` and `IMAGE_PULL_POLICY` are the names both the stand and the product charts read. They now reach only the product charts, and the stand's values files set `ci` and `Never` themselves.
- Other stand settings passed through `E2E_HELM_ARGS` are now dropped without a warning. The commit's user-visible line announces this.

**State an earlier version left behind:** comment 3's row covers harness objects created with `kubectl apply`. No new persisted state.

**Dockerfile partitions:** see S4.

## Item 3a: level, placement, and the environment

`run-suite` can only be observed against a cluster, so no in-process test is owed. But no CI job reaches the start-failure branch, so the new path has never run anywhere (S2).

I exercised the Dockerfile merge in a scratch build that used the same pinned `alpine:3.22` and `jq:1.8.1` images, with four cases:
- **Files `b file.json`, `c.json` and `sub/a.json`:** merged in byte order (b, c, sub/a), the space in the name kept intact, and a file with no trailing newline parsed fine.
- **An empty directory:** the realm came out unchanged (14 users).
- **A missing directory:** the step still exits 0, but `COPY` always creates the directory, because it holds `README.md`.

The repository has no check that does this (S4).

## Item 4: names by content, not by position

None. I checked the new Makefile lines, the troubleshooting rows, the README sentences and the commit message; "the three" at `test/k8s/README.md:64` was already there.

## Item 5: the failure report

The new message names the Job and lists its Pods, which works for ErrImageNeverPull. On the no-Pod fault, the listing is empty and the cause (FailedCreate) is not printed; this is part of S1.

## Item 6: what the writer says it verified

The commit states no run:
- no ErrImageNeverPull run with its duration and output;
- no run on any of the documented minimum versions;
- no `make test-stand-files` run with more than one user file.

## Item 7: siblings of the change

- **`run-suite` callers:** `e2e-suite` and `parity-suite` (`Makefile:122,171`); both get the fix and both carry S1.
- **`$(find …)` merges elsewhere:** none (`git grep`).
- **Lists of overrides:** only `test/k8s/README.md:66` lists `E2E_HELM_ARGS`, and it names `TEST_STAND_HELM_ARGS`. `docs/local-integration-tests.md` never listed overrides; it now names the timeout variables in a troubleshooting row.
- **Stale counts:** I searched for "both", "two", "three", "five" and "two-entry" near image, component, build and publish. Nothing still counts the components as two.
- **Remedy rows:** the row at line 193 names both targets, both causes and both reruns. The row at line 196 names both targets and both variables. The ErrImageNeverPull row (line 192) does not mention the new "did not start within 3 minutes" message (taste T1).

## Findings

| # | Finding | Label | File:line | Requested change |
| --- | --- | --- | --- | --- |
| S1 | The start wait counts 90 attempts, not 3 minutes. When the Job has no Pod, each `kubectl logs job/` waits the 20s `--pod-running-timeout`: ~33 min, past helm's 15m and CI's 30m. The loop ignores a helm that has already exited, and the message ("within 3 minutes"), the comment and the commit's user-visible line are false for this case. The Pod listing is empty when the cause is on the Job. | Substantive | `Makefile:104-119` | Bound the whole wait at 3 minutes, last attempt included: `--pod-running-timeout=2s` on the polling call, or a `date +%s` deadline. Stop polling once `kill -0 $helm_pid` fails. Print the Job's events (`describe job` or `get events --field-selector involvedObject.name=<job>`) next to the Pods. Then run the no-Pod fault and report its duration and output. |
| S2 | The new failure path has never run. Nothing backs the "about three minutes" and the message on ErrImageNeverPull. | Substantive | `Makefile:113-118`; commit message | A kind run with one suite image left unloaded, reporting the duration and the printed output. |
| S3 | The documented minimums have no run: Docker 23.0, Helm 3.14, Helm 4.0–4.2, any kubectl or kind. CI runs only Helm v4.3.1, and "no tool feature newer than these versions" is unchecked. | Substantive | `docs/local-integration-tests.md:35,38,41-42` | A run of `make e2e` and `make parity` on Helm 3.14 and Docker 23.0, for example a CI matrix entry with Helm v3.14.x. Otherwise, narrow the claims to what CI runs. |
| S4 | The fixed order and the space-in-name handling claimed for the merge have no test. With no user files in the repository, `make test-stand-files` only exercises the empty case. My scratch build showed both behaviors work. | Substantive | `build/authz-agent-transfer/Dockerfile:43-45` | A check, for example in `test/scripts/`, that builds the `chart-files` stage over two or more user files (one named with a space) and compares the output to an expected file. At minimum, state such a run in the description. |
| T1 | The troubleshooting table has no row quoting the new "did not start within 3 minutes" message. | Taste | `docs/local-integration-tests.md:192` | Quote the message in the ErrImageNeverPull row. |
| T2 | "publishes the two services as" can be read as "publishes only the two". I could not confirm what the external dev workflow pushes for the other three components. | Taste | `README.md:60` | Say whether dev builds of the test and transfer images are pushed too. |

I did not run the suites or any target against a cluster, so the Helm 4.0–4.2 behavior in comment 1 rests on the reviewer's statement. I also did not do a style pass over the prose.
