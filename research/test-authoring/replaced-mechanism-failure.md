# The failure of a replaced mechanism

Evidence for the rule in `SKILL.md` §3 that a change which replaces a mechanism owes a run of two faults, the one the
old mechanism met most often and, for a loop, the one on which one attempt waits longest, with how long each takes to
fail and what each prints.

## The incident

In [Netcracker/qubership-authz-agent#122][a122], the kind suite targets moved from a Job applied with `kubectl apply`
to the suite Job of a Helm test-stand chart, run by `helm test`. The old target waited for the suite Pod with
`kubectl wait --for=condition=Ready pod -l job-name=runtime-suite --timeout=3m`. The new one started
`helm test --timeout 15m` in the background and polled `kubectl logs job/<name>` before streaming the log.

The author ran the new targets, and so did two automated review passes: `final-review` in a fresh subagent and a
cross-review by Codex and a Claude subagent. Every run had the suite image loaded, so every run took the success path.
A human reviewer read the failure path instead ([general comment][g]): with the suite image missing from the kind node
(`ErrImageNeverPull`, for example after a missed `kind load`), the old target failed after 3 minutes, and the new one
waited out the 15-minute `helm test` timeout, half of the CI job's `timeout-minutes: 30`.

The author's fix stopped the new target after "three minutes" when the log could not be read. The next round found
that the three minutes were 90 attempts of `kubectl logs job/<name>` with a 2-second sleep between them, not a deadline
([comment][c-loop]). While the Job exists and has no Pod, for example when a ResourceQuota or an admission webhook
refuses it, each attempt waits up to kubectl's default `--pod-running-timeout` of 20 seconds, so the loop takes about
90 × 22 s, roughly 33 minutes.

## What the rule asks, and why

Both defects are on the path no green run reaches, and both are found by comparing the old mechanism with the new one on
a fault: the time to fail and the output. They need two different faults. On the missing image, a Pod exists, `kubectl
logs` fails at once, and the fixed loop ends after about 3.5 minutes; the 33 minutes appear only when the Job has no
Pod, the fault on which one attempt waits longest. The loop defect also shows how a loop's time to fail is counted. For
a loop bounded by a count of attempts, it is the count times the sum of the longest attempt and the sleep. Here the
longest attempt is a default timeout that no flag in the Makefile shows, and counting only the sleep gives the 3 minutes
the author wrote. A loop that checks a deadline before each attempt has the same trap: the last attempt can start just
before the deadline, and the sleep after it runs in full, so the loop takes up to the deadline plus the longest attempt
and the longest sleep.

The paragraph says nothing about the test of a fault. §4, §5, and §8 already ask for a controlled clock and for the
behavior a constant decides rather than the constant, and both control runs of the case below wrote a test of the
give-up path with a fake `sleep` without the paragraph.

One incident, one kind of mechanism (a wait in a build target). The rule names the others it covers (a client, a
deployment step) without a measured incident for them in this folder. The matching question in `final-review` was
measured on review cases of PR #122, which [Netcracker/qubership-ai-packages#186][p186] commits under
`research/final-review/cases/`. The test-authoring case `cases/authz-agent-122-suite-loop-from-scratch` runs the
paragraph and, as a control, the skill without it on the commit of PR #122 that gave the 90-attempt loop a path that
gives up.

[a122]: https://github.com/Netcracker/qubership-authz-agent/pull/122
[g]: https://github.com/Netcracker/qubership-authz-agent/pull/122#issuecomment-6362443580
[c-loop]: https://github.com/Netcracker/qubership-authz-agent/pull/122#discussion_r4359760444
[p186]: https://github.com/Netcracker/qubership-ai-packages/pull/186
