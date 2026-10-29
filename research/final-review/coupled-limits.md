# Two limits on one quantity

Evidence for the rule in `final-review` item *Boundaries, partitions, and the negative control* (and its analogue for a
change with no code), `test-authoring` §4 bullet *A limit set elsewhere on the same work* with its §11 question,
and the paragraph under *Reliability, operability, and observability* in `adversarial-code-review`.

## The class

Two or more limits bound the same quantity (a duration, a number of attempts, a size, a count) at different layers: a
wrapper and what it wraps, a caller and the process it starts, a job and the step inside it. The limits are set in
different places, and nothing ties one to the other. Two failures follow:

- **A documented setting is capped by a limit set where the documented configuration does not reach.** Raising the
  setting past the hidden limit has no effect, and the user who raised it sees the hidden limit's failure.
- **The inner limit does not fire before the outer one.** The outer limit kills the work first, so the inner limit's
  failure path (its message, its log upload, its cleanup) never runs, and the report the user gets is the outer one's
  generic one.

Both are boundary defects: the input is the setting, and the value just past the other limit is a boundary nobody
tested. The rule asks the reviewer to list the limits on the path, name where each is set, and check that boundary.

## Instances

| Where | Inner limit | Outer limit | Which failure |
| --- | --- | --- | --- |
| [Netcracker/qubership-authz-agent#122][a122] ([comment][a122c]) | `suite.activeDeadlineSeconds: 900` in chart values (and `-test.timeout 600s` in `suite.args`) | `helm test --timeout 15m`, fixed in the Makefile | Capped setting; at the defaults both fire at 900 s |
| [vmware-tanzu/helm-charts#408][v408], found by [velero-io/velero#10437][v10437] | controller-runtime's `defaultGracefulShutdownPeriod = 30 * time.Second`, which velero v1.9.2 does not override (`pkg/cmd/server/server.go:315`; controller-runtime v0.10.2 `pkg/manager/internal.go:54`) | the chart's new `terminationGracePeriodSeconds: 3600` | Capped setting: the value the PR adds has no effect past 30 s |
| [camunda/camunda#44166][c44166], fixed by [camunda/camunda#63383][c63383] | the poll loop, `80 x 30s`, with a `Timed out waiting` branch | the job's `timeout-minutes: 20` (later 35) | Inner does not fire first; its timeout branch is unreachable |
| [kubernetes/test-infra#37871][k37871] | kubetest2 `--timeout=4h0m0s`, whose expiry uploads node logs | prow `decoration_config.timeout: 180m` | Inner does not fire first; hung runs end with no node logs |
| [hashicorp/terraform-provider-aws#39040][t39040] | the provider's 10-minute waiter for `InService` | the user's `maximum_execution_timeout_in_seconds` | Capped setting |
| [apache/airflow#62218][af62218], fixed by [apache/airflow#62869][af62869] | the broker `visibility_timeout` of 86400 s that `default_celery.py` applies | the user's task execution time | Capped setting, undocumented |
| TINKERPOP-2814, apache/tinkerpop `8906c4e147` | Netty's default SSL handshake timeout | the user's `connectionSetupTimeoutMillis` | Capped setting |
| HTTPCLIENT-2099, apache/httpcomponents-client `5bdcb242f0` | the connect timeout applied to the TLS handshake | the configured socket timeout | Capped setting |
| [helm/helm#9805][h9805] | client-go's per-request `?timeout=32s` | the documented `--timeout` | Capped setting |

[a122]: https://github.com/Netcracker/qubership-authz-agent/pull/122
[a122c]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4358379579
[v408]: https://github.com/vmware-tanzu/helm-charts/pull/408
[v10437]: https://github.com/velero-io/velero/issues/10437
[c44166]: https://github.com/camunda/camunda/pull/44166
[c63383]: https://github.com/camunda/camunda/pull/63383
[k37871]: https://github.com/kubernetes/test-infra/pull/37871
[t39040]: https://github.com/hashicorp/terraform-provider-aws/issues/39040
[af62218]: https://github.com/apache/airflow/issues/62218
[af62869]: https://github.com/apache/airflow/pull/62869
[h9805]: https://github.com/helm/helm/issues/9805

The velero and camunda rows became review cases, `velero-charts-408-review` and `camunda-44166-review`, beside
`authz-agent-122-review`. The two cover the two failures and are not derived from PR #122: in velero the hidden limit
is in the application the chart starts and is not visible in the repository; in camunda both limits are in one file
of a GitHub Actions workflow.

## Why the rule names no tool

Every instance has a different pair of tools, and the reviewer has to find the pair from the path the change sits on.
The rule names the layers (what starts or wraps the code, what the code starts, the environment), the places a limit
is set (a documented setting, a value fixed in a script or a wrapper, a default), and the boundary to check.

## What the cases show

Per-run grades are in each case's README. Three texts of the rule ran; the matrix of this note, all three texts and
the controls of the two new cases, cost 24.31 USD.

- **`authz-agent-122-review`, check 3.** Without the rule, 0 of 4 runs. With the committed text, Opus 2 of 2, naming
  the cap and asking to derive the helm timeout from the Job's deadline, and Haiku 1 pass and 1 weak pass. The drafts
  scored the same for Opus and as well or worse for Haiku. Check 1, inherited state, held in all twelve runs.
- **`velero-charts-408-review`.** Opus finds the premise without the rule, through the claimed-cases item; with it,
  Opus names velero's own shutdown handling as the inner limit. Haiku found it in neither the control nor either draft,
  and with the drafts paired the grace period with `resticTimeout`, a limit on one operation, in all four runs. With
  the committed text, which says how to tell a limit on the same work and what to ask for a limit outside the
  repository, both Haiku runs name velero's shutdown handling and neither pairs `resticTimeout`.
- **`camunda-44166-review`.** Every arm finds it in every run, through the comment the job timeout contradicts.
- **`pgjdbc-1557-review` and `pgjdbc-2572-review`**, two code changes in a JDBC driver, with the defect confirmed by a
  later fix. Opus finds them without the rule (4 of 4 on the replaced limit, 2 of 2 on the equal pair, 2 of 2 on the
  swallowed timeout) and with it does no better: 4 of 4, 1 of 2, 1 of 2. Haiku gains one finding per run on #1557 and
  none on #2572, where it reports other pairs instead. These runs cost 5.20 USD.

The rule reliably moves Opus on a cap the diff shows only through two files of configuration, and does not cost the
other findings there. On a code change, where both limits sit in code the reviewer reads anyway, Opus finds the defect
without the rule, and the two misses with it (a pair judged harmless, a run that reported only missing tests) are within
the noise of two runs per cell. On PR #122 Haiku, with the committed text, finds the cap or the default-order defect in
both runs, though it states the cap itself in one; on the pgjdbc wrapper it finds nothing in either arm. A limit the
repository does not contain, as in velero, is found as a request for evidence, never as the number; the reviewer would
need the application's source, which `final-review` does not fetch.

The rule was then shortened to cut repeats, and Haiku alone re-ran the two cases that tell the arms apart. A cut that
dropped the step of raising each documented setting past the other limits failed check 3 of `authz-agent-122-review`
in both runs: Haiku listed the chain and judged only the defaults. With the step back, both runs pass it, and velero
passes in all four runs with no false pair. These runs cost 2.21 USD; Opus did not run the shortened text.

A review of the pull request pointed out that "counted from the same start" excluded an enclosing limit that starts
earlier, such as a CI job around the test run it starts. Dropping the condition and comparing expiry times, with the
time before the inner work starts taken from the outer budget, brought the `resticTimeout` pair back in both Haiku
velero runs: Haiku argued that the restic clock had started earlier. The committed text counts a limit whose work
contains this work or lies inside it as a whole, and excludes one on a single operation inside it or on work that only
overlaps it. With it, Haiku passed check 3 of `authz-agent-122-review` in two runs of three and check 1 in three,
velero in both runs with no false pair, and camunda in both, counting the setup before the poll against the job's
budget in one. Both rounds cost 3.67 USD (`start-<n>` and `enclosing-<n>` under each case).

Gaps: no trial runs the test-authoring text while writing tests or the adversarial-code-review text; both were checked
by reading only. The target models of `agent-packages/AGENTS.md` include Sonnet, which did not run.
